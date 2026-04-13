from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс для всех тестов."""

    @classmethod
    def setUpTestData(cls):
        """Создание общих фикстур и URL для всех тестов."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author
        )

        cls.other_note = Note.objects.create(
            title='Чужая заметка',
            text='Текст',
            slug='other-slug',
            author=cls.reader
        )

        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст заметки',
            'slug': 'new-slug'
        }

        cls.edit_form_data = {
            'title': 'Обновлённая заметка',
            'text': 'Обновлённый текст',
            'slug': 'updated-slug'
        }

        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.signup_url = reverse('users:signup')
        cls.logout_url = reverse('users:logout')
        cls.add_url = reverse('notes:add')
        cls.list_url = reverse('notes:list')
        cls.success_url = reverse('notes:success')
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
