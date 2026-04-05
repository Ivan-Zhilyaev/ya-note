from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author
        )

    def test_pages_availability_for_anonymous(self):
        """Доступность страниц для анонимного пользователя."""
        urls = (
            ('notes:home', None, HTTPStatus.OK),
            ('users:login', None, HTTPStatus.OK),
            ('users:signup', None, HTTPStatus.OK),
        )
        for name, args, expected_status in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

        url = reverse('users:logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_availability_for_note_pages(self):
        """Доступность страниц заметок для разных пользователей."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user.username, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Редирект анонимного пользователя на страницу логина."""
        login_url = reverse('users:login')
        for name in ('notes:add', 'notes:list', 'notes:success',
                     'notes:edit', 'notes:delete', 'notes:detail'):
            with self.subTest(name=name):
                if name in ('notes:edit', 'notes:delete', 'notes:detail'):
                    url = reverse(name, args=(self.note.slug,))
                else:
                    url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
