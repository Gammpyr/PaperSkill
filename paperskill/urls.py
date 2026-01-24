from django.urls import path
from rest_framework.routers import DefaultRouter

from paperskill import views
from paperskill.apps import PaperskillConfig

app_name = PaperskillConfig.name

router = DefaultRouter()
router.register("courses", views.CourseViewSet, basename="courses")

urlpatterns = [
    
              ] + router.urls
