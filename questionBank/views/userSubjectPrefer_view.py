from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import UserSubjectPreference, Subject
from ..serializers import UserSubjectPreferenceSerializer
from ..utils import format_error_response

class UserSubjectPreferenceView(APIView):
    """
    API endpoint to allow users to set their subject preferences.
    Users can select 5 subjects, including English as compulsory.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the user's subject preferences.
        """
        user = request.user
        preference = get_object_or_404(UserSubjectPreference, user=user)
        serializer = UserSubjectPreferenceSerializer(preference)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Allow the user to select their preferred subjects.
        """
        user = request.user
        subjects = request.data.get('subjects', [])

        if len(subjects) != 5 or 'English' not in subjects:
            return Response(format_error_response(
                status.HTTP_400_BAD_REQUEST, 
                "INVALID_SUBJECT_SELECTION", 
                "You must select exactly 5 subjects, including English."
            ))

        selected_subjects = Subject.objects.filter(name__in=subjects)
        if selected_subjects.count() != 5:
            return Response(format_error_response(
                status.HTTP_400_BAD_REQUEST, 
                "INVALID_SUBJECTS", 
                "One or more invalid subjects selected."
            ))

        preference, _ = UserSubjectPreference.objects.get_or_create(user=user)
        preference.selected_subjects.set(selected_subjects)
        preference.save()

        return Response({"message": "Subjects selected successfully."}, status=status.HTTP_200_OK)
