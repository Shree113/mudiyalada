import logging
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.db.models import Count
import random
import string

from .models import Student, Question, StudentAnswer
from .serializers import StudentSerializer, QuestionSerializer, StudentAnswerSerializer

logger = logging.getLogger(__name__)

@api_view(['POST'])
def create_student(request):
    """
    Create a new student entry.
    """
    serializer = StudentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def superuser_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_superuser:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "message": "Login successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You are not authorized as an admin"}, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['DELETE'])
def delete_student(request, pk):
    try:
        student = Student.objects.get(pk=pk)
        student.delete()
        return Response({'message': 'Student deleted'}, status=200)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)

@api_view(['GET'])
def get_questions(request):
    """
    Retrieve all questions
    """
    try:
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    """
    Retrieve quiz questions based on student status
    """
    student_id = request.query_params.get('student_id')
    
    try:
        student = Student.objects.get(id=student_id)
        if student.needs_retest:
            # Get retest questions
            questions = Question.objects.filter(is_retest=True)
        else:
            # Get regular questions
            questions = Question.objects.filter(is_retest=False)
        
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    except Student.DoesNotExist:
        return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

# Remove the generate_question and old get_retest_questions functions as they're no longer needed
@api_view(['POST'])
def get_retest_questions(request):
    """
    Get unused questions for retesting tied students
    """
    student_id = request.query_params.get('student_id')
    
    # Get questions this student hasn't answered yet
    answered_questions = StudentAnswer.objects.filter(
        student_id=student_id
    ).values_list('question_id', flat=True)
    
    # Get 5 unused questions from admin-added questions
    new_questions = Question.objects.exclude(
        id__in=answered_questions
    ).order_by('?')[:5]
    
    if not new_questions:
        return Response({
            "message": "No more questions available for retest"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = QuestionSerializer(new_questions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def generate_question():
    """
    Generate a random question with options
    """
    operators = ['+', '-', '*']
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    operator = random.choice(operators)
    
    if operator == '+':
        answer = num1 + num2
    elif operator == '-':
        answer = num1 - num2
    else:
        answer = num1 * num2
    
    question_text = f"What is {num1} {operator} {num2}?"
    
    # Generate 4 options with one correct answer
    correct_option = 'A'
    options = [
        answer,
        answer + random.randint(1, 5),
        answer - random.randint(1, 5),
        answer + random.randint(-5, -1)
    ]
    random.shuffle(options)
    
    # Find where the correct answer is after shuffling
    correct_option = string.ascii_uppercase[options.index(answer)]
    
    return {
        'text': question_text,
        'option_a': str(options[0]),
        'option_b': str(options[1]),
        'option_c': str(options[2]),
        'option_d': str(options[3]),
        'correct_option': correct_option
    }

@api_view(['POST'])
def get_retest_questions(request):
    """
    Generate new questions for retesting tied students
    """
    num_questions = 5  # Number of retest questions
    questions = []
    
    for _ in range(num_questions):
        question_data = generate_question()
        question = Question.objects.create(**question_data)
        questions.append(question)
    
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def submit_answer(request):
    """
    Submit an answer for a question
    """
    student_id = request.data.get('student_id')
    question_id = request.data.get('question_id')
    chosen_option = request.data.get('chosen_option')

    if not all([student_id, question_id, chosen_option]):
        return Response(
            {"error": "Missing required fields"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        student = Student.objects.get(id=student_id)
        question = Question.objects.get(id=question_id)
        
        # Check if answer already exists
        existing_answer = StudentAnswer.objects.filter(
            student=student,
            question=question
        ).first()
        
        if existing_answer:
            return Response(
                {"error": "Answer already submitted for this question"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create answer and check if correct
        is_correct = chosen_option.upper() == question.correct_option.upper()
        
        # Store the answer
        StudentAnswer.objects.create(
            student=student,
            question=question,
            chosen_option=chosen_option.upper(),
            is_correct=is_correct
        )
        
        # Update student's score if answer is correct
        if is_correct:
            student.total_score = student.total_score + 5  # Add 5 points for correct answer
            student.save()
            
            return Response({
                "message": "Correct answer! Score updated.",
                "score": student.total_score
            })
        else:
            return Response({
                "message": "Incorrect answer.",
                "score": student.total_score
            })
    
    except Student.DoesNotExist:
        return Response(
            {"error": "Student not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Question.DoesNotExist:
        return Response(
            {"error": "Question not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def leaderboard(request):
    """
    Get the leaderboard sorted by total score
    """
    try:
        # Get top 10 students by score
        students = Student.objects.all().order_by('-total_score', 'name')[:10]
        
        # Create detailed leaderboard data
        leaderboard_data = []
        for rank, student in enumerate(students, 1):
            correct_answers = StudentAnswer.objects.filter(
                student=student,
                is_correct=True
            ).count()
            
            leaderboard_data.append({
                'rank': rank,
                'student_name': student.name,
                'college': student.college,
                'total_score': student.total_score,
                'correct_answers': correct_answers
            })
        
        return Response({
            'leaderboard': leaderboard_data
        })
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def complete_quiz(request):
    """
    Mark the quiz as completed for a student
    """
    student_id = request.data.get('student_id')
    try:
        student = Student.objects.get(id=student_id)
        # Add any completion logic here
        return Response({"message": "Quiz completed successfully"})
    except Student.DoesNotExist:
        return Response(
            {"error": "Student not found"},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def check_tie_scores(request):
    """
    Check for students with tied scores
    """
    # Get scores that appear more than once
    tied_scores = Student.objects.values('total_score')\
        .annotate(count=Count('total_score'))\
        .filter(count__gt=1)\
        .order_by('-total_score')

    if not tied_scores:
        return Response({"message": "No tied scores found"})

    # Get students with tied scores
    tied_students = []
    for score in tied_scores:
        students = Student.objects.filter(total_score=score['total_score'])
        tied_students.extend(StudentSerializer(students, many=True).data)

    return Response({
        "tied_scores_found": True,
        "students": tied_students
    })
