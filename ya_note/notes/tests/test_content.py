from notes.forms import NoteForm
from .test_base import TestBaseNotePage


class TestNotePage(TestBaseNotePage):

    def test_note_in_list_for_author(self):
        response = self.author_client.get(self.notes_list_url)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_note_not_in_list_for_another_user(self):
        response = self.not_author_client.get(self.notes_list_url)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_pages_contains_form(self):
        urls = (
            (self.notes_add_url),
            (self.notes_edit_url)
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
