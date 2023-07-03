from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from yanote.urls import *

User = get_user_model()

class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель заметки')
        cls.note = Note.objects.create(title='Заголовок', text='Текст', slug='text', author=cls.author)


    def test_note_in_context(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_list_notes_different_users(self):
        url = reverse('notes:list')
        users = (self.author, self.reader)
        for user in users:
            self.client.force_login(user)
            with self.subTest(user=user):
                response = self.client.get(url)
                object_list = response.context['note_list']
                if user == self.author:
                    self.assertIn(self.note, object_list)
                else:
                    self.assertNotIn(self.note, object_list)

    def test_add_edit_pages_have_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', self.note.slug),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                if name == 'notes:add':
                    url = reverse(name)
                else:
                    url = reverse(name, args=(args,))
                response = self.client.get(url)
                self.assertIn('form', response.context)




