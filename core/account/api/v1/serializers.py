from django.core import exceptions
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

User = get_user_model()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True) # Current password field
    new_password = serializers.CharField(required=True) # New password field
    new_password1 = serializers.CharField(required=True) # Confirm new password field

    def validate(self, attrs):
        # Check if new passwords match
        if attrs.get("new_password") != attrs.get("new_password1"):
            raise serializers.ValidationError(
                {"detail": _("passwords does not match")})
        try:
            # Validate new password strength
            validate_password(password=attrs.get("new_password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"new password": list(e.messages)})
        return super().validate(attrs)
