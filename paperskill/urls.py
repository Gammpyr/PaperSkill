from django.urls import path
from rest_framework.routers import DefaultRouter

from paperskill import views
from paperskill.apps import PaperskillConfig

app_name = PaperskillConfig.name

router = DefaultRouter()
router.register("courses", views.CourseViewSet, basename="courses")
router.register("lessons", views.LessonViewSet, basename="lessons")

urlpatterns = [
        path('courses/', views.CourseListView.as_view(), name='courses_list'),
        path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
        path('courses/<int:id>/', views.CourseDetailView.as_view(), name='course_detail'),
        # path('courses/<int:id>/update/', views.CourseUpdateView.as_view(), name='course_update'),
        # path('courses/<int:id>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
        #
        # path('courses/<int:id>/subscribe/', views.CourseSubscriptionAPIView.as_view(), name='subscribe_course'),
        # path('courses/<int:id>/unsubscribe/', views.CourseUnsubscribeAPIView.as_view(), name='unsubscribe_course'),
        #
        # path('courses/<int:id>/lessons/<int:lesson_id>/', views.LessonDetailView.as_view(), name='lesson_detail'),
        # path('courses/<int:id>/lessons/<int:lesson_id>/update/', views.LessonUpdateView.as_view(), name='lesson_update'),
        # path('courses/<int:id>/lessons/<int:lesson_id>/delete/', views.LessonDeleteView.as_view(), name='lesson_delete'),
        # path('courses/<int:id>/lessons/create/', views.LessonCreateView.as_view(), name='lesson_create'),
        # path('courses/<int:id>/lessons/', views.LessonListView.as_view(), name='lessons_list'),


              ] + router.urls
