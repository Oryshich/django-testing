from django.urls import reverse

from notes.forms import NoteForm
from .test_base import TestBaseNotePage


class TestNotePage(TestBaseNotePage):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse('notes:list')

    def test_note_in_list_for_author(self):
        response = self.author_client.get(self.url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        response = self.not_author_client.get(self.url)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
