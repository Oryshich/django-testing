from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestBaseNotePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Тестовая запись для Note',
            text='Просто текст.',
            slug='slug_string',
            author=cls.author
        )
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.author_client = Client()
        cls.not_author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)
