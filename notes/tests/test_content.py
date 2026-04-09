from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNoteCreatePage(TestCase):
    """Тестирование страницы создания заметки."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')

    def setUp(self):
        self.client.force_login(self.author)

    def test_authorized_client_has_form(self):
        """Авторизованный пользователь видит форму."""
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_slug_auto_generation(self):
        """Если slug не указан, он генерируется из заголовка."""
        response = self.client.post(self.add_url, data={
            'title': 'Моя новая заметка',
            'text': 'Текст заметки',
        })
        self.assertRedirects(response, self.success_url)
        new_note = Note.objects.get(title='Моя новая заметка')
        self.assertEqual(new_note.slug, 'moya-novaya-zametka')

    def test_slug_uniqueness(self):
        """Нельзя создать две заметки с одинаковым slug."""
        self.client.post(self.add_url, data={
            'title': 'Первая заметка',
            'text': 'Текст',
            'slug': 'same-slug'
        })

        response = self.client.post(self.add_url, data={
            'title': 'Вторая заметка',
            'text': 'Другой текст',
            'slug': 'same-slug'
        })

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('slug', form.errors)
        self.assertIn(
            'same-slug - такой slug уже существует, '
            'придумайте уникальное значение!',
            form.errors['slug']
        )
