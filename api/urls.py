from django.urls import path
from . import views

urlpatterns = [
    path('students/create/', views.create_student, name='create_student'),
    path('questions/', views.get_questions, name='get_questions'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('check-tie-scores/', views.check_tie_scores, name='check_tie_scores'),
]