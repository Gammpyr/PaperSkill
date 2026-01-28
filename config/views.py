from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from paperskill.models import Course
from users.models import User


class IndexView(TemplateView):
    template_name = "paperskill/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses_count'] = Course.objects.count()
        context['students_count'] = User.objects.count()
        context['courses'] = Course.objects.annotate(lesson_count=Count('lessons')).order_by('-created_at')[:3]

        return context

def home(request):
    return HttpResponse("<h1>Добро пожаловать в PaperSkill!</h1><p>Это главная страница Django-проекта.</p>")

class ContactView(TemplateView):
    template_name = "paperskill/contacts.html"

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        return render(request, 'paperskill/answer.html', {'name': name, 'email': email})
