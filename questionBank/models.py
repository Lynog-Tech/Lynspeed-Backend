from django.db import models
from django.conf import settings
from random import sample, shuffle
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
# import logging
# logger = logging.getLogger(__name__)


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    def get_worksheets(self):
        return self.worksheets.all()

    def get_questions(self):
        questions = []
        for worksheet in self.get_worksheets():
            questions.extend(worksheet.get_questions())
        return questions


class UserSubjectPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subject_preference')
    selected_subjects = models.ManyToManyField(Subject, related_name='user_preferences')
    
    def save(self, *args, **kwargs):
        # Ensure English is always in the selected subjects
        english_subject = Subject.objects.get(name="English")
        if not self.selected_subjects.filter(name="English").exists():
            self.selected_subjects.add(english_subject)
        if self.selected_subjects.count() > 5:
            raise ValueError("You can only select up to 5 subjects including English.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s subject preferences"

    def get_available_test_subjects(self):
        # Always include English and allow user to swap one subject
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
    correct_option = models.CharField(max_length=25, choices=OPTION_CHOICES)
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

    def get_correct_answer(self):
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
        """
        Randomly select one worksheet from each selected subject and fetch all questions available in that worksheet.
        The order of questions in each worksheet is preserved.
        """
        questions = []
        selected_subjects = list(self.subjects.all())

        # Ensure English is in the selected subjects
        english_subject = Subject.objects.get(name="English")
        if english_subject not in selected_subjects:
            selected_subjects.append(english_subject)

        for subject in selected_subjects:
            # Get all worksheets for the subject
            worksheets = list(subject.get_worksheets())
            
            # Ensure there are worksheets available
            if not worksheets:
                continue
            
            # Randomly select one worksheet
            selected_worksheet = sample(worksheets, 1)[0]
            
            # Fetch all questions from the selected worksheet (preserving the order)
            worksheet_questions = list(selected_worksheet.get_questions())
            
            # Add questions to the list
            questions.extend(worksheet_questions)

        # # Log assigned questions
        # logger.info(f"Assigned questions for test session {self.id}: {[q.id for q in questions]}")

        # Clear existing TestSessionQuestion entries for this session
        TestSessionQuestion.objects.filter(test_session=self).delete()

        # Create TestSessionQuestion entries for the questions
        for question in questions:
            TestSessionQuestion.objects.create(test_session=self, question=question)

        # Clear any existing UserResponse entries for this session
        UserResponse.objects.filter(test_session=self).delete()

        # Create UserResponse entries for the questions
        for question in questions:
            UserResponse.objects.create(user=self.user, question=question, test_session=self)

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
        return f"Response by {self.user.full_name} for question {self.question.id}"

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
    def __str__(self):
        return f"Result for {self.user.username} in {self.subject.name} - {self.worksheet.name}"

    def calculate_score(self):
        # Get all user responses for the subject
        user_responses = self.test_session.user_responses.filter(question__worksheet__subject=self.subject)
        
        # Count correct responses
        correct_responses_count = user_responses.filter(is_correct=True).count()
    
        # Total questions
        total_questions = user_responses.count()
        
        # Calculate score as a percentage
        self.score = (correct_responses_count / total_questions) * 100 if total_questions > 0 else 0
        self.save()

    def calculate_speed(self):
        total_responses = self.test_session.user_responses.count()
        self.speed = (self.test_session.duration * 60) / total_responses if total_responses > 0 else 0  # Convert duration to seconds
        self.save()

    def get_failed_questions(self):
        failed_responses = self.test_session.user_responses.filter(
            question__worksheet__subject=self.subject,
            is_correct=False
        )
        return failed_responses
        

@receiver(post_save, sender=Subject)
@receiver(post_save, sender=Worksheet)
@receiver(post_save, sender=Question)
@receiver(post_delete, sender=Subject)
@receiver(post_delete, sender=Worksheet)
@receiver(post_delete, sender=Question)
def invalidate_cache(sender, **kwargs):
    """
    Clear the cache when a Subject, Worksheet, or Question is saved or deleted.
    """
    cache.clear()