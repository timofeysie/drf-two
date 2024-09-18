from django.urls import path
from . import views

urlpatterns = [
    # Questions
    path('questions/', views.QuestionList.as_view(), name='question-list'),
    path('questions/<int:pk>/', views.QuestionDetail.as_view(), name='question-detail'),

    # Answers
    path('answers/', views.AnswerList.as_view(), name='answer-list'),
    path('answers/<int:pk>/', views.AnswerDetail.as_view(), name='answer-detail'),

    # Votes
    path('votes/', views.VoteList.as_view(), name='vote-list'),
    path('votes/<int:pk>/', views.VoteDetail.as_view(), name='vote-detail'),
]