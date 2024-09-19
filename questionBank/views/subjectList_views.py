from rest_framework import generics
from ..models import Subject
from ..serializers import SubjectSerializer
from ..cache_utils import get_cached_subjects

class SubjectListView(generics.ListAPIView):
    """
    API endpoint to retrieve the list of subjects.
    English is always included as a compulsory subject.
    """
    serializer_class = SubjectSerializer

    def get_queryset(self):
        """
        Override the default method to retrieve cached subjects
        """
        return get_cached_subjects()
