from django.test import TestCase
from rest_framework.test import APIRequestFactory
import factory
from .models import *
import datetime
import faker


# тест на создание отзыва.


class CarFactory(factory.Factory):
    class Meta:
        model = Car


class UserFactory(factory.Factory):
    class Meta:
        model = AuthUser


class ReviewFactory(factory.Factory):
    class Meta:
        model = Review

    owner = factory.SubFactory(UserFactory)
    car = factory.SubFactory(CarFactory)


class UserCreateTestCase(TestCase):
    mock_data = {
        "is_superuser": 0,
        "username": "test user",
        "first_name": "test",
        "last_name": "test",
        "email": "test@test.com",
    }

    def setUp(self):
        self.test_review = UserFactory.create(**self.mock_data)

    def test_review_created(self):
        for key in self.mock_data.keys():
            self.assertEqual(getattr(self.test_review, key), self.mock_data[key])



class ReviewCreateTestCase(TestCase):
    mock_data = {
        "message": "test review",
        "date": datetime.datetime.now(),
        "cross_country_point": 1,
        "economic_point": 4,
        "safety_point": 3,
        "contrallabilty_point": 2,
        "reliable_point": 2,
        "comfort_point": 2,
        "title": "test review"
    }

    def setUp(self):
        self.test_review = ReviewFactory.create(**self.mock_data)

    def test_review_created(self):
        for key in self.mock_data.keys():
            self.assertEqual(getattr(self.test_review, key), self.mock_data[key])

#
