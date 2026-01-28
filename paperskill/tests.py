from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from paperskill.models import Course, Lesson
from paperskill.views import LessonDetailView
from django.core.exceptions import PermissionDenied
from django.urls import reverse


User = get_user_model()


class CourseModelTest(TestCase):
    """Тесты для модели курса"""

    def setUp(self):
        """Создаем пользователя перед каждым тестом"""
        self.user = User.objects.create_user(
            phone_number='+79876543210',
            password='testpassword123',
            username='testuser'
        )

    def test_create_course(self):
        """Тест создания курса"""
        course = Course.objects.create(
            name='Python для начинающих',
            description='Курс по основам программирования на Python',
            owner=self.user,
            is_paid=False,
            price=0.00
        )

        self.assertEqual(course.name, 'Python для начинающих')
        self.assertEqual(course.owner, self.user)
        self.assertEqual(course.is_paid, False)
        self.assertEqual(course.price, 0.00)

    def test_create_paid_course(self):
        """Тест создания платного курса"""
        course = Course.objects.create(
            name='Django продвинутый курс',
            description='Продвинутый курс по веб-разработке',
            owner=self.user,
            is_paid=True,
            price=5000.00
        )

        self.assertEqual(course.is_paid, True)
        self.assertEqual(course.price, 5000.00)

    def test_course_string_representation(self):
        """Тест строкового представления курса"""
        course = Course.objects.create(
            name='Тестовый курс',
            owner=self.user
        )

        self.assertEqual(str(course), 'Тестовый курс [Владелец: +79876543210]')

    def test_course_default_values(self):
        """Тест значений по умолчанию"""
        course = Course.objects.create(
            name='Курс без описания',
            owner=self.user
        )

        self.assertEqual(course.is_paid, False)
        self.assertEqual(course.price, None)
        self.assertEqual(course.description, '')


class LessonDetailViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Создаем пользователей
        self.owner = User.objects.create_user(
            phone_number='+79991112233',
            email='owner@test.com',
            password='testpass123'
        )
        self.student = User.objects.create_user(
            phone_number='+79992223344',
            email='student@test.com',
            password='testpass123'
        )
        self.superuser = User.objects.create_superuser(
            phone_number='+79993334455',
            email='admin@test.com',
            password='testpass123'
        )

        # Создаем курс
        self.course_free = Course.objects.create(
            name='Бесплатный курс',
            description='Описание бесплатного курса',
            owner=self.owner,
            is_paid=False
        )

        self.course_paid = Course.objects.create(
            name='Платный курс',
            description='Описание платного курса',
            owner=self.owner,
            is_paid=True,
            price=1000
        )

        # Создаем уроки
        self.lesson_free = Lesson.objects.create(
            name='Урок в бесплатном курсе',
            description='Содержание урока',
            course=self.course_free,
            owner=self.owner
        )

        self.lesson_paid = Lesson.objects.create(
            name='Урок в платном курсе',
            description='Содержание платного урока',
            course=self.course_paid,
            owner=self.owner
        )

    def test_get_object(self):
        """Тест получения объекта урока"""
        view = LessonDetailView()
        view.kwargs = {'lesson_id': self.lesson_free.id}

        lesson = view.get_object()
        self.assertEqual(lesson, self.lesson_free)
        self.assertEqual(lesson.course, self.course_free)

    def _create_view_with_request(self, user, course_id, lesson_id):
        """Вспомогательный метод для создания view с запросом"""
        request = self.factory.get('/')
        request.user = user

        view = LessonDetailView()
        view.request = request
        view.args = ()
        view.kwargs = {'pk': course_id, 'lesson_id': lesson_id}

        return view, request

    def test_dispatch_free_course_authenticated(self):
        """Тест доступа авторизованного пользователя к бесплатному курсу"""
        view, request = self._create_view_with_request(
            self.student, self.course_free.id, self.lesson_free.id
        )

        # Должен разрешить доступ
        try:
            response = view.dispatch(request)
            self.assertTrue(response.status_code in [200, 302])
        except PermissionDenied:
            self.fail("Авторизованный пользователь должен иметь доступ к бесплатному курсу")

    def test_dispatch_paid_course_student_not_bought(self):
        """Тест доступа студента к платному курсу, который он не купил"""
        view, request = self._create_view_with_request(
            self.student, self.course_paid.id, self.lesson_paid.id
        )

        # Должен вызвать PermissionDenied
        with self.assertRaises(PermissionDenied) as context:
            view.dispatch(request)

        self.assertIn('У вас нет доступа', str(context.exception))

    def test_dispatch_paid_course_student_bought(self):
        """Тест доступа студента к купленному платному курсу"""
        # Добавляем курс в купленные
        self.student.bought_courses.add(self.course_paid)

        view, request = self._create_view_with_request(
            self.student, self.course_paid.id, self.lesson_paid.id
        )

        # Должен разрешить доступ
        try:
            response = view.dispatch(request)
            self.assertTrue(response.status_code in [200, 302])
        except PermissionDenied:
            self.fail("Студент с купленным курсом должен иметь доступ")

    def test_dispatch_owner_access(self):
        """Тест доступа владельца курса"""
        view, request = self._create_view_with_request(
            self.owner, self.course_paid.id, self.lesson_paid.id
        )

        # Должен разрешить доступ
        try:
            response = view.dispatch(request)
            self.assertTrue(response.status_code in [200, 302])
        except PermissionDenied:
            self.fail("Владелец курса должен иметь доступ")

    def test_dispatch_superuser_access(self):
        """Тест доступа суперпользователя"""
        view, request = self._create_view_with_request(
            self.superuser, self.course_paid.id, self.lesson_paid.id
        )

        # Должен разрешить доступ
        try:
            response = view.dispatch(request)
            self.assertTrue(response.status_code in [200, 302])
        except PermissionDenied:
            self.fail("Суперпользователь должен иметь доступ")

    def test_dispatch_lesson_owner_access(self):
        """Тест доступа владельца урока (не владельца курса)"""
        # Создаем отдельного владельца урока
        lesson_owner = User.objects.create_user(
            phone_number='+79994445566',
            email='lesson_owner@test.com',
            password='testpass123'
        )

        lesson = Lesson.objects.create(
            name='Урок от другого автора',
            description='Содержание',
            course=self.course_paid,
            owner=lesson_owner
        )

        view, request = self._create_view_with_request(
            lesson_owner, self.course_paid.id, lesson.id
        )

        # Должен разрешить доступ (владелец урока)
        try:
            response = view.dispatch(request)
            self.assertTrue(response.status_code in [200, 302])
        except PermissionDenied:
            self.fail("Владелец урока должен иметь доступ")

    def test_dispatch_anonymous_user_free_course(self):
        """Тест доступа анонимного пользователя к бесплатному курсу"""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get('/')
        request.user = AnonymousUser()

        view = LessonDetailView()
        view.request = request
        view.args = ()
        view.kwargs = {'pk': self.course_free.id, 'lesson_id': self.lesson_free.id}

        # Анонимный пользователь не имеет доступа
        with self.assertRaises(PermissionDenied):
            view.dispatch(request)

    def test_dispatch_anonymous_user_paid_course(self):
        """Тест доступа анонимного пользователя к платному курсу"""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get('/')
        request.user = AnonymousUser()

        view = LessonDetailView()
        view.request = request
        view.args = ()
        view.kwargs = {'pk': self.course_paid.id, 'lesson_id': self.lesson_paid.id}

        # Анонимный пользователь не имеет доступа
        with self.assertRaises(PermissionDenied):
            view.dispatch(request)

    def _create_view_with_request_and_object(self, user, course, lesson):
        """Вспомогательный метод для создания view с запросом и объектом"""
        request = self.factory.get('/')
        request.user = user

        view = LessonDetailView()
        view.request = request
        view.args = ()
        view.kwargs = {'pk': course.id, 'lesson_id': lesson.id}
        view.object = lesson  # Устанавливаем объект напрямую

        return view

    def test_get_context_data(self):
        """Тест контекстных данных"""
        view = self._create_view_with_request_and_object(
            self.owner, self.course_free, self.lesson_free
        )

        context = view.get_context_data()

        # Проверяем наличие нужных данных в контексте
        self.assertIn('course', context)
        self.assertEqual(context['course'], self.course_free)
        self.assertIn('can_edit', context)
        self.assertTrue(context['can_edit'])
        self.assertIn('lesson', context)
        self.assertEqual(context['lesson'], self.lesson_free)

    def test_can_edit_for_superuser(self):
        """Тест права редактирования для суперпользователя"""
        view = self._create_view_with_request_and_object(
            self.superuser, self.course_free, self.lesson_free
        )

        context = view.get_context_data()
        self.assertTrue(context['can_edit'])

    def test_can_edit_for_student(self):
        """Тест права редактирования для студента (без прав)"""
        view = self._create_view_with_request_and_object(
            self.student, self.course_free, self.lesson_free
        )

        context = view.get_context_data()
        self.assertFalse(context['can_edit'])

    def test_can_edit_for_course_owner(self):
        """Тест права редактирования для владельца курса"""
        view = self._create_view_with_request_and_object(
            self.owner, self.course_free, self.lesson_free
        )

        context = view.get_context_data()
        self.assertTrue(context['can_edit'])

    def test_can_edit_for_lesson_owner(self):
        """Тест права редактирования для владельца урока"""
        lesson_owner = User.objects.create_user(
            phone_number='+79995556677',
            email='lessonowner@test.com',
            password='testpass123'
        )

        lesson = Lesson.objects.create(
            name='Урок',
            description='Описание',
            course=self.course_free,
            owner=lesson_owner
        )

        view = self._create_view_with_request_and_object(
            lesson_owner, self.course_free, lesson
        )

        context = view.get_context_data()
        self.assertTrue(context['can_edit'])