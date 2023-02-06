from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post, Comment, Follow, User
from posts.tests.test_constant import (
    URL_INDEX, URL_POST_CREATE, URL_GROUP_LIST, URL_PROFILE, TEST_POST,
    URL_EDIT, AUTH, TEST_NAME, TEST_SLUG, TEST_DISCRIP, PAGE, POST, LOGIN,
    URL_INDEX, URL_POST_CREATE, URL_GROUP_LIST, URL_DETAIL, TEST_OF_POST,
    INDEX_HTML, CREATE_HTML, GROUP_LIST_HTML, SLUG, USER_NAME, GUEST,
    PAGE_OBJ, AUTHOR, TEXT, GROUP, URL_FOLLOW_INDEX, URL_ADD_COMMENT,
    URL_PROFFILE_UNFOLLOW, COMMENT, FORM, USER, POST_ID
)


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create(username=GUEST)
        cls.user2 = User.objects.create(username=USER)
        cls.author = User.objects.create(username=AUTHOR)
        cls.group = Group.objects.create(
            title=TEST_NAME,
            slug=TEST_SLUG,
            description=TEST_DISCRIP,
        )

        cls.post = Post.objects.create(
            text=TEST_POST,
            author=cls.user1,
            group=cls.group,
        )

        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.user1
        )

        cls.templates_pages_names = {
            INDEX_HTML: reverse(URL_INDEX),
            CREATE_HTML: reverse(URL_POST_CREATE),
            GROUP_LIST_HTML: reverse(
                URL_GROUP_LIST,
                kwargs={SLUG: TEST_SLUG},
            )
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        cache.clear()

    def posts_check_all_fields(self, post):
        """Метод, проверяющий поля поста."""
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, self.post.group.id)

    def test_posts_pages_use_correct_template(self):
        """Проверка, использует ли адрес URL соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client1.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_context_index_template(self):
        """
        Проверка, сформирован ли шаблон group_list с
        правильным контекстом.
        Появляется ли пост, при создании на главной странице.
        """
        response = self.authorized_client1.get(reverse(URL_INDEX))
        self.posts_check_all_fields(response.context[PAGE_OBJ][0])
        last_post = response.context[PAGE_OBJ][0]
        self.assertEqual(last_post, self.post)

    def test_posts_context_group_list_template(self):
        """
        Проверка, сформирован ли шаблон group_list с
        правильным контекстом.
        Появляется ли пост, при создании на странице его группы.
        """
        response = self.authorized_client1.get(
            reverse(
                URL_GROUP_LIST,
                kwargs={SLUG: self.group.slug},
            )
        )
        test_group = response.context[GROUP]
        self.posts_check_all_fields(response.context[PAGE_OBJ][0])
        test_post = str(response.context[PAGE_OBJ][0])
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_post, str(self.post))

    def test_posts_context_create_post_template(self):
        """
        Проверка, сформирован ли шаблон create_post с
        правильным контекстом.
        """
        response = self.authorized_client1.get(reverse(URL_POST_CREATE))

        form_fields = {
            GROUP: forms.fields.ChoiceField,
            TEXT: forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            form_field = response.context[FORM].fields[value]
            self.assertIsInstance(form_field, expected)

    def test_posts_context_post_edit_template(self):
        """
        Проверка, сформирован ли шаблон post_edit с
        правильным контекстом.
        """
        response = self.authorized_client1.get(
            reverse(
                URL_EDIT,
                kwargs={POST_ID: self.post.id},
            )
        )

        form_fields = {TEXT: forms.fields.CharField}

        for value, expected in form_fields.items():
            form_field = response.context.get(FORM).fields.get(value)
            self.assertIsInstance(form_field, expected)

    def test_posts_context_profile_template(self):
        """
        Проверка, сформирован ли шаблон profile с
        правильным контекстом.
        """
        response = self.authorized_client1.get(
            reverse(
                URL_PROFILE,
                kwargs={USER_NAME: self.user1.username},
            )
        )
        profile = {AUTHOR: self.post.author}

        for value, expected in profile.items():
            context = response.context[value]
            self.assertEqual(context, expected)

        self.posts_check_all_fields(response.context[PAGE_OBJ][0])
        test_page = response.context[PAGE_OBJ][0]
        self.assertEqual(test_page, self.user1.posts.all()[0])

    def test_posts_context_post_detail_template(self):
        """
        Проверка, сформирован ли шаблон post_detail с
        правильным контекстом.
        """
        response = self.authorized_client1.get(
            reverse(
                URL_DETAIL,
                kwargs={POST_ID: self.post.id},
            )
        )

        profile = {POST: self.post}

        for value, expected in profile.items():
            context = response.context[value]
            self.assertEqual(context, expected)

    def test_posts_not_from_foreign_group(self):
        """
        Проверка, при указании группы поста, попадает
        ли он в другую группу.
        """
        response = self.authorized_client1.get(reverse(URL_INDEX))
        self.posts_check_all_fields(response.context[PAGE_OBJ][0])
        post = response.context[PAGE_OBJ][0]
        group = post.group
        self.assertEqual(group, self.group)

    def test_post_comment_authorized_user(self):
        """
        Проверка авторизированного пользователя
        может ли комментировать посты
        """
        comment = Comment.objects.create(
            text=COMMENT,
            author=self.user1,
            post_id=self.post.id
        )
        response = (self.client.post(
            reverse(
                URL_ADD_COMMENT, 
                kwargs={POST_ID: self.post.id}
            )
        ))
        response = (self.client.get(
            reverse(
                URL_DETAIL,
                kwargs={POST_ID: self.post.id}
            )
        ))
        self.assertContains(response, comment)

    def test_comment_post_guest_user(self):
        """Проверка, гость не может комментировать посты."""
        response = (self.guest_client.post(
            reverse(
                URL_ADD_COMMENT, 
                kwargs={POST_ID: self.post.id}
            )
        ))
        self.assertRedirects(response, reverse(
            LOGIN) + '?next=' + reverse(
                URL_ADD_COMMENT,
            kwargs={POST_ID: self.post.id})
        )

    def test_post_profile_unfollow(self):
        """Проверка, возможно ли отписаться от автора поста."""
        self.authorized_client2.get(
            reverse(
                URL_PROFFILE_UNFOLLOW, 
                kwargs={USER_NAME: AUTHOR}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                author=self.author,
                user=self.user2
            ).exists()
        )

    def test_post_follow_index_follower(self):
        """Проверка, находится ли новый пост в ленте подписчика."""
        response_follower = self.authorized_client2.get(
            reverse(URL_FOLLOW_INDEX)
        )
        post_follow = response_follower.context.get(PAGE_OBJ)[0]
        self.assertEqual(post_follow, self.post)

    def test_post_follow_index_unfollower(self):
        """Проверка находится ли пост в ленте не подписчика."""
        response_unfollower = self.authorized_client1.get(
            reverse(URL_FOLLOW_INDEX)
        )
        post_unfollow = response_unfollower.context.get(PAGE_OBJ)
        self.assertEqual(post_unfollow.object_list.count(), 0)


class PostsPaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username=AUTH)
        cls.authorized_client1 = Client()
        cls.authorized_client1.force_login(cls.user1)
        cls.group = Group.objects.create(
            title=TEST_NAME,
            slug=TEST_SLUG,
            description=TEST_DISCRIP,
        )
        bilk_post: list = []
        for count in range(TEST_OF_POST):
            bilk_post.append(Post(text=f'Тестовый текст {count}',
                                  group=cls.group,
                                  author=cls.user1))
        Post.objects.bulk_create(bilk_post)

    def test_paginator_on_pages(self):
        """Проверка пагинации на страницах."""

        PAGE_ONE = 10
        PAGE_TWO = 3

        pages = (
                (1, PAGE_ONE),
                (2, PAGE_TWO)
        )
        url_pages = [
            reverse(URL_INDEX),
            reverse(
                URL_GROUP_LIST, 
                kwargs={SLUG: self.group.slug}
            ),
            reverse(
                URL_PROFILE, 
                kwargs={USER_NAME: self.user1.username}
            ),
        ]
        for url in url_pages:
            for page, count in pages:
                response = self.client.get(url, {PAGE: page})
                self.assertEqual(
                    len(response.context[PAGE_OBJ]), count,
                )
