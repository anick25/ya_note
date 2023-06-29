from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from yanote.urls import *

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель заметки')
        cls.note = Note.objects.create(title='Заголовок', text='Текст', slug='text', author=cls.author)


    def test_home_page(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        self.client.force_login(self.author)
        urls = ('notes:list', 'notes:add', 'notes:success')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_note_edit_delete(self):
        users = ((self.author, HTTPStatus.OK),
                 (self.reader, HTTPStatus.NOT_FOUND))
        urls = (
            ('notes:detail', self.note.slug),
            ('notes:edit', self.note.slug),
            ('notes:delete', self.note.slug)
        )
        for user, status in users:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(name=name, user=user):
                    url = reverse(name, args=(args,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):

        login_url = reverse('users:login')
        for name, args in (('notes:list', None),
                     ('notes:success', None),
                     ('notes:add', None),
                     ('notes:detail', self.note.slug),
                     ('notes:edit', self.note.slug),
                     ('notes:delete', self.note.slug)):
            with self.subTest(name=name, args=args):
                if args is None:
                    url = reverse(name)
                else:
                    url = reverse(name, args=(args,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)


