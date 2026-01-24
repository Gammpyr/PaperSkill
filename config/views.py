from django.http import HttpResponse


def home(request):
    return HttpResponse("<h1>Добро пожаловать в PaperSkill!</h1><p>Это главная страница Django-проекта.</p>")