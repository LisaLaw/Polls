from rest_framework import serializers

from polls.pollsapp.models import Question, Choice

class QuestionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'pub_date', 'owner']

class ChoiceSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'owner']