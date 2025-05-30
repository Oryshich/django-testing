from http import HTTPStatus

from django.urls import reverse

from notes.models import Note
from .test_base import TestBaseNotePage


class TestRoutes(TestBaseNotePage):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.notes_home_url = reverse('notes:home')
        cls.users_login_url = reverse('users:login')
        cls.users_signup_url = reverse('users:signup')
        cls.users_logout_url = reverse('users:logout')
        cls.notes_list_url = reverse('notes:list')
        cls.notes_add_url = reverse('notes:add')
        cls.notes_success_url = reverse('notes:success')

    def test_pages_availability(self):
        urls = (
            self.notes_home_url,
            self.users_login_url,
            self.users_signup_url
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_logout_availability(self):
        response = self.not_author_client.post(self.users_logout_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            self.notes_list_url,
            self.notes_add_url,
            self.notes_success_url
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        urls = ('notes:detail', 'notes:edit', 'notes:delete')
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        new_note = Note.objects.get()
        for user, status in users_statuses:
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(new_note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        new_note = Note.objects.get()
        urls = (
            ('notes:detail', (new_note.slug,)),
            ('notes:edit', (new_note.slug,)),
            ('notes:delete', (new_note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
