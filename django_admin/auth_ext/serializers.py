from rest_framework import serializers, exceptions, validators
from auth_ext.models import Permission, Role, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', )


class SimplePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'code', 'name', )


class PermConfigSerializer(serializers.ModelSerializer):
    """ 配置用的权限序列化， 通常用于内嵌其他序列化 """
    disabled = serializers.BooleanField(read_only=True)

    class Meta:
        model = Permission
        fields = ('id', 'code', 'name', 'disabled', )


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        exclude = ('status', )


class SimpleRoleSerializer(serializers.ModelSerializer):
    editable = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ('id', 'code', 'name', 'editable')
        extra_kwargs = {
            'name': {'validators': [validators.UniqueValidator(Role.objects.all(), message='角色名已存在')]},
        }

    def get_editable(self, obj):
        return not obj.is_system_role


class RoleSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    permissions = PermConfigSerializer(many=True, read_only=True)
    user_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    permission_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    editable = serializers.SerializerMethodField()

    class Meta:
        model = Role
        exclude = ('is_deleted', )
        extra_kwargs = {
            'name': {'validators': [validators.UniqueValidator(Role.objects.all(), message='角色名已存在')]},
        }

    def get_editable(self, obj):
        return not obj.is_system_role

