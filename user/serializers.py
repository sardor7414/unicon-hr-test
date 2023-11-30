from rest_framework import serializers
from user.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    reply_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'phone', 'password', 'reply_password')

        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        attrs = super().validate(attrs)
        phone = attrs['phone']
        user = self.Meta.model.objects.filter(phone=phone).first()
        if user:
            raise serializers.ValidationError("User already exists")
        password = attrs['password']
        reply_password = attrs.pop('reply_password')
        if password != reply_password:
            raise serializers.ValidationError("Passwords must match!")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

