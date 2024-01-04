from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainSerializer as BaseTokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from user.utils import EmailHandler


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_conf = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_conf', 'first_name', 'last_name']

    def validate(self, attrs):
        emails = list(map(lambda email: email.replace('.', ''), User.objects.values_list('email', flat=True)))
        email = str(attrs['email']).replace('.', '')
        username = attrs['username']

        if not username.isalnum():
            raise serializers.ValidationError({"username": "The username should only contain alphanumeric characters."})
        
        if len(username) < 4:
            raise serializers.ValidationError({"username": "The username should be at last 4 characters long."})

        if email in emails:
            raise serializers.ValidationError({"email": "user with this Email Address already exists."})

        if attrs['password'] != attrs['password_conf']:
            raise serializers.ValidationError({"passowrd": "Passwords Do Not Match."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_conf', None)
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        email_message = EmailHandler(request=self.context['request'], user=user)
        email_message.send_email(email_type='verify_email')
        return user


class VerifyEmailSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Invalid user"})

        token = attrs['token']

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Invalid token"})

        return {"user": user, **attrs}


class TokenObtainSerializer(BaseTokenObtainSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    token_class = None

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']

        try:
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)
        except:
            raise serializers.ValidationError({"username": "No active account found with the given credentials"})

        self.user = authenticate(request=self.context.get('request'), username=user.username, password=password)

        if self.user is None:
            raise serializers.ValidationError({"password": "No active account found with the given credentials"})

        return {}

    @classmethod
    def get_token(cls, user):
        return cls.token_class.for_user(user)


class TokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class ChangeFirstNameLastNameSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True, style={"input_type": "password"})
    new_password = serializers.CharField(required=True, style={"input_type": "password"})
    new_password_conf = serializers.CharField(required=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'new_password_conf']

    def validate(self, attrs):
        user = self.context['request'].user
        old_password = attrs['old_password']
        new_password = attrs['new_password']
        new_password_conf = attrs['new_password_conf']

        if not user.check_password(old_password):
            raise serializers.ValidationError({"Old password": "Old password incorrect!"})

        if new_password != new_password_conf:
            raise serializers.ValidationError({"New passwords": "New passwords not match!"})

        if old_password == new_password:
            raise serializers.ValidationError({"New and Old Password": "You cant set your current password."})

        user.set_password(new_password)
        user.save()

        return attrs


class ResetPasswordCheckEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']


class ResetPasswordSerializer(serializers.ModelSerializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True, style={"input_type": "password"})
    new_password_conf = serializers.CharField(required=True, write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ['uid', 'token', 'new_password', 'new_password_conf']

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Invalid user"})

        token = attrs['token']

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Invalid token"})

        new_password = attrs['new_password']
        new_password_conf = attrs['new_password_conf']

        if new_password != new_password_conf:
            raise serializers.ValidationError(
                {"password": "New passwords not match!"})

        return {"user": user, **attrs}
