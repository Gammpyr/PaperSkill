from rest_framework import serializers

from users.models import Payment, User


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "password",
            "avatar",
            "country",
            "is_active",
            "date_joined",
            "courses",
            "bought_courses",
        ]
        read_only_fields = ["id", "date_joined", "is_active", "courses", "bought_courses"]

    def create(self, validated_data):
        user = User.objects.create_user(
            phone_number=validated_data["phone_number"],
            password=validated_data["password"],
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            country=validated_data.get("country"),
            avatar=validated_data.get("avatar", None),
        )
        return user


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = [
            "user",
            "session_id",
            "payment_url",
            "product_id",
            "price_id",
        ]

    def validate_payment_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма платежа должна быть больше 0.")
        return value

    # def validate(self, data):
    #     paid_course = data.get("paid_course")
    #     paid_lesson = data.get("paid_lesson")
    #
    #     if not paid_course and not paid_lesson:
    #         raise serializers.ValidationError("Укажите, за что вы хотите оплатить. За курс или урок.")
    #     if paid_course and paid_lesson:
    #         raise serializers.ValidationError("Можно оплатить либо за курс, либо за урок.")
    #     return data
