from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from django.core import exceptions
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from polls.users.models import User
from polls.pollsapp.models import Question, Choice


class UserSerializer(serializers.ModelSerializer):
    """Serializer to handle users."""
    questions = serializers.PrimaryKeyRelatedField(many=True, queryset=Question.objects.all())
    choices = serializers.PrimaryKeyRelatedField(many=True, queryset=Choice.objects.all())

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            'questions',
            'choices',
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
        }

    def validate_password(self, value):
        # Validates the password and catch the exception
        try:
            password_validation.validate_password(password=value)
        except exceptions.ValidationError as exception:
            raise serializers.ValidationError(exception.messages)
        else:
            value = make_password(value)
            return value


class VerifySerializer(serializers.Serializer):
    """Serializer to verify the user's email."""

    verification_code = serializers.CharField()

    def validate_verification_code(self, value):
        if not User.objects.filter(verification_code=value).exists():
            raise serializers.ValidationError(_("Verification code not found"))
        return value

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RequestRestoreCodeSerializer(serializers.Serializer):
    """Serializer to request a new password for the user."""

    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("Email not found"))
        return value

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RestorePasswordSerializer(serializers.Serializer):
    """Serializer to restore a password for the user."""

    password = serializers.CharField()
    repeat_password = serializers.CharField()
    restore_password_code = serializers.CharField()

    def validate_restore_password_code(self, value):
        if not User.objects.filter(restore_password_code=value).exists():
            raise serializers.ValidationError(_("Restore code doesn't exists"))
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        repeat_password = attrs.get("repeat_password")
        if password and repeat_password and password != repeat_password:
            raise serializers.ValidationError(_("Passwords are not the same"))
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass