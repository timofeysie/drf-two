from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    """
    Represents a question posted by a user. A question is identified
    by its owner and the textual content of the question itself. Each
    question has a timestamp indicating when it was created and
    can be associated with multiple answers.
    """
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Question {self.id} by {self.owner}"


class Answer(models.Model):
    """
    Represents an answer to a specific question. Each answer is linked
    to a question and contains text as its content. Answers are
    timestamped at creation.
    """
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Answer {self.id} to Question {self.question.id}"


class Vote(models.Model):
    """
    Represents a vote cast by a user for an answer to a question. Each vote is
    linked not only to the answer but also directly to the question for
    integrity and quick querying purposes. A user can only vote once per
    question, ensuring uniqueness of the voter-question pair.
    """
    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(
        User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('question', 'voter')
        ordering = ['-created_at']

    def __str__(self):
        return f"Vote by {self.voter} for {self.answer}"