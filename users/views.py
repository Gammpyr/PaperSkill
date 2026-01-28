from django.conf import settings
from django.contrib.auth import login
from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter

from users.forms import CustomUserCreationForm
from users.models import User, Payment
from users.serializers import CustomUserSerializer, PaymentSerializer
from users.services import create_stripe_product, create_stripe_price, create_stripe_session


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()


class UserListAPIView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["paid_course", "payment_method"]
    ordering_fields = ["payment_date"]

    def perform_create(self, serializer):
        try:
            payment = serializer.save(user=self.request.user)

            product_name = payment.paid_course.name

            product = create_stripe_product(product_name)
            price = create_stripe_price(product, payment.payment_amount)
            session = create_stripe_session(price)

            payment.session_id = session.get("id")
            payment.payment_url = session.get("url")
            payment.product_id = product.get("id")
            payment.price_id = price.get("id")
            payment.save()
        except Exception as e:
            raise ValidationError(f"Ошибка при создании сессии оплаты: {str(e)}")


class ProfileView(TemplateView):
    template_name = 'users/profile.html'

class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('paperskill:course_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user)
        return super().form_valid(form)

    def send_welcome_email(self, user):
        if user.email:
            subject = 'Добро пожаловать в PaperSkill!'
            message = f'{user.display_name.title()}, спасибо, что зарегистрировались на нашем сайте!'
            recipient_list = [user.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)