from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import TestSession, TestSessionQuestion, UserResponse, Question
from ..serializers import QuestionSerializer, UserResponseSerializer
from ..utils import format_error_response

class ViewTestSessionResultsView(APIView):
    """
    API endpoint to view failed questions in a completed test session.
    Shows the failed questions grouped by subject, along with user's incorrect response 
    and the correct answer for each failed question.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        """
        Get the failed questions of the specified test session, grouped by subject.
        """
        user = request.user
        test_session = get_object_or_404(TestSession, id=session_id, user=user)

        if not test_session.completed:
            return Response(format_error_response(
                status.HTTP_400_BAD_REQUEST, 
                "INCOMPLETE_TEST_SESSION", 
                "The test session is not yet completed."
            ))

        # Fetch session questions and user responses
        session_questions = TestSessionQuestion.objects.filter(test_session=test_session)
        user_responses = UserResponse.objects.filter(test_session=test_session, user=user)

        failed_questions_by_subject = self._get_failed_questions_by_subject(session_questions, user_responses)

        return Response({
            "test_session_id": test_session.id,
            "subjects": [subject.name for subject in test_session.subjects.all()],
            "start_time": test_session.start_time,
            "end_time": test_session.end_time,
            "failed_questions_by_subject": failed_questions_by_subject  # Failed questions grouped by subject
        }, status=status.HTTP_200_OK)

    def _get_failed_questions_by_subject(self, session_questions, user_responses):
        """
        Build a dictionary of failed questions grouped by subject.
        Each entry will contain the failed question, the user's incorrect response, 
        and the correct option for that question.
        """
        question_response_map = {response.question.id: response for response in user_responses}
        failed_questions_by_subject = {}

        for session_question in session_questions:
            question = session_question.question
            user_response = question_response_map.get(question.id)
            subject = question.subject.name  # Assuming Question has a 'subject' field

            # Initialize the subject group if not already present
            if subject not in failed_questions_by_subject:
                failed_questions_by_subject[subject] = []

            # If user answered the question and it was incorrect
            if user_response and question.correct_option != user_response.selected_option:
                failed_question = {
                    "question": QuestionSerializer(question).data,
                    "user_response": UserResponseSerializer(user_response).data,
                    "correct_option": question.correct_option  # Add the correct option for failed questions
                }
                failed_questions_by_subject[subject].append(failed_question)

        return failed_questions_by_subject
