from django.http import HttpResponse
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "paperskill/index.html"

def home(request):
    return HttpResponse("<h1>Добро пожаловать в PaperSkill!</h1><p>Это главная страница Django-проекта.</p>")