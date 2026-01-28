import re

from rest_framework import serializers

from .models import Course, Lesson
from .validators import UrlValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ['created_at', 'owner']


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.IntegerField(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    def validate(self, attrs):
        video_url = attrs.get("video_url")
        if video_url and not re.search(r"(youtube\.com|youtu\.be|rutube\.ru)", video_url):
            raise serializers.ValidationError({"video_url": "Разрешены только ссылки на YouTube или RuTube"})
        return attrs

    class Meta:
        model = Course
        fields = "__all__"
        validators = [UrlValidator(field="video_url")]
        read_only_fields = ['created_at', 'owner']
