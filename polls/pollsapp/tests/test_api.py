from rest_framework import status
from rest_framework.test import APITestCase

from polls.pollsapp.models import Question
from polls.users.models import User
from polls.users.tests.factories import UserFactory

# Create your tests here.
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
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) #check if status code of the new question equals 201
        self.assertEqual(questions + 1, Question.objects.all().count()) #check if all Question instances have augmented by 1 (a new question has been created)
        
    def test_question_text_is_not_empty(self):
        question_text = Question('question_text') #get the question text for all questions
        self.assertIsNot(question_text, '') #checks that question text isn't empty
        