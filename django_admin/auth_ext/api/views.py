from rest_framework import generics, serializers, response, permissions, exceptions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.views import JSONWebTokenAPIView, JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings as jwt_settings

from auth_ext.models import ExternalUser, Permission, Role
from auth_ext.authentication import set_token, delete_token
from auth_ext.serializers import PermissionSerializer, UserSerializer, RoleSerializer, SimplePermissionSerializer, \
    SimpleRoleSerializer, PermConfigSerializer
from auth_ext.menu import get_menu_for_user, MenuItem
from rest_framework.response import Response as DetailResponse
from rest_framework import generics as generics_ext, serializers as serializers_ext
from auth_ext.models import User


class UserOwn(generics.GenericAPIView):
    """
    get:
    获取当前用户信息

    """
    class DefaultSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('id', 'username', 'last_login', )

    serializer_class = DefaultSerializer

    def get(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            raise exceptions.AuthenticationFailed()
        serializer = self.get_serializer(instance=request.user)
        return response.Response(data=serializer.data)


class UserOwnMenu(generics.GenericAPIView):
    """
    get:
    获取当前用户的菜单

    """
    class MenuSerializer(serializers_ext.Serializer):
        children = serializers.SerializerMethodField()
        visible = serializers.ListField(child=serializers.CharField(max_length=200))

        class Meta:
            model = MenuItem
            fields = ('path', 'name', 'component', 'children', 'visible')

        def get_children(self, obj):
            serializer = self.__class__(many=True, instance=obj.children)
            return serializer.data

    serializer_class = MenuSerializer

    def get(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            raise exceptions.AuthenticationFailed()
        menu_tree = get_menu_for_user(request.user)
        serializer = self.get_serializer(instance=menu_tree, many=True)
        return response.Response(data=serializer.data)


class UserHasPerm(generics.GenericAPIView):
    """
    post:
    验证当前用户是否拥有某个权限

    """
    class DefaultSerializer(serializers.Serializer):
        perm = serializers.CharField(max_length=200)
    serializer_class = DefaultSerializer

    def post(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            raise exceptions.AuthenticationFailed()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        has_perm = request.user.has_perm(serializer.validated_data.get('perm'))
        return response.Response(data={'has_perm': has_perm})


class JSONWebTokenObtain(JSONWebTokenAPIView):
    """
    get:
    通过cookie换取token

    post:
    账号密码登录

    """
    authentication_classes = [SessionAuthentication, ]
    serializer_class = JSONWebTokenSerializer

    def get_authenticators(self):
        if self.request and self.request.method == 'POST':
            # POST方法登录不做认证
            return []
        return super().get_authenticators()

    def get(self, request, *args, **kwargs):
        """ 通过cookie换取token """
        user = request.user
        if not user or not user.is_authenticated:
            raise exceptions.AuthenticationFailed()
        payload = jwt_settings.JWT_PAYLOAD_HANDLER(user)
        token = jwt_settings.JWT_ENCODE_HANDLER(payload)
        set_token(user, token)
        resp = response.Response(data={'token': token})
        return resp

    def post(self, request, *args, **kwargs):
        """ 账号密码登录 """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            set_token(user, token)
            resp = response.Response(data={'token': token})
            return resp
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    """ 登出 """
    def get(self, request):
        delete_token(request.user)
        return DetailResponse('登出成功')

    def handle_exception(self, exc):
        """ 登出时不需要处理401 403 认证、权限异常，直接返回200 """
        if isinstance(exc, (exceptions.AuthenticationFailed,
                            exceptions.NotAuthenticated,
                            exceptions.PermissionDenied)):
            # 用户token在后端已经失效时，调用登出接口不返回认证&权限异常
            return DetailResponse('登出成功，无效的token')
        return super().handle_exception(exc)


# =========================================== 外部用户配置 ================================================
class ExternalUserPermissionMixin(object):
    permission_classes = [permissions.IsAdminUser]


class ExternalUserList(ExternalUserPermissionMixin, generics.ListCreateAPIView):
    """
    get:
    返回外部用户列表

    post:
    新增外部用户信息

    """
    class DefaultSerializer(serializers.ModelSerializer):
        class Meta:
            model = ExternalUser
            fields = ('id', 'username', 'expire', 'refresh_token')

    queryset = ExternalUser.objects.all()
    serializer_class = DefaultSerializer


class ExternalUserDetail(ExternalUserPermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    返回外部用户详情

    put:
    修改外部用户信息

    patch:
    部分修改外部用户信息

    delete:
    删除外部用户信息

    """
    queryset = ExternalUser.objects.all()
    serializer_class = ExternalUserList.DefaultSerializer


class ExternalUserRefresh(ExternalUserPermissionMixin, generics.GenericAPIView):
    """
    post:
    刷新refresh_token信息

    """
    queryset = ExternalUser.objects.all()
    serializer_class = serializers.Serializer

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.update_refresh_token()
        obj.save()
        return response.Response(data={'refresh_token': obj.refresh_token})


# ============================================= 权限配置 ==================================================
class PermissionListView(generics.ListAPIView):
    """
    get:
    查看权限列表

    """
    class PrettySerializer(serializers.Serializer):
        """ 三层（app-model-perm）结构的权限序列化类 """
        class ModelPermissionSetSerializer(serializers.Serializer):
            code = serializers.CharField(max_length=255, help_text='model')
            name = serializers.CharField(max_length=255, help_text='模型名')
            children = SimplePermissionSerializer(many=True, read_only=True)

        code = serializers.CharField(max_length=255, help_text='app')
        name = serializers.CharField(max_length=255, help_text='app名')
        children = ModelPermissionSetSerializer(many=True, read_only=True)

    queryset = Permission.objects.all()
    serializer_class = SimplePermissionSerializer
    filter_fields = ('app_label', 'model_name', )
    search_fields = ('code', 'name', )

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer_class = self.get_serializer_class()

        pretty = self.request.query_params.get('pretty', False)
        if pretty in ('True', 'TRUE', 'true', True):
            queryset = queryset.model.pretty(queryset)
            serializer_class = self.PrettySerializer
            page = None     # 树形结构不分页
        else:
            page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializer_class(queryset, many=True)
        return response.Response(serializer.data)


class PermissionDetailView(generics.RetrieveAPIView):
    """
    get:
    查看权限详情

    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


# ============================================= 用户配置 ==================================================
class UserListView(generics.ListAPIView):
    """
    get:
    返回用户列表

    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    search_fields = ('username', )


class UserDetailView(generics_ext.OpRetrieveUpdateAPIView):
    """
    get:
    返回用户详情

    put:
    修改用户信息

    patch:
    部分修改用户信息

    """
    class DefaultSerializer(serializers.ModelSerializer):
        permissions = PermConfigSerializer(source='get_all_permission_objs', many=True, read_only=True)
        permission_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
        roles = SimpleRoleSerializer(source='get_all_role_objs', many=True, read_only=True)
        role_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)

        class Meta:
            model = User
            fields = ('id', 'username', 'permissions', 'permission_ids', 'roles', 'role_ids')
            extra_kwargs = {
                'username': {'read_only': True},
            }

    queryset = User.objects.filter(is_active=True)
    serializer_class = DefaultSerializer


# ============================================== 角色配置 ==================================================
class RoleListView(generics_ext.OpListCreateAPIView):
    """
    get:
    查看角色列表

    post:
    新增角色

    """
    class PrettySerializer(serializers.Serializer):
        kind = serializers.IntegerField(read_only=True)
        name = serializers.CharField(source='kind_name', max_length=100, read_only=True)
        roles = SimpleRoleSerializer(many=True, read_only=True)

    queryset = Role.objects.all()
    serializer_class = SimpleRoleSerializer
    search_fields = ('code', 'name', )

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer_class = self.get_serializer_class()

        pretty = self.request.query_params.get('pretty', False)
        if pretty in ('True', 'TRUE', 'true', True):
            queryset = queryset.model.pretty(queryset)
            serializer_class = self.PrettySerializer
            page = None     # 树形结构不分页
        else:
            page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializer_class(queryset, many=True)
        return response.Response(serializer.data)


class RoleDetailView(generics_ext.OpRetrieveUpdateDestroyAPIView):
    """
    get:
    查看角色详情

    put:
    修改角色

    patch:
    部分修改角色

    delete:
    删除角色

    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
