from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestBaseNotePage(TestCase):
    NOTE_TEXT = 'Текст новости'
    TEST_SLUG = 'TEST_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.form_data = {
            'title': 'Заголовок',
            'text': cls.NOTE_TEXT,
            'slug': cls.TEST_SLUG}
        cls.note = Note.objects.create(
            title=cls.form_data['title'],
            text=cls.form_data['text'],
            author=cls.author,
            slug=cls.form_data['slug'])
        cls.author_client = Client()
        cls.not_author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)
        cls.notes_detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.notes_edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.notes_delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.notes_home_url = reverse('notes:home')
        cls.users_login_url = reverse('users:login')
        cls.users_signup_url = reverse('users:signup')
        cls.users_logout_url = reverse('users:logout')
        cls.notes_list_url = reverse('notes:list')
        cls.notes_add_url = reverse('notes:add')
        cls.notes_success_url = reverse('notes:success')
