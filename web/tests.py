from django.test import TestCase
from django.contrib.auth.models import User, Group
from web.models import users_for_user


class GroupSeparationTest(TestCase):

    def test_users_for_user(self):
        group_a = Group.objects.create(name='A')
        group_b = Group.objects.create(name='B')

        user_a_1 = User.objects.create(username='user_a_1')
        user_a_2 = User.objects.create(username='user_a_2')
        user_a_3 = User.objects.create(username='user_a_3')

        group_a.user_set.add(user_a_1)
        group_a.user_set.add(user_a_2)
        group_a.user_set.add(user_a_3)

        user_b_1 = User.objects.create(username='user_b_1')
        user_b_2 = User.objects.create(username='user_b_2')
        user_b_3 = User.objects.create(username='user_b_3')

        group_b.user_set.add(user_b_1)
        group_b.user_set.add(user_b_2)
        group_b.user_set.add(user_b_3)

        user = User.objects.get(id=user_a_1.pk)
        users = users_for_user(user)

        self.assertEquals(
            set([u.pk for u in users]),
            set([user_a_2.pk, user_a_3.pk])
        )
