from http import HTTPStatus

from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_base import TestBaseNotePage


class TestNoteCreation(TestBaseNotePage):
    NOTE_TEXT = 'Текст новости'
    TEST_SLUG = 'TEST_slug'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Note.objects.all().delete()
        cls.url = reverse('notes:add')
        cls.login_url = reverse('users:login')
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': 'Заголовок',
            'text': cls.NOTE_TEXT,
            'author': cls.author,
            'slug': cls.TEST_SLUG}
        cls.note = Note.objects.create(
            title=cls.form_data['title'],
            text=cls.form_data['text'],
            author=cls.form_data['author'],
            slug=cls.form_data['slug'])

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_count = Note.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count() - notes_count
        self.assertEqual(notes_count, 0)

    def test_not_unique_slug(self):
        notes_count = Note.objects.count()
        response = self.author_client.post(self.url, data=self.form_data)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=self.TEST_SLUG + WARNING
        )
        notes_count = Note.objects.count() - notes_count
        self.assertEqual(notes_count, 0)

    def test_empty_slug(self):
        Note.objects.all().delete()
        expected_count = 1
        self.form_data.pop('slug')
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(
            Note.objects.count(),
            expected_count,
            msg=('Проверьте количество записей в БД!')
        )
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        new_note = Note.objects.get(pk=self.note.id)
        url = reverse('notes:edit', args=(new_note.slug,))
        response = self.author_client.post(url, self.form_data)
        self.assertRedirects(response, self.success_url)
        note_after = Note.objects.get(pk=self.note.id)
        self.assertEqual(note_after.title, self.form_data['title'])
        self.assertEqual(note_after.text, self.form_data['text'])
        self.assertEqual(note_after.slug, self.form_data['slug'])
        self.assertEqual(note_after.author, self.author)

    def test_other_user_cant_edit_note(self):
        new_note = Note.objects.get()
        url = reverse('notes:edit', args=(new_note.slug,))
        response = self.not_author_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=new_note.id)
        self.assertEqual(new_note.title, note_from_db.title)
        self.assertEqual(new_note.text, note_from_db.text)
        self.assertEqual(new_note.slug, note_from_db.slug)
        self.assertEqual(new_note.author, self.author)

    def test_author_can_delete_note(self):
        new_note = Note.objects.get()
        url = reverse('notes:delete', args=(new_note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        notes_count = Note.objects.count()
        new_note = Note.objects.get()
        url = reverse('notes:delete', args=(new_note.slug,))
        response = self.not_author_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)
