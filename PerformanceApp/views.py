from rest_framework import generics
from .models import PerformanceRecord, PerformanceAnalysis, PerformanceChart
from .serializers import PerformanceRecordSerializer, PerformanceAnalysisSerializer, PerformanceChartSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

# Performance Record Views
class PerformanceRecordListView(generics.ListCreateAPIView):
    serializer_class = PerformanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PerformanceRecord.objects.filter(user=self.request.user)

class PerformanceRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PerformanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PerformanceRecord.objects.filter(user=self.request.user)

# Performance Analysis Views
class PerformanceAnalysisListView(generics.ListAPIView):
    serializer_class = PerformanceAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PerformanceAnalysis.objects.filter(user=self.request.user)

# Performance Chart Views
class PerformanceChartView(generics.RetrieveAPIView):
    serializer_class = PerformanceChartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PerformanceChart.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        chart_instance = serializer.save(user=self.request.user)
        chart_instance.generate_chart_data()  # Generates the chart data
