from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тестирование создания заметок."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст заметки',
            'slug': 'new-slug'
        }

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count_before = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)

        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)


class TestNoteEditDelete(TestCase):
    """Тестирование редактирования и удаления заметок."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заметка для теста',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author
        )

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

        cls.form_data = {
            'title': 'Обновлённая заметка',
            'text': 'Обновлённый текст',
            'slug': 'updated-slug'
        }

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_user_cant_edit_note_of_another_user(self):
        """Другой пользователь не может редактировать чужую заметку."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.form_data['title'])
        self.assertNotEqual(self.note.text, self.form_data['text'])

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)

        notes_count = Note.objects.filter(slug=self.note.slug).count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Другой пользователь не может удалить чужую заметку."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        notes_count = Note.objects.filter(slug=self.note.slug).count()
        self.assertEqual(notes_count, 1)
