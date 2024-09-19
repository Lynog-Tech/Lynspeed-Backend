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
    API endpoint to view the results of a completed test session.
    Shows the questions, user's answers, and whether the answers were correct or incorrect.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        """
        Get the results of the specified test session.
        """
        user = request.user
        test_session = get_object_or_404(TestSession, id=session_id, user=user)

        if not test_session.completed:
            return Response(format_error_response(
                status.HTTP_400_BAD_REQUEST, 
                "INCOMPLETE_TEST_SESSION", 
                "The test session is not yet completed."
            ))

        # Fetch questions and user's responses
        session_questions = TestSessionQuestion.objects.filter(test_session=test_session)
        user_responses = UserResponse.objects.filter(test_session=test_session, user=user)

        results = self._get_test_results(session_questions, user_responses)

        return Response({
            "test_session_id": test_session.id,
            "subjects": [subject.name for subject in test_session.subjects.all()],
            "start_time": test_session.start_time,
            "end_time": test_session.end_time,
            "results": results
        }, status=status.HTTP_200_OK)

    def _get_test_results(self, session_questions, user_responses):
        """
        Build the test session results, including each question, the user's response, 
        and whether it was correct.
        """
        question_response_map = {response.question.id: response for response in user_responses}
        results = []

        for session_question in session_questions:
            question = session_question.question
            user_response = question_response_map.get(question.id)

            result = {
                "question": QuestionSerializer(question).data,
                "user_response": None,
                "correct": False
            }

            if user_response:
                result["user_response"] = UserResponseSerializer(user_response).data
                result["correct"] = question.correct_option == user_response.selected_option

            results.append(result)

        return results
