from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "paperskill/index.html"

def home(request):
    return HttpResponse("<h1>Добро пожаловать в PaperSkill!</h1><p>Это главная страница Django-проекта.</p>")

class ContactView(TemplateView):
    template_name = "paperskill/contacts.html"

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        return render(request, 'paperskill/answer.html', {'name': name, 'email': email})
