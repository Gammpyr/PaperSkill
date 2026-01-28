from django.db import models


class Course(models.Model):
    CATEGORIES = (("IT", "Программирование"), ("DESIGN", "Дизайн"), ("BUSINESS", "Бизнес"), ("MARKETING", "Маркетинг"))

    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(blank=True, null=True, upload_to="images/", verbose_name="Превью")
    video_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на видео")
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="owned_courses",
        verbose_name="Владелец",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_paid = models.BooleanField(default=False, verbose_name="Платный курс")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Цена")
    category = models.CharField(max_length=20, choices=CATEGORIES, verbose_name="Категория")

    def __str__(self):
        return f"{self.name} [Владелец: {self.owner}]"

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["id"]


class Lesson(models.Model):
    name = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(blank=True, null=True, upload_to="images/", verbose_name="Превью")
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="lessons",
        verbose_name="Владелец",
    )
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядковый номер")

    def __str__(self):
        return f"{self.name} [Курс: {self.course.name}]"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["id"]


# class CourseSubscription(models.Model):
#     user = models.ForeignKey(
#         "users.User",
#         on_delete=models.CASCADE,
#         related_name="subscriptions",
#         verbose_name="Пользователь",
#     )
#     course = models.ForeignKey(
#         "Course",
#         on_delete=models.CASCADE,
#         related_name="subscriptions",
#         verbose_name="Курс",
#     )
#
#     class Meta:
#         verbose_name = "Подписка"
#         verbose_name_plural = "Подписки"
#         unique_together = ["user", "course"]
#
#     def __str__(self):
#         return f"{self.user} - {self.course}"
