
import datetime
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

from polls.users.models import User, Question
from polls.users.tests.factories import UserFactory


class UserAPITests(APITestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_list_users(self):
        UserFactory.create_batch(size=10)
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/v1/users/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(1, data["count"])

    def test_register_user(self):
        users = User.objects.all().count()
        data = {
            "email": "new@example.com",
            "password": "some_password",
            "questions": [], #needed, but empty because a new user doesn't have any questions associated with them yet
            "choices": [],
            }
        response = self.client.post("/api/v1/users/", data=data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(users + 1, User.objects.all().count())
        user = User.objects.get(email=data["email"])
        self.assertTrue(user.check_password(data["password"]))

    def test_get_me(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/v1/users/me/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("id", data)

    def test_update_me(self):
        self.client.force_authenticate(self.user)
        data = {
            "email": "client1@example.com",
            "password": "new_password",
        }
        response = self.client.patch("/api/v1/users/me/", data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(data["email"], user.email)
        self.assertTrue(user.check_password(data["password"]))


class VerifyEmailAPITests(APITestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_request_restore_code(self):
        self.user.is_email_verified = False
        self.user.save()
        self.assertFalse(self.user.is_email_verified)
        data = {
            "verification_code": self.user.verification_code,
        }
        response = self.client.post(
            "/api/v1/verify_email/",
            data=data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.is_email_verified)


class RestorePasswordAPITests(APITestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_request_restore_code(self):
        self.assertIsNone(self.user.restore_password_code)
        data = {
            "email": self.user.email,
        }
        response = self.client.post(
            "/api/v1/request_restore_code/",
            data=data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(pk=self.user.pk)
        self.assertIsNotNone(user.restore_password_code)

    def test_restore_password(self):
        self.user.send_restore_code()
        data = {
            "password": "new_password",
            "repeat_password": "new_password",
            "restore_password_code": self.user.restore_password_code,
        }
        response = self.client.post(
            "/api/v1/restore_password/",
            data=data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.check_password(data["password"]))


class QuestionTest(APITestCase):

    def setUp(self):
        self.question = Question() #now I can use question as an instance of the Model Question

        #create a user to prevent 403 error
        self.user = UserFactory()

    def test_question_is_created(self):
        #force authentiaction
        self.client.force_authenticate(self.user)

        questions = Question.objects.all().count() #get all Question instances and count them
        data = {
            "question_text": "new question text",
            } 
        response = self.client.post('/api/v1/questions/', data=data, format="json") #user adds a questions in url "questions/" with the question text from above. Get back the result in json
        #'/api/v1/users/'
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) #check if status code of the new question equals 201
        self.assertEqual(questions + 1, Question.objects.all().count()) #check if all Question instances have augmented by 1 (a new question has been created)

    def test_question_text_is_not_empty(self):
        question_text = Question('question_text') #get the question text for all questions
        self.assertIsNot(question_text, '') #checks that question text isn't empty
