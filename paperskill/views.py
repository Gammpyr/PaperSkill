from django.db.models import Count
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from paperskill.models import Course, Lesson
from paperskill.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    # pagination_class = None
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.prefetch_related('lessons').annotate(
            lesson_count=Count('lessons')
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    # pagination_class = None
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)