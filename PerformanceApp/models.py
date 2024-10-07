from django.db import models
from django.conf import settings

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class PerformanceRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='performance_records')
    date = models.DateField(auto_now_add=True)
    score = models.FloatField()  # Percentage score
    speed = models.FloatField()  # Time taken to complete the subject test (in seconds)

    def __str__(self):
        return f"{self.user.username}'s performance in {self.subject.name} on {self.date}"

class PerformanceAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance_analysis')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    average_score = models.FloatField()
    average_speed = models.FloatField()

    def calculate_average_score(self):
        records = self.user.performance_records.filter(subject=self.subject)
        total_score = sum(record.score for record in records)
        self.average_score = total_score / len(records) if records.exists() else 0
        self.save()

    def calculate_average_speed(self):
        records = self.user.performance_records.filter(subject=self.subject)
        total_speed = sum(record.speed for record in records)
        self.average_speed = total_speed / len(records) if records.exists() else 0
        self.save()

    def __str__(self):
        return f"{self.user.username}'s analysis for {self.subject.name}"

class PerformanceChart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance_charts')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    chart_data = models.JSONField()  # Stores chart data (e.g., scores over time)

    def generate_chart_data(self):
        records = self.user.performance_records.filter(subject=self.subject).order_by('date')
        self.chart_data = {
            'dates': [record.date.strftime('%Y-%m-%d') for record in records],
            'scores': [record.score for record in records],
            'speeds': [record.speed for record in records],
        }
        self.save()

    def __str__(self):
        return f"Performance chart for {self.user.username} in {self.subject.name}"
