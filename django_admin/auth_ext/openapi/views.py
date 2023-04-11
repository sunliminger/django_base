from rest_framework import generics, exceptions, response, serializers
from auth_ext.models import ExternalUser, Token


class RefreshToken(generics.GenericAPIView):
    """
    post:
    通过refresh_token刷新token

    """
    class DefaultSerializer(serializers.Serializer):
        refresh_token = serializers.CharField(max_length=100, help_text='Refresh Token')

        def validate(self, attrs):
            refresh_token = attrs.get('refresh_token')
            try:
                user = ExternalUser.objects.get(refresh_token=refresh_token)
            except ExternalUser.DoesNotExist:
                msg = 'Unable to log in with provided credentials.'
                raise exceptions.ValidationError(msg, code='authorization')
            attrs['user'] = user
            return attrs

    permission_classes = []
    queryset = ExternalUser.objects.all()
    serializer_class = DefaultSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        external_user = serializer.validated_data.get('user')
        token = Token.op_refresh(external_user)

        result = {
            'token': token.key,
            'created': token.created.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'expire': external_user.expire,
        }
        return response.Response(data=result)
