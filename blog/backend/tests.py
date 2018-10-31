from django.test import TestCase
from backend.models import User, Question


class TestRating(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user("tegrdjkhgkjdrhkjghdr", "hgreh@kfdsj.re", "grgr")
        self.question_1 = Question.objects.create(title="regeg", text="fewfw", author_id=self.user_1.id)

    def test_question_rating(self):
        self.assertEqual(0, self.question_1.rating)
        self.question_1.rating_change(self.user_1)
        self.assertEqual(1, self.question_1.rating)
        self.question_1.rating_change(self.user_1)
        self.assertEqual(0, self.question_1.rating)
        self.question_1.rating_change(self.user_1)
        self.assertEqual(1, self.question_1.rating)
