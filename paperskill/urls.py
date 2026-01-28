from django.urls import path
from rest_framework.routers import DefaultRouter

from paperskill import views
from paperskill.apps import PaperskillConfig

app_name = PaperskillConfig.name

router = DefaultRouter()
router.register("courses", views.CourseViewSet, basename="courses")
router.register("lessons", views.LessonViewSet, basename="lessons")

urlpatterns = [
    path("courses/", views.CourseListView.as_view(), name="courses_list"),
    path("courses/create/", views.CourseCreateView.as_view(), name="course_create"),
    path("courses/<int:pk>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("courses/<int:pk>/update/", views.CourseUpdateView.as_view(), name="course_update"),
    path("courses/<int:pk>/delete/", views.CourseDeleteView.as_view(), name="course_delete"),
    #
    # path('courses/<int:pk>/subscribe/', views.CourseSubscriptionAPIView.as_view(), name='subscribe_course'),
    # path('courses/<int:pk>/unsubscribe/', views.CourseUnsubscribeAPIView.as_view(), name='unsubscribe_course'),
    #
    path("courses/<int:pk>/lessons/<int:lesson_id>/", views.LessonDetailView.as_view(), name="lesson_detail"),
    path("courses/<int:pk>/lessons/<int:lesson_id>/update/", views.LessonUpdateView.as_view(), name="lesson_update"),
    path("courses/<int:pk>/lessons/<int:lesson_id>/delete/", views.LessonDeleteView.as_view(), name="lesson_delete"),
    path("courses/<int:pk>/lessons/create/", views.LessonCreateView.as_view(), name="lesson_create"),
    # path('courses/<int:pk>/lessons/', views.LessonListView.as_view(), name='lessons_list'),
] + router.urls
