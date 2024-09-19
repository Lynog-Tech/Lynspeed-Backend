from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import TestSession, Subject, Question, Worksheet, TestSessionQuestion
from ..serializers import SubjectSerializer, QuestionSerializer
from ..utils import format_error_response, validate_subject_selection
import random

class StartTestSessionView(APIView):
    """
    API endpoint to start a new test session.
    A test session is started with English as a compulsory subject,
    and any additional 3 subjects chosen by the user from their preferences.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle the creation of a test session based on selected subjects.
        """
        user = request.user
        selected_subject_names = request.data.get('subjects', [])

        user_preference = user.subject_preference
        if not user_preference:
            return Response(format_error_response(
                status.HTTP_400_BAD_REQUEST, 
                "NO_SUBJECT_PREFERENCE", 
                "User has not selected subject preferences."
            ))

        if not validate_subject_selection(selected_subject_names):
            return Response(format_error_response(
                status.HTTP_400_BAD_REQUEST, 
                "INVALID_SUBJECT_SELECTION", 
                "You must select exactly 4 subjects, including English."
            ))

        test_session = self._create_test_session(user, selected_subject_names)
        subjects_with_questions, assigned_question_ids = self._assign_questions_to_session(test_session)

        return Response({
            "test_session_id": test_session.id,
            "subjects": subjects_with_questions,
            "assigned_question_ids": assigned_question_ids
        }, status=status.HTTP_201_CREATED)

    def _create_test_session(self, user, selected_subject_names):
        selected_subjects = Subject.objects.filter(name__in=selected_subject_names)
        test_session = TestSession.objects.create(user=user)
        test_session.subjects.set(selected_subjects)
        return test_session

    def _assign_questions_to_session(self, test_session):
        subjects_with_questions = []
        assigned_question_ids = []

        for subject in test_session.subjects.all():
            worksheet, worksheet_data = self._get_worksheet_data_for_subject(subject)
            questions = Question.objects.filter(worksheet=worksheet).distinct()

            self._assign_questions_to_test_session(test_session, questions, assigned_question_ids)
            worksheet_data['questions'] = QuestionSerializer(questions, many=True).data
            subject_data = SubjectSerializer(subject).data
            subject_data['worksheets'] = [worksheet_data]
            subjects_with_questions.append(subject_data)

        return subjects_with_questions, assigned_question_ids

    def _get_worksheet_data_for_subject(self, subject):
        worksheets = Worksheet.objects.filter(subject=subject)
        if worksheets.exists():
            worksheet = random.choice(worksheets)
            worksheet_data = {
                "worksheet_id": worksheet.id,
                "worksheet_title": worksheet.name,
                "questions": []
            }
        else:
            worksheet_data = {
                "worksheet_id": None,
                "worksheet_title": "No worksheets available",
                "questions": []
            }
            worksheet = None

        return worksheet, worksheet_data

    def _assign_questions_to_test_session(self, test_session, questions, assigned_question_ids):
        for question in questions:
            TestSessionQuestion.objects.create(test_session=test_session, question=question)
            assigned_question_ids.append(question.id)
