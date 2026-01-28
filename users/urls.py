from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users import views

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"payments", views.PaymentViewSet, basename="payments")

urlpatterns = [
    path('users/create/', views.UserCreateAPIView.as_view(), name='users-create'),
    path('users/', views.UserListAPIView.as_view(), name='users-list'),
    path('users/update/<int:pk>/', views.UserUpdateAPIView.as_view(), name='users-update'),

    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
] + router.urls