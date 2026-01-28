from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users import views
from users.apps import UsersConfig
from users.forms import CustomAuthenticationForm

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"payments", views.PaymentViewSet, basename="payments")

urlpatterns = [
    path("users/create/", views.UserCreateAPIView.as_view(), name="users-create"),
    path("users/", views.UserListAPIView.as_view(), name="users-list"),
    path("users/update/<int:pk>/", views.UserUpdateAPIView.as_view(), name="users-update"),
    path("accounts/profile/", views.ProfileView.as_view(), name="profile"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "login/",
        LoginView.as_view(template_name="users/login.html", authentication_form=CustomAuthenticationForm),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="paperskill:courses_list"), name="logout"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("payment/success/<int:payment_id>/", views.PaymentSuccessView.as_view(), name="payment_success"),
    path("payment/cancel/<int:payment_id>/", views.PaymentCancelView.as_view(), name="payment_cancel"),
] + router.urls
