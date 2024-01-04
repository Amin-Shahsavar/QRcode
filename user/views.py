from django.contrib.auth import get_user_model

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.serializers import TokenBlacklistSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView as BaseTokenObtainPairView

from user.serializers import (
    UserSerializer,
    VerifyEmailSerializer,
    TokenObtainPairSerializer,
    ChangeFirstNameLastNameSerializer,
    ChangePasswordSerializer,
    ResetPasswordCheckEmailSerializer,
    ResetPasswordSerializer,
)
from user.utils import EmailHandler


User = get_user_model()


class RegistartionView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"Ceated": "User created successfully.",
                 "Verify Email": "Please check your email to verify your Email Address."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class VerifyEmailView(generics.CreateAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            if user.is_verified_email:
                return Response({"User": "User is already verified!"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            else:
                user.is_verified_email = True
                user.save()
                return Response({"Message": "Email verified successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class TokenObtainPairView(BaseTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = TokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            if not serializer.user.is_verified_email:
                email_message = EmailHandler(request=request, user=serializer.user)
                email_message.send_email('verify_email')
                return Response(
                    {"Email": "Email not verified verification link sended to your email!"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class ProfileView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        serializer = UserSerializer(instance=user , context={'request': request})
        return Response(serializer.data)

    def delete(self, request):
        user = self.request.user
        user.delete()
        return Response({"Message": "User deleted."}, status=status.HTTP_204_NO_CONTENT)


class ChangeFirstNameLastNameView(generics.UpdateAPIView):
    serializer_class = ChangeFirstNameLastNameSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = ChangeFirstNameLastNameSerializer(
            instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"Message": "First name and Last name changed."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response({"Message": "Password successfuly changed."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class LogoutView(generics.GenericAPIView):
    serializer_class = TokenBlacklistSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"Logout": "logged out"}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({"Deatil": "invalid token"}, status=status.HTTP_401_UNAUTHORIZED)


class ResetPasswordCheckEmailView(generics.GenericAPIView):
    serializer_class = ResetPasswordCheckEmailSerializer

    def post(self, request):
        serializer = ResetPasswordCheckEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"Message": "Given email dosen't exist!"}, status=status.HTTP_401_UNAUTHORIZED)
        email_message = EmailHandler(request=request, user=user)
        email_message.send_email('reset_password')
        return Response({"Message": "We send a email to reset your password"}, status=status.HTTP_200_OK)


class RestPasswordView(generics.UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    queryset = User.objects.all()

    def update(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({"Message": "Password successfuly reset"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
