from http import HTTPStatus

from django.test import Client

from .base import BaseTestCase


class TestRoutes(BaseTestCase):
    """Тестирование маршрутов."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_pages_availability(self):
        """Доступность страниц для разных пользователей."""
        test_cases = (
            (self.home_url, self.client, HTTPStatus.OK),
            (self.login_url, self.client, HTTPStatus.OK),
            (self.signup_url, self.client, HTTPStatus.OK),
            (self.logout_url, self.client, HTTPStatus.METHOD_NOT_ALLOWED),
            (self.detail_url, self.author_client, HTTPStatus.OK),
            (self.edit_url, self.author_client, HTTPStatus.OK),
            (self.delete_url, self.author_client, HTTPStatus.OK),
            (self.detail_url, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.edit_url, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.delete_url, self.reader_client, HTTPStatus.NOT_FOUND),
        )

        for url, client, expected_status in test_cases:
            with self.subTest(url=url, client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        """Редирект анонимного пользователя на страницу логина."""
        urls_without_args = (self.add_url, self.list_url, self.success_url)
        urls_with_args = (self.detail_url, self.edit_url, self.delete_url)

        for url in urls_without_args + urls_with_args:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
