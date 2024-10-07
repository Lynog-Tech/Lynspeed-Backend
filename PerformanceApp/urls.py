from django.urls import path
from .views import PerformanceRecordListView, PerformanceRecordDetailView, PerformanceAnalysisListView, PerformanceChartView

urlpatterns = [
    path('records/', PerformanceRecordListView.as_view(), name='performance-records'),
    path('records/<int:pk>/', PerformanceRecordDetailView.as_view(), name='performance-record-detail'),
    path('analysis/', PerformanceAnalysisListView.as_view(), name='performance-analysis'),
    path('charts/<int:pk>/', PerformanceChartView.as_view(), name='performance-chart'),
]
