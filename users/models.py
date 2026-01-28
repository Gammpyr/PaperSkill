from django.contrib.auth.models import AbstractUser, UserManager, BaseUserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User с phone_number в качестве USERNAME_FIELD.
    """
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Требуется номер телефона')

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)  # <-- Хеширование пароля
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True, blank=True, null=True, verbose_name='Имя пользователя', )
    email = models.EmailField(unique=True, verbose_name='email')
    phone_number = PhoneNumberField(unique=True, verbose_name='Номер телефона')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name='Страна')
    courses = models.ManyToManyField('paperskill.Course', blank=True, related_name='users')
    bought_courses = models.ManyToManyField('paperskill.Course', blank=True, related_name='buyers')

    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({str(self.phone_number)})"
