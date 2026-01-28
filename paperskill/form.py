from django import forms

from .models import Course, Lesson


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "description", "image", "video_url", "category", "is_paid", "price"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите название курса"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Опишите ваш курс..."}
            ),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "video_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://example.com/video"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "is_paid": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Введите цену в рублях", "step": "0.01", "min": "0"}
            ),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["name", "description", "image"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Название урока", "required": True}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 5, "placeholder": "Подробное описание урока", "required": True}
            ),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Порядковый номер урока"}),
        }
