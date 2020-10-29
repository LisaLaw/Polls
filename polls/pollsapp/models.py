import datetime

from django.db import models
from django.utils import timezone

from polls.users.models import User

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(default=timezone.now)#('date published')
    owner = models.ForeignKey(User, related_name='questions', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.question_text
    
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    def create(self, validated_data):
        return Question.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.question_text = validated_data.get('question_text', instance.question_text)
        instance.save()
        return instance

    def save(self, *args, **kwargs):
        super(Question, self).save(*args, **kwargs)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    owner = models.ForeignKey(User, related_name='choices', null=True, blank=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.choice_text