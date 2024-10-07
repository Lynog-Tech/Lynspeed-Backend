from rest_framework import serializers
from .models import PerformanceRecord, PerformanceAnalysis, PerformanceChart, Subject

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']

class PerformanceRecordSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()

    class Meta:
        model = PerformanceRecord
        fields = ['id', 'user', 'subject', 'date', 'score', 'speed']

    def create(self, validated_data):
        # Extract subject data
        subject_data = validated_data.pop('subject')
        # Get or create the subject instance
        
        if subject_data:
            # Get or create the subject instance
            subject, created = Subject.objects.get_or_create(name=subject_data['name'])
        else:
            raise serializers.ValidationError({'subject': 'This field is required.'})
        subject, created = Subject.objects.get_or_create(name=subject_data['name'])
        # Create the performance record with the subject
        performance_record = PerformanceRecord.objects.create(subject=subject, **validated_data)
        return performance_record

    def update(self, instance, validated_data):
        # Extract and handle subject data
        subject_data = validated_data.get('subject', None)
        if subject_data:
            subject, created = Subject.objects.get_or_create(name=subject_data['name'])
            instance.subject = subject
        
        # Update the instance fields
       
        instance.user = validated_data.get('user', instance.user)
        instance.date = validated_data.get('date', instance.date)
        instance.score = validated_data.get('score', instance.score)
        instance.speed = validated_data.get('speed', instance.speed)
        instance.save()
        return instance

class PerformanceAnalysisSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()

    class Meta:
        model = PerformanceAnalysis
        fields = ['id', 'user', 'subject', 'average_score', 'average_speed']

    def create(self, validated_data):
        subject_data = validated_data.pop('subject')
        subject, created = Subject.objects.get_or_create(name=subject_data['name'])
        performance_analysis = PerformanceAnalysis.objects.create(subject=subject, **validated_data)
        return performance_analysis

    def update(self, instance, validated_data):
        subject_data = validated_data.pop('subject')
        subject, created = Subject.objects.get_or_create(name=subject_data['name'])
        instance.subject = subject
        instance.user = validated_data.get('user', instance.user)
        instance.average_score = validated_data.get('average_score', instance.average_score)
        instance.average_speed = validated_data.get('average_speed', instance.average_speed)
        instance.save()
        return instance
    
class PerformanceChartSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()

    class Meta:
        model = PerformanceChart
        fields = ['id', 'user', 'subject', 'chart_data']

    def create(self, validated_data):
        subject_data = validated_data.pop('subject')
        subject, created = Subject.objects.get_or_create(name=subject_data['name'])
        performance_chart = PerformanceChart.objects.create(subject=subject, **validated_data)
        return performance_chart

    def update(self, instance, validated_data):
        subject_data = validated_data.pop('subject')
        subject, created = Subject.objects.get_or_create(name=subject_data['name'])
        instance.subject = subject
        instance.user = validated_data.get('user', instance.user)
        instance.chart_data = validated_data.get('chart_data', instance.chart_data)
        instance.save()
        return instance