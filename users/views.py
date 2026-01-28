import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter

from users.forms import CustomUserCreationForm
from users.models import Payment, User
from users.serializers import CustomUserSerializer, PaymentSerializer
from users.services import create_stripe_price, create_stripe_product, create_stripe_session


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

            request = self.request
            success_url = request.build_absolute_uri(
                reverse("users:payment_success", kwargs={"payment_id": payment.id})
            )
            cancel_url = request.build_absolute_uri(reverse("users:payment_cancel", kwargs={"payment_id": payment.id}))

            product = create_stripe_product(payment.paid_course.name)
            price = create_stripe_price(product, payment.payment_amount)
            session = create_stripe_session(price, success_url, cancel_url)

            payment.session_id = session.get("id")
            payment.payment_url = session.get("url")
            payment.product_id = product.get("id")
            payment.price_id = price.get("id")
            payment.save()
        except Exception as e:
            raise ValidationError(f"Ошибка при создании сессии оплаты: {str(e)}")


class ProfileView(TemplateView):
    template_name = "users/profile.html"


class RegisterView(FormView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("paperskill:course_list")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user)
        return super().form_valid(form)

    def send_welcome_email(self, user):
        if user.email:
            subject = "Добро пожаловать в PaperSkill!"
            message = f"{user.display_name.title()}, спасибо, что зарегистрировались на нашем сайте!"
            recipient_list = [user.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "users/payment_success.html"

    def get(self, request, *args, **kwargs):
        payment_id = self.kwargs.get("payment_id")
        session_id = request.GET.get("session_id")

        try:
            payment = get_object_or_404(Payment, id=payment_id, user=request.user)

            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
                payment.payment_status = "succeeded"
                payment.save()

                if payment.paid_course and payment.paid_course not in request.user.bought_courses.all():
                    request.user.bought_courses.add(payment.paid_course)
                    request.user.save()

                messages.success(request, "Платеж успешно завершен! Курс добавлен в вашу библиотеку.")
            else:
                messages.warning(request, "Платеж не подтвержден. Пожалуйста, проверьте статус позже.")

        except Exception as e:
            messages.error(request, f"Ошибка при проверке платежа: {str(e)}")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_id = self.kwargs.get("payment_id")

        try:
            payment = Payment.objects.get(id=payment_id, user=self.request.user)
            context["payment"] = payment
            context["course"] = payment.paid_course
        except Payment.DoesNotExist:
            pass

        return context


class PaymentCancelView(LoginRequiredMixin, TemplateView):
    """Страница отмены оплаты"""

    template_name = "users/payment_cancel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_id = self.kwargs.get("payment_id")

        try:
            payment = get_object_or_404(Payment, id=payment_id, user=self.request.user)
            context["payment"] = payment
            context["course"] = payment.paid_course

        except Payment.DoesNotExist:
            messages.error(self.request, "Платеж не найден")

        return context


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """Обработчик вебхуков Stripe"""

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except ValueError:
            return JsonResponse({"error": "Invalid payload"}, status=400)
        except stripe.error.SignatureVerificationError:
            return JsonResponse({"error": "Invalid signature"}, status=400)

        # Обработка события
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            # Находим платеж по сессии
            session_id = session.get("id")
            try:
                from .models import Payment

                payment = Payment.objects.get(session_id=session_id)

                # Обновляем статус
                if session.get("payment_status") == "paid":
                    payment.payment_status = "succeeded"
                    payment.save()

                    # Добавляем курс в купленные
                    if payment.paid_course and payment.paid_course not in payment.user.bought_courses.all():
                        payment.user.bought_courses.add(payment.paid_course)
                        payment.user.save()

            except Payment.DoesNotExist:
                pass

        return JsonResponse({"status": "success"})
