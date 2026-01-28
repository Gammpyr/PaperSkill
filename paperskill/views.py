from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from paperskill.form import CourseForm, LessonForm
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
    permission_classes = [IsAuthenticated]

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

class CourseDetailView(DetailView):
    model = Course
    template_name = 'paperskill/course/detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        has_access = False
        if user.is_authenticated:
            has_access = (
                    not course.is_paid or
                    course in user.bought_courses.all() or
                    course.owner == user or
                    user.is_superuser
            )

        context['has_access_to_lessons'] = has_access
        context['is_owner'] = user.is_authenticated and (course.owner == user or user.is_superuser)

        return context

class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'paperskill/course/form.html'
    # fields = ['name', 'category', 'description', 'image', 'video_url', 'is_paid', 'price', ]
    success_url = reverse_lazy('paperskill:course_list')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.owner = self.request.user
            return super().form_valid(form)
        else:
            return super().form_invalid(form)

    def get_success_url(self):
        return reverse('paperskill:course_detail', kwargs={'pk': self.object.pk})


class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'paperskill/course/form.html'
    success_url = reverse_lazy('paperskill:courses_list')

    def get_success_url(self):
        return reverse('paperskill:course_detail', kwargs={'pk': self.object.pk})

class CourseDeleteView(LoginRequiredMixin, DeleteView):
    model = Course
    template_name = 'paperskill/course/confirm_delete.html'
    success_url = reverse_lazy('paperskill:courses_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_superuser or obj.owner != self.request.user:
            raise PermissionDenied("У вас нет прав на удаление этого продукта")
        return obj


class LessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'paperskill/lesson/form.html'

    def get_course(self):
        """Получить курс из URL параметра"""
        return Course.objects.get(pk=self.kwargs['pk'])

    def dispatch(self, request, *args, **kwargs):
        """Проверка прав доступа: только владелец курса или суперпользователь"""
        course = self.get_course()

        if not request.user.is_superuser and course.owner != request.user:
            raise PermissionDenied("У вас нет прав для добавления уроков в этот курс")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_course()
        context['course'] = course
        context['title'] = f'Создание урока для курса "{course.name}"'
        return context

    def form_valid(self, form):
        """Привязать урок к курсу и установить владельца"""
        lesson = form.save(commit=False)
        lesson.course = self.get_course()
        lesson.owner = self.request.user

        lesson.save()

        messages.success(self.request, f'Урок "{lesson.name}" успешно создан!')
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправление на детальную страницу курса после создания"""
        return reverse('paperskill:course_detail', kwargs={'pk': self.get_course().pk})


class LessonDetailView(DetailView):
    """Детальный просмотр урока"""
    model = Lesson
    template_name = 'paperskill/lesson/detail.html'
    context_object_name = 'lesson'

    def get_object(self, queryset=None):
        lesson_id = self.kwargs.get('lesson_id')
        return Lesson.objects.get(pk=lesson_id)

    def dispatch(self, request, *args, **kwargs):
        lesson = self.get_object()
        course = lesson.course
        user = request.user

        has_access = False
        if user.is_authenticated:
            has_access = (
                    not course.is_paid or
                    course in user.bought_courses.all() or
                    course.owner == user or
                    lesson.owner == user or
                    user.is_superuser
            )

        if not has_access:
            raise PermissionDenied("У вас нет доступа к этому уроку. Купите курс для получения полного доступа.")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        context['course'] = lesson.course

        user = self.request.user
        context['can_edit'] = (
                user.is_authenticated and
                (user.is_superuser or lesson.owner == user or lesson.course.owner == user)
        )

        return context


class LessonUpdateView(LoginRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'paperskill/lesson/form.html'
    context_object_name = 'lesson'

    def get_object(self, queryset=None):
        """Получить урок по course.pk и lesson_id из URL"""
        course_pk = self.kwargs['pk']
        lesson_id = self.kwargs['lesson_id']
        return get_object_or_404(Lesson, pk=lesson_id, course__pk=course_pk)

    def get_context_data(self, **kwargs):
        """Добавить курс и заголовок в контекст"""
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        context['title'] = 'Редактирование урока'
        return context

    def get_success_url(self):
        """Перенаправление после успешного обновления"""
        return reverse('paperskill:lesson_detail', kwargs={
            'pk': self.object.course.pk,
            'lesson_id': self.object.pk
        })


class LessonDeleteView(LoginRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'paperskill/lesson/confirm_delete.html'
    context_object_name = 'lesson'

    def get_object(self, queryset=None):
        """Получить урок по course.pk и lesson_id из URL"""
        course_pk = self.kwargs['pk']
        lesson_id = self.kwargs['lesson_id']
        return get_object_or_404(Lesson, pk=lesson_id, course__pk=course_pk)

    def get_context_data(self, **kwargs):
        """Добавить курс в контекст"""
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context

    def get_success_url(self):
        """Перенаправление после успешного удаления"""
        return reverse('paperskill:course_detail', kwargs={'pk': self.object.course.pk})