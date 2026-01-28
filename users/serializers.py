from rest_framework import serializers

from users.models import User


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone_number', 'password',
            'avatar', 'country', 'is_active', 'date_joined', 'courses', 'bought_courses'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active', 'courses', 'bought_courses']

    def create(self, validated_data):
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            country=validated_data.get('country'),
            avatar=validated_data.get('avatar', None),
        )
        return user
