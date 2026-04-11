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


class TestNoteEditPage(TestCase):
    """Тестирование страницы редактирования заметки."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def setUp(self):
        self.client.force_login(self.author)

    def test_edit_page_contains_form(self):
        """На страницу редактирования заметки передаётся форма."""
        response = self.client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)


class TestNoteListPage(TestCase):
    """Тестирование страницы списка заметок."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.other_user = User.objects.create(username='Другой пользователь')
        cls.list_url = reverse('notes:list')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author
        )

    def test_note_in_list_for_author(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list для автора.
        """
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_other_user(self):
        """
        В список заметок одного пользователя не попадают
        заметки другого пользователя.
        """
        self.client.force_login(self.other_user)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)
