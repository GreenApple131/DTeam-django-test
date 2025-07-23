from rest_framework import serializers
from main.models import CV


class CVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = "__all__"

    def validate_email(self, value):
        """Validate email format"""
        if "@" not in value:
            raise serializers.ValidationError("Invalid email format")
        return value

    def validate_phone(self, value):
        """Validate phone number format"""
        if not value.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise serializers.ValidationError("Invalid phone number format")
        return value
