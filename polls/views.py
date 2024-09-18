from django.db.models import Count
from rest_framework import generics, permissions, filters
from rest_framework.exceptions import ValidationError
from .models import Question, Answer, Vote
from .serializers import QuestionSerializer, AnswerSerializer, VoteSerializer
from drf_two.permissions import IsOwnerOrReadOnly


class QuestionList(generics.ListCreateAPIView):
    """
    Provides a list of all questions and allows authenticated users to create
    new questions. Questions are listed with a count of votes for their
    answers, ordered by creation date in descending order. The view also
    supports search functionality on question text and owner username.
    """
    queryset = Question.objects.annotate(votes_count=Count(
        'answers__votes', distinct=True)).order_by('-created_at')
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'owner__username',
        'text',
    ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Provides detailed view for a specific question, including capabilities
    to update or delete. Only the owner of the question has the permissions
    to update or delete it.
    """
    queryset = Question.objects.annotate(votes_count=Count(
        'answers__votes', distinct=True)).order_by('-created_at')
    serializer_class = QuestionSerializer
    permission_classes = [IsOwnerOrReadOnly]


class AnswerList(generics.ListCreateAPIView):
    """
    Lists all answers for questions, annotated with a count of votes
    for each answer, ordered by their creation date in descending order.
    """
    queryset = Answer.objects.annotate(votes_count=Count(
        'votes', distinct=True)).order_by('-created_at')
    serializer_class = AnswerSerializer


class AnswerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Provides a detailed view for a specific answer, allowing retrieval,
    update, and deletion operations. Updates and deletions are restricted
    to the owner of the answer.
    """
    queryset = Answer.objects.annotate(votes_count=Count(
        'votes', distinct=True))
    serializer_class = AnswerSerializer


class VoteList(generics.ListCreateAPIView):
    """
    Provides a list of all votes and allows authenticated users
    to create a vote on an answer. Prevents a user from voting
    more than once on the same question.
    """
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user
        question = serializer.validated_data['answer'].question

        if Vote.objects.filter(answer__question=question, voter=user).exists():
            raise ValidationError(
                {"error": "You have already voted on this question"})

        serializer.save(voter=user, question=question)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class VoteDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Allows detailed operations on a specific vote.
    """
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
