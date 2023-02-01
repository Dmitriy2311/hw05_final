from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests.test_constant import (
    POST_CREATE, EDIT, SLUG, NEW_USER, POST_ID, GROUP,
    TEST_NAME_GROUP, TEST_DESCRIP_GROUP, POST, TEXT,
    TEXT_POST, TEXT_POST_FORM, NEW_TEXT_POST, DETAIL
)


class PostsFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=NEW_USER)
        cls.group = Group.objects.create(
            title=TEST_NAME_GROUP,
            slug=SLUG,
            description=TEST_DESCRIP_GROUP,
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=TEXT_POST,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_posts_forms_create_post(self):
        """Проверка, создает ли форма пост в базе."""
        post_count = Post.objects.count()
        form_data = {
            TEXT: TEXT_POST_FORM,
            GROUP: self.group.id,
        }
        self.authorized_client.post(
            reverse(POST_CREATE),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text=TEXT_POST_FORM,
            group=self.group.id,
        ).exists())

    def test_posts_forms_edit_post(self):
        """Проверка, редактируется ли пост."""
        form_data = {
            TEXT: NEW_TEXT_POST,
            GROUP: self.group.id,
        }
        self.authorized_client.post(reverse(
            EDIT,
            kwargs={POST_ID: self.post.id},
        ), data=form_data)
        response = self.authorized_client.get(reverse(
            DETAIL,
            kwargs={POST_ID: self.post.id},
        ))
        self.assertEqual(response.context[POST].text, NEW_TEXT_POST)
        self.assertTrue(Post.objects.filter(
            text=NEW_TEXT_POST,
            group=self.group.id,
        ).exists())
