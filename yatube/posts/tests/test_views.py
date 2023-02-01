from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post, Comment, Follow, User
from posts.tests.test_constant import (
    INDEX, POST_CREATE, GROUP_LIST, PROFILE, TEST_POST, POST_ID, COMMENT,
    EDIT, AUTH, TEST_NAME, TEST_SLUG, TEST_DISCRIP, PAGE, POST,  LOGIN,
    INDEX, POST_CREATE, GROUP_LIST, DETAIL, TEST_OF_POST, FORM, USER,
    INDEX_HTML, CREATE_HTML, GROUP_LIST_HTML, SLUG, USER_NAME, GUEST,
    PAGE_OBJ, AUTHOR, TEXT, GROUP, FOLLOW_INDEX, ADD_COMMENT, PROFFILE_FOLLOW,
    PROFFILE_UNFOLLOW, TEST_COMMENT, ERROR_REDIRECT_GUEST, ERROR_VALUE_COMMENT,
    ERROR_REDIRECT, ERROR_FIND_COMMENT, ERROR_CHANGE_VAJUE_COMMENT, ERROR_ADD_COMMENT
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
            INDEX_HTML: reverse(INDEX),
            CREATE_HTML: reverse(POST_CREATE),
            GROUP_LIST_HTML: reverse(
                GROUP_LIST,
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
        response = self.authorized_client1.get(reverse(INDEX))
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
                GROUP_LIST,
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
        response = self.authorized_client1.get(reverse(POST_CREATE))

        form_fields = {
            GROUP: forms.fields.ChoiceField,
            TEXT: forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context[FORM].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_posts_context_post_edit_template(self):
        """
        Проверка, сформирован ли шаблон post_edit с
        правильным контекстом.
        """
        response = self.authorized_client1.get(
            reverse(
                EDIT,
                kwargs={POST_ID: self.post.id},
            )
        )

        form_fields = {TEXT: forms.fields.CharField}

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(FORM).fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_context_profile_template(self):
        """
        Проверка, сформирован ли шаблон profile с
        правильным контекстом.
        """
        response = self.authorized_client1.get(
            reverse(
                PROFILE,
                kwargs={USER_NAME: self.user1.username},
            )
        )
        profile = {AUTHOR: self.post.author}

        for value, expected in profile.items():
            with self.subTest(value=value):
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
                DETAIL,
                kwargs={POST_ID: self.post.id},
            )
        )

        profile = {POST: self.post}

        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)

    def test_posts_not_from_foreign_group(self):
        """
        Проверка, при указании группы поста, попадает
        ли он в другую группу.
        """
        response = self.authorized_client1.get(reverse(INDEX))
        self.posts_check_all_fields(response.context[PAGE_OBJ][0])
        post = response.context[PAGE_OBJ][0]
        group = post.group
        self.assertEqual(group, self.group)

    def test_post_comment_guest_user(self):
        """
        Проверка неавторизированного пользователя
        на редирект при попытке комментирования
        и невозможность комментирования.
        """
        comment_count = Comment.objects.count()
        form_data = {TEXT: TEST_COMMENT}
        response_guest = self.guest_client.post(
            reverse(ADD_COMMENT, kwargs={POST_ID: self.post.id}),
            data=form_data,
            follow=True,
        )
        redirect_page = reverse(LOGIN) + '?next=%2Fposts%2F1%2Fcomment%2F'
        self.assertRedirects(
            response_guest,
            redirect_page,
            msg_prefix=ERROR_REDIRECT_GUEST,
        )
        self.assertEqual(
            Comment.objects.count(),
            comment_count,
            ERROR_VALUE_COMMENT,
        )

    def test_post_comment_authorized_user(self):
        """
        Проверка авторизированного пользователя
        на редирект после комментирования,
        возможность комментирования,
        изменяемое количество комментариев и их добавление.
        """
        comment_count = Comment.objects.count()
        form_data = {TEXT: TEST_COMMENT}
        response_authorized = self.authorized_client1.post(
            reverse(ADD_COMMENT, kwargs={POST_ID: self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response_authorized,
            reverse(DETAIL, kwargs={POST_ID: self.post.id}),
            msg_prefix=ERROR_REDIRECT,
        )
        self.assertEqual(
            response_authorized.context.get(COMMENT)[0].text,
            TEST_COMMENT,
            ERROR_FIND_COMMENT,
        )
        self.assertEqual(
            Comment.objects.count(),
            comment_count + 1,
            ERROR_CHANGE_VAJUE_COMMENT,
        )
        self.assertTrue(
            Comment.objects.filter(
                text=TEST_COMMENT,
                author=self.user1,
                post_id=self.post.id,
            ).exists(),
            ERROR_ADD_COMMENT,
        )

    def test_post_profile_follow(self):
        """Проверка, возможно ли подписаться на автора поста."""
        self.authorized_client1.get(
            reverse(PROFFILE_FOLLOW, kwargs={USER_NAME: AUTHOR})
        )
        self.assertTrue(
            Follow.objects.filter(
                author=self.author,
                user=self.user1,
            ).exists(),
        )

    def test_post_profile_unfollow(self):
        """Проверка, возможно ли отписаться от автора поста."""
        self.authorized_client2.get(
            reverse(PROFFILE_UNFOLLOW, kwargs={USER_NAME: AUTHOR})
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
            reverse(FOLLOW_INDEX)
        )
        post_follow = response_follower.context.get(PAGE_OBJ)[0]
        self.assertEqual(post_follow, self.post)

    def test_post_follow_index_unfollower(self):
        """Проверка находится ли пост в ленте не подписчика."""
        response_unfollower = self.authorized_client1.get(
            reverse(FOLLOW_INDEX)
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
            reverse(INDEX),
            reverse(GROUP_LIST, kwargs={SLUG: self.group.slug}),
            reverse(PROFILE, kwargs={USER_NAME: self.user1.username}),
        ]
        for url in url_pages:
            for page, count in pages:
                response = self.client.get(url, {PAGE: page})
                self.assertEqual(
                    len(response.context[PAGE_OBJ]), count,
                )
