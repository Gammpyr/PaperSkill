from django.contrib import admin

from paperskill.models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "created_at")
    list_filter = ("owner",)
    search_fields = ("name", "description", "owner")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "course", "owner", "created_at")
    list_filter = ("owner", "course")
    search_fields = ("name", "description", "owner", "course")
