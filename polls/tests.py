import datetime

import django.urls
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question


# Create your tests here.


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_have_choice_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    question.choice_set.create(choice_text='choice1', votes=0)
    return question


def create_no_choice_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    return question


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        question = create_have_choice_question(question_text='Past question.', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        create_have_choice_question(question_text='Future question.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        question = create_have_choice_question(question_text='Past question.', days=-30)
        create_have_choice_question(question_text='Future question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_question(self):
        question1 = create_have_choice_question(question_text='Past question1.', days=-30)
        question2 = create_have_choice_question(question_text='Past question2.', days=-5)
        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question1, question2],
        )

    def test_no_choice_question(self):
        create_no_choice_question(question_text='no choice question.', days=-1)
        response = self.client.get(reverse('polls:index'))

        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_have_choice_question(self):
        question = create_have_choice_question(question_text='have choice question.', days=-1)
        url = reverse('polls:index')
        response = self.client.get(url)

        self.assertContains(response, question.question_text)

    def test_have_choice_question_and_no_choice_question(self):
        have_choice_question = create_have_choice_question(question_text='have choice question.', days=-1)
        create_no_choice_question(question_text='no choice question.', days=-1)
        url = reverse('polls:index')
        response = self.client.get(url)

        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 [have_choice_question])

    def test_admin_user_index_view(self):
        past_question = create_no_choice_question(question_text='Past question.', days=-1)
        future_question = create_no_choice_question(question_text='Future question.', days=5)

        url = reverse('polls:index')
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 [past_question, future_question])

    def test_user_index_view(self):
        past_question = create_no_choice_question(question_text='Past question.', days=-1)
        future_question = create_no_choice_question(question_text='Future question.', days=5)

        url = reverse('polls:index')
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 [past_question])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_have_choice_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_have_choice_question(question_text='Past question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionResultViewTests(TestCase):
    def test_future_question_vote_results(self):
        future_question = create_have_choice_question(question_text='Future question.', days=5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_vote_results(self):
        past_question = create_have_choice_question(question_text='Past question.', days=-5)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
