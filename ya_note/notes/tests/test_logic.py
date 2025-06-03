from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_base import TestBaseNotePage


class TestNoteCreation(TestBaseNotePage):

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(
            self.notes_add_url,
            data=self.form_data
        )
        self.assertRedirects(response, self.notes_success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_count = Note.objects.count()
        response = self.client.post(self.notes_add_url, data=self.form_data)
        expected_url = f'{self.users_login_url}?next={self.notes_add_url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count() - notes_count
        self.assertEqual(notes_count, 0)

    def test_not_unique_slug(self):
        notes_count = Note.objects.count()
        response = self.author_client.post(
            self.notes_add_url,
            data=self.form_data
        )
        notes_count = Note.objects.count() - notes_count
        self.assertEqual(notes_count, 0)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=self.TEST_SLUG + WARNING
        )

    def test_empty_slug(self):
        Note.objects.all().delete()
        expected_count = 1
        self.form_data.pop('slug')
        response = self.author_client.post(
            self.notes_add_url,
            data=self.form_data
        )
        self.assertRedirects(response, self.notes_success_url)
        self.assertEqual(
            Note.objects.count(),
            expected_count,
            msg=('Проверьте количество записей в БД!')
        )
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        new_form_data = {
            'title': 'Измененный заголовок',
            'text': 'Текст №2',
            'slug': self.TEST_SLUG}
        response = self.author_client.post(self.notes_edit_url, new_form_data)
        self.assertRedirects(response, self.notes_success_url)
        note_after = Note.objects.get(pk=self.note.id)
        self.assertEqual(note_after.title, new_form_data['title'])
        self.assertEqual(note_after.text, new_form_data['text'])
        self.assertEqual(note_after.slug, self.form_data['slug'])
        self.assertEqual(note_after.author, self.note.author)

    def test_other_user_cant_edit_note(self):
        new_form_data = {
            'title': 'Измененный заголовок',
            'text': 'Текст №2',
            'slug': self.TEST_SLUG}
        response = self.not_author_client.post(
            self.notes_edit_url,
            new_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        notes_count = Note.objects.count()
        response = self.author_client.post(self.notes_delete_url)
        self.assertRedirects(response, self.notes_success_url)
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_other_user_cant_delete_note(self):
        notes_count = Note.objects.count()
        response = self.not_author_client.post(self.notes_delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)
