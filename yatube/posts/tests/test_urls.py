from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests.test_constant import (
    INDEX, GROUP_LIST, PROFILE, TEST_POST, PROFILE_HTML, PROFILE,
    EDIT, AUTH, NO_AUTH, TEST_SLUG, TEST_DESCRIPT, SLUG, USER_NAME,
    INDEX, GROUP_LIST, DETAIL, DETAIL_HTML, POST_CREATE, POST_ID,
    INDEX_HTML, CREATE_HTML, GROUP_LIST_HTML, TEST_GROUP
)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTH)
        cls.user_not_author = User.objects.create_user(
            username=NO_AUTH
        )
        cls.group = Group.objects.create(
            title=TEST_GROUP,
            slug=TEST_SLUG,
            description=TEST_DESCRIPT,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_POST,
        )

        cls.url_names_public = {
            INDEX_HTML: reverse(INDEX),
            GROUP_LIST_HTML: reverse(
                GROUP_LIST,
                kwargs={SLUG: TEST_SLUG},
            ),
            PROFILE_HTML: reverse(
                PROFILE,
                kwargs={USER_NAME: cls.user.username},
            ),
            DETAIL_HTML: reverse(
                DETAIL,
                kwargs={POST_ID: cls.post.id},
            ),
        }

        cls.url_autorized = {
            INDEX_HTML: reverse(INDEX),
            GROUP_LIST_HTML: reverse(
                GROUP_LIST,
                kwargs={SLUG: TEST_SLUG},
            ),
            PROFILE_HTML: reverse(
                PROFILE,
                kwargs={USER_NAME: cls.user.username},
            ),
            DETAIL_HTML: reverse(
                DETAIL,
                kwargs={POST_ID: cls.post.id},
            ),
            CREATE_HTML: reverse(
                EDIT,
                kwargs={POST_ID: cls.post.id},
            ),
        }

        cls.url_names_redirects = {
            reverse(
                EDIT, kwargs={POST_ID: cls.post.id}): (
                f"/auth/login/?next=/posts/{cls.post.pk}/edit/"
            ),
            "/create/": "/auth/login/?next=/create/",
        }

        cls.url_names_templates = {
            reverse(INDEX): INDEX_HTML,
            reverse(
                GROUP_LIST, kwargs={SLUG: TEST_SLUG}
            ): GROUP_LIST_HTML,
            reverse(
                PROFILE, kwargs={USER_NAME: cls.user.username}
            ): PROFILE_HTML,
            reverse(
                DETAIL, kwargs={POST_ID: cls.post.id}
            ): DETAIL_HTML,
            reverse(
                EDIT, kwargs={POST_ID: cls.post.id}
            ): CREATE_HTML,
            reverse(POST_CREATE): CREATE_HTML,
        }

        cls.url_unexisting_page = "/unexisting_page/"

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author)

    def test_guest_urls_public(self):
        """Страницы доступные любому пользователю."""

        for address in self.url_names_public.items():
            with self.subTest(eaddress=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_autorized_urls_access(self):
        """Страницы доступные авторизованному пользователю."""

        for address in self.url_autorized.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_list_url_redirect_guest(self):
        """Страницы перенаправляют анонимного пользователя
        на страницу логина.
        """

        for address, redirect_address in self.url_names_redirects.items():
            with self.subTest(address=address):
                response = self.client.get(address, follow=True)
                self.assertRedirects(response, redirect_address)

    def test_redirect_not_author(self):
        """Редирект при попытке редактирования поста не автором"""

        response = self.authorized_client_not_author.get(
            f"/posts/{self.post.pk}/edit/", follow=True
        )
        self.assertRedirects(response, f"/posts/{self.post.pk}/")

    def test_task_list_url_corret_templates(self):
        """Страницы доступные авторизованному пользователю."""

        for address, template in self.url_names_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_not_found(self):
        """Страница не найденна."""

        response = self.client.get(self.url_unexisting_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
