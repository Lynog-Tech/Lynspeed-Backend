from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from random import sample

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    def get_worksheets(self):
        return self.worksheets.all()

    def get_questions(self):
        return Question.objects.filter(worksheet__subject=self)

class UserSubjectPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subject_preference')
    selected_subjects = models.ManyToManyField(Subject, related_name='user_preferences')
    
    def clean(self):
        if self.selected_subjects.count() > 4:
            raise ValidationError("You can only select up to 4 subjects including English.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        english_subject = Subject.objects.get(name="English")
        self.selected_subjects.add(english_subject)

    def __str__(self):
        return f"{self.user.username}'s subject preferences"

    def get_available_test_subjects(self):
        return self.selected_subjects.all()

class Worksheet(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='worksheets')
    name = models.CharField(max_length=100)
    file_path = models.CharField(max_length=255, blank=True)
    
    class Meta:
        unique_together = ['subject', 'name']

    def __str__(self):
        return f"{self.subject.name} - {self.name}"
    
    def get_questions(self):
        return self.questions.all()

class Question(models.Model):
    OPTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]

    worksheet = models.ForeignKey(Worksheet, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=255, default='Option A')
    option_b = models.CharField(max_length=255, default='Option B')
    option_c = models.CharField(max_length=255, default='Option C')
    option_d = models.CharField(max_length=255, default='Option D')
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    image = models.ImageField(upload_to='question_images/', null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.worksheet.name} - {self.text[:50]}..."

    def get_options(self):
        return {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d
        }

    @property
    def correct_answer(self):
        return self.get_options()[self.correct_option]

class TestSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    subjects = models.ManyToManyField(Subject)
    completed = models.BooleanField(default=False)

    def __str__(self):  
        return f"TestSession of {self.user} on {self.start_time}"

    @property
    def duration(self):
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60.0  # Duration in minutes
        return None

    def generate_questions(self):
        questions = []
        selected_subjects = list(self.subjects.all())
        english_subject = Subject.objects.get(name="English")
        if english_subject not in selected_subjects:
            selected_subjects.append(english_subject)

        for subject in selected_subjects:
            worksheets = list(subject.get_worksheets())
            if not worksheets:
                continue
            
            selected_worksheet = sample(worksheets, 1)[0]
            worksheet_questions = list(selected_worksheet.get_questions())
            questions.extend(worksheet_questions)

        self.testsessionquestion_set.all().delete()
        self.user_responses.all().delete()

        TestSessionQuestion.objects.bulk_create([
            TestSessionQuestion(test_session=self, question=question)
            for question in questions
        ])

        UserResponse.objects.bulk_create([
            UserResponse(user=self.user, question=question, test_session=self)
            for question in questions
        ])

        return questions

class TestSessionQuestion(models.Model):
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('test_session', 'question')

class UserResponse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=Question.OPTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='user_responses')
    is_correct = models.BooleanField(default=False)  

    def __str__(self):
        return f"Response by {self.user.username} for question {self.question.id}"

    def save(self, *args, **kwargs):
        self.is_correct = self.selected_option == self.question.correct_option
        super().save(*args, **kwargs)

class Result(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    worksheet = models.ForeignKey(Worksheet, on_delete=models.CASCADE)
    score = models.FloatField()
    speed = models.FloatField()  # in seconds
    timestamp = models.DateTimeField(auto_now_add=True)
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='session_results')

    def __str__(self):
        return f"Result for {self.user.username} in {self.subject.name} - {self.worksheet.name}"

    def calculate_score(self):
        user_responses = self.test_session.user_responses.filter(question__worksheet__subject=self.subject)
        correct_responses_count = user_responses.filter(is_correct=True).count()
        total_questions = user_responses.count()
        self.score = (correct_responses_count / total_questions) * 100 if total_questions > 0 else 0
        self.save()

    def calculate_speed(self):
        total_responses = self.test_session.user_responses.count()
        self.speed = (self.test_session.duration * 60) / total_responses if total_responses > 0 else 0
        self.save()

    def get_failed_questions(self):
        return self.test_session.user_responses.filter(
            question__worksheet__subject=self.subject,
            is_correct=False
        )