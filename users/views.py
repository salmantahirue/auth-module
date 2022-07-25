from django.contrib.auth.models import User
from rest_framework import generics, permissions, authentication
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.hashers import check_password

from .serializers import UserSerializer, RegisterSerializer


class RegisterAPI(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    allowed_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        email = request.data['email']
        try:
            check_is_active = User.objects.get(email=email, username=request.data['username'])
            if not check_is_active.is_active:
                check_is_active.is_active = True
                check_is_active.save()
                data = {'username': check_is_active.username,
                        'email': check_is_active.email}
                return Response(data, status=status.HTTP_200_OK)
            else:
                data = {'username': check_is_active.username,
                        'email': check_is_active.email,
                        'message': 'user already exist'}
                return Response(data, status=status.HTTP_200_OK)
        except:
            serializer = RegisterSerializer(data=request.data)
            data = {}
            if serializer.is_valid():
                account = serializer.save()
                data['email'] = account.email
                data['username'] = account.username
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                data = serializer.errors
                return Response(data, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(ObtainAuthToken):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        get_user = self.queryset.filter(username=request.data['username']).first()
        if get_user:
            if get_user.is_active is True:
                if check_password(request.data['password'], get_user.password):
                    serializer.is_valid(raise_exception=True)
                    # user = serializer.validated_data['user']
                    token, created = Token.objects.get_or_create(user=get_user)
                    return Response({
                        'token': token.key,
                        'user_id': get_user.pk,
                        'email': get_user.email
                    })
                else:
                    return Response({
                        'message': 'User password not matched'
                    })
            else:
                return Response({
                    "error": "Inactive user not able to login",
                })
        else:
            return Response({
                "error": "User does not exist",
            })


class UpdateIsActiveAPIView(generics.UpdateAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        try:
            user = request.user.id
            instance = self.queryset.get(id=user)
            if instance.is_active is True:
                instance.is_active = False
                instance.save()
                return Response({"message": "user successfully deleted"},
                                status=status.HTTP_200_OK)
            else:
                return Response({"message": "user already deleted"},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)