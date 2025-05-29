from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст новости'
    TEST_SLUG = 'TEST_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.url = reverse('notes:add')
        cls.login_url = reverse('users:login')
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.user_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.user_client.force_login(cls.user)
        cls.form_data = {
            'title': 'Заголовок',
            'text': cls.NOTE_TEXT,
            'author': cls.author,
            'slug': cls.TEST_SLUG}

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.url, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_not_unique_slug(self):
        Note.objects.create(
            title='Заголовок',
            text=self.NOTE_TEXT,
            author=self.author,
            slug=self.TEST_SLUG)
        response = self.auth_client.post(self.url, data=self.form_data)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=self.TEST_SLUG + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        expected_count = Note.objects.count() + 1
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(
            Note.objects.count(),
            expected_count,
            msg=('Проверьте количество записей в БД!')
        )
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        new_note = Note.objects.get()
        url = reverse('notes:edit', args=(new_note.slug,))
        response = self.auth_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        new_note.refresh_from_db()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        new_note = Note.objects.get()
        url = reverse('notes:edit', args=(new_note.slug,))
        response = self.user_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=new_note.id)
        self.assertEqual(new_note.title, note_from_db.title)
        self.assertEqual(new_note.text, note_from_db.text)
        self.assertEqual(new_note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        new_note = Note.objects.get()
        url = reverse('notes:delete', args=(new_note.slug,))
        response = self.auth_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        new_note = Note.objects.get()
        url = reverse('notes:delete', args=(new_note.slug,))
        response = self.user_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
