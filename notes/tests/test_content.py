from notes.forms import NoteForm

from .base import BaseTestCase


class TestContent(BaseTestCase):
    """Тестирование контента."""

    def test_pages_contains_form(self):
        """На страницы создания и редактирования передаётся форма."""
        test_cases = (
            (self.add_url, 'notes:add'),
            (self.edit_url, 'notes:edit'),
        )
        for url, name in test_cases:
            with self.subTest(name=name):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_in_list_for_author(self):
        """Заметка отображается в списке у автора."""
        response = self.author_client.get(self.list_url)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_other_user(self):
        """Заметка не отображается в списке у другого пользователя."""
        response = self.reader_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)
        self.assertIn(self.other_note, object_list)
