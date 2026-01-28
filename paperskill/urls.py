from django.urls import path
from rest_framework.routers import DefaultRouter

from paperskill import views
from paperskill.apps import PaperskillConfig

app_name = PaperskillConfig.name

router = DefaultRouter()
router.register("courses", views.CourseViewSet, basename="courses")
router.register("lessons", views.LessonViewSet, basename="lessons")

urlpatterns = [
                    path('courses/<int:id>/start/', views.CourseSubscriptionAPIView.as_view(), name='start_course')

              ] + router.urls
