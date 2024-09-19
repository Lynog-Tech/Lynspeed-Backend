from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import TestSession, TestSessionQuestion, Question, UserResponse
from ..serializers import UserResponseSerializer
from ..utils import format_error_response, logger

class SubmitTestSessionView(APIView):
    """
    API endpoint to submit responses for a test session.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        test_session_id = request.data.get('test_session_id')
        responses = request.data.get('responses', [])

        if not test_session_id:
            return Response(format_error_response(
                status.HTTP_400_BAD_REQUEST, 
                "MISSING_TEST_SESSION_ID", 
                "Test session ID is required."
            ))

        test_session = self._get_active_test_session(test_session_id, user)
        if not test_session:
            return Response(format_error_response(
                status.HTTP_400_BAD_REQUEST, 
                "INVALID_TEST_SESSION", 
                "This test session is already completed or does not exist."
            ))

        assigned_question_ids = set(TestSessionQuestion.objects.filter(test_session=test_session).values_list('question_id', flat=True))
        submitted_question_ids = self._process_responses(user, test_session, responses, assigned_question_ids)

        if assigned_question_ids != submitted_question_ids:
            missing_questions = assigned_question_ids - submitted_question_ids
            logger.warning(f"Missing submitted questions for session {test_session_id}: {missing_questions}")

        self._complete_test_session(test_session)

        return Response({"detail": "Test session responses submitted successfully."}, status=status.HTTP_200_OK)

    def _get_active_test_session(self, test_session_id, user):
        test_session = get_object_or_404(TestSession, id=test_session_id, user=user)
        return test_session if not test_session.completed else None

    def _process_responses(self, user, test_session, responses, assigned_question_ids):
        submitted_question_ids = set()

        for response_data in responses:
            question_id = response_data.get('question_id')
            selected_option = response_data.get('selected_option')

            if not question_id or int(question_id) not in assigned_question_ids:
                logger.error(f"Question ID {question_id} not found or invalid in session {test_session.id}")
                continue

            submitted_question_ids.add(int(question_id))
            self._save_user_response(user, test_session, question_id, selected_option)

        return submitted_question_ids

    def _save_user_response(self, user, test_session, question_id, selected_option):
        question = get_object_or_404(Question, id=question_id)
        serializer = UserResponseSerializer(data={
            'user': user.id,
            'question': question.id,
            'selected_option': selected_option,
            'test_session': test_session.id
        })

        if serializer.is_valid():
            serializer.save()
        else:
            logger.error(f"Validation error for question {question_id}: {serializer.errors}")

    def _complete_test_session(self, test_session):
        test_session.end_time = timezone.now()
        test_session.completed = True
        test_session.save()
