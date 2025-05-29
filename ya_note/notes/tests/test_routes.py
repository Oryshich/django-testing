from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пользователь №1')
        cls.reader = User.objects.create(username='Пользователь №2')
        cls.note = Note.objects.create(
            title='Заголовок #1',
            text='Текст #1',
            slug='WWW',
            author=cls.author
        )
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_pages_availability(self):
        urls = (('notes:home', 'users:login', 'users:signup'))
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_logout_availability(self):
        url = reverse('users:logout')
        response = self.reader_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = ('notes:list', 'notes:add', 'notes:success')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        urls = ('notes:detail', 'notes:edit', 'notes:delete')
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        self.author_client.post(reverse('notes:add'), data={'text': 'XXXX'})
        new_note = Note.objects.get()
        for user, status in users_statuses:
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(new_note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        self.author_client.post(reverse('notes:add'), data={'text': 'XXXX'})
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
