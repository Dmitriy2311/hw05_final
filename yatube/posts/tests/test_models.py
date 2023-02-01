from django.test import TestCase

from posts.models import Group, Post, User, MAX_LONG_TEXT
from posts.tests.test_constant import (
    TEST_USER, AUTH, TEST_GROUP, TEST_SLUG, TEST_DESCRIPT, TEST_POST,
    GROUP, TEXT, AUTHOR
)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USER)
        cls.group = Group.objects.create(
            title=TEST_GROUP,
            slug=TEST_SLUG,
            description=TEST_DESCRIPT,
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_POST,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, модели и модели группы корректно работает __str__."""
        with self.subTest(str=str):
            self.assertEqual(self.post.text[:MAX_LONG_TEXT], str(self.post))
            self.assertEqual(self.group.title, str(self.group))

    def test_verbose_name(self):
        """verbose_name в полях модели совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            TEXT: TEST_POST,
            AUTHOR: AUTH,
            GROUP: TEST_GROUP,
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected)
