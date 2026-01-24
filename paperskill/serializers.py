from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ['created_at', 'owner', 'course']


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.IntegerField(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ['created_at', 'owner']
