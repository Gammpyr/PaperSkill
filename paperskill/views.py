from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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


class CourseSubscriptionAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):
        user = self.request.user
        course_id = self.kwargs['id']
        course = get_object_or_404(Course, id=course_id)

        if not user.courses.filter(id=course_id).exists():
            user.courses.add(course)
            return Response({'message': 'Вы подписались на курс!'}, status=200)
        else:
            return Response({'message': 'Курс уже начат!'}, status=200)






class CourseListView(ListView):
    model = Course
    template_name = 'paperskill/course/list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.prefetch_related('lessons').annotate(
            lesson_count=Count('lessons')
        )

