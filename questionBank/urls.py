from django.urls import path
from questionBank.views.subjectList_views import SubjectListView
from questionBank.views.userSubjectPrefer_view import UserSubjectPreferenceView
from questionBank.views.startTestSession_view import StartTestSessionView
from questionBank.views.submitTestSession_view import SubmitTestSessionView
from questionBank.views.viewTestResult_view import ViewTestSessionResultsView


urlpatterns = [
    path('subjects/', SubjectListView.as_view(), name='subject-list'),

    # URL for managing user subject preferences
    path('user/subjects/', UserSubjectPreferenceView.as_view(), name='user-subject-preferences'),

    # URL for starting a new test session
    path('test-session/start/', StartTestSessionView.as_view(), name='start-test-session'),

    # URL for submitting the test session
    path('test-session/submit/', SubmitTestSessionView.as_view(), name='submit-test-session'),

    # URL for viewing the results of a test session
    path('test-session/<int:session_id>/results/', ViewTestSessionResultsView.as_view(), name='view-test-session-results'),
]
