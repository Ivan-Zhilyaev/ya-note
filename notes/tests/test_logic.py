from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

from .base import BaseTestCase


class TestNoteCreation(BaseTestCase):
    """Тестирование создания заметок."""

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_before = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        notes_after = Note.objects.count()
        self.assertEqual(notes_before, notes_after)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        Note.objects.exclude(id=self.note.id).delete()
        notes_before = Note.objects.count()

        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        notes_after = Note.objects.count()
        self.assertEqual(notes_after, notes_before + 1)

        new_note = Note.objects.exclude(id=self.note.id).get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        notes_before = Note.objects.count()
        self.form_data['slug'] = self.note.slug

        response = self.author_client.post(self.add_url, data=self.form_data)

        notes_after = Note.objects.count()
        self.assertEqual(notes_before, notes_after)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        form = response.context['form']
        self.assertIn('slug', form.errors)
        self.assertIn(self.note.slug + WARNING, form.errors['slug'])

    def test_empty_slug(self):
        """Если slug не указан, он формируется автоматически."""
        Note.objects.exclude(id=self.note.id).delete()
        notes_before = Note.objects.count()

        data_without_slug = {
            'title': 'Моя новая заметка',
            'text': 'Текст заметки',
        }

        response = self.author_client.post(
            self.add_url, data=data_without_slug
        )
        self.assertRedirects(response, self.success_url)

        notes_after = Note.objects.count()
        self.assertEqual(notes_after, notes_before + 1)

        new_note = Note.objects.exclude(id=self.note.id).get()
        expected_slug = slugify(data_without_slug['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(BaseTestCase):
    """Тестирование редактирования и удаления заметок."""

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.author_client.post(
            self.edit_url, data=self.edit_form_data
        )
        self.assertRedirects(response, self.success_url)

        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.edit_form_data['title'])
        self.assertEqual(updated_note.text, self.edit_form_data['text'])
        self.assertEqual(updated_note.slug, self.edit_form_data['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_other_user_cant_edit_note(self):
        """Другой пользователь не может редактировать чужую заметку."""
        response = self.reader_client.post(
            self.edit_url, data=self.edit_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        notes_before = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_after = Note.objects.count()
        self.assertEqual(notes_after, notes_before - 1)

    def test_other_user_cant_delete_note(self):
        """Другой пользователь не может удалить чужую заметку."""
        notes_before = Note.objects.count()
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_after = Note.objects.count()
        self.assertEqual(notes_before, notes_after)
