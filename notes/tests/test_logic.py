from pytils.translit import slugify
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from yanote.urls import *
from notes.forms import WARNING

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.note_data = {'title':'Заголовок', 'text': 'Текст', 'slug': 'text', 'author': cls.author}
        cls.note_data_without_slug = {'title': 'Заголовок', 'text': 'Текст', 'author': cls.author}

    def test_create_note(self):
        url = reverse('notes:add')
        self.client.post(url, data=self.note_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)
        self.client.force_login(self.author)
        self.client.post(url, data=self.note_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_create_note_with_similar_slug(self):
        url = reverse('notes:add')
        self.client.force_login(self.author)
        self.client.post(url, data=self.note_data)
        response = self.client.post(url, data=self.note_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.note_data['slug'] + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_slug(self):
        url = reverse('notes:add')
        self.client.force_login(self.author)
        self.client.post(url, data=self.note_data_without_slug)
        note = Note.objects.get(pk=1)
        note_slug = note.slug
        note_title = note.title
        expected_slug = slugify(note_title)[:100]
        self.assertEqual(note_slug, expected_slug)

class TestEditDeleteNote(TestCase):
    NOTE_TEXT = 'Текст'
    NEW_NOTE_TEXT = 'Обновлённый текс'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель заметки')
        cls.note = Note.objects.create(title='Заголовок', text='Текст', slug='text', author=cls.author)
        cls.delete_url = reverse('notes:delete', args = (cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args = (cls.note.slug,))
        cls.form_data = {'text': cls.NEW_NOTE_TEXT, 'title':'Заголовок', 'slug': 'text', 'author': cls.author}

    def test_author_can_delete_comment(self):
        self.client.force_login(self.author)
        response = self.client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)


    def test_user_can_delete_author_comment(self):
        self.client.force_login(self.reader)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_comment(self):
        self.client.force_login(self.author)
        response = self.client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        self.client.force_login(self.reader)
        response = self.client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)









