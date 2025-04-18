from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
    )
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email',  'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            # nickname=validated_data['nickname'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    






