from rest_framework import serializers
from .models import Subject, UserSubjectPreference,TestSession, Result, Question, UserResponse

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']

class UserSubjectPreferenceSerializer(serializers.ModelSerializer):
    selected_subjects = SubjectSerializer(many=True)

    class Meta:
        model = UserSubjectPreference
        fields = ['selected_subjects']

    def validate_selected_subjects(self, value):
        if len(value) != 5:
            raise serializers.ValidationError("You must select exactly 5 subjects.")
        subject_names = [subject.name for subject in value]
        if "English" not in subject_names:
            raise serializers.ValidationError("English is a compulsory subject.")
        return value
    
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'image']


class TestSessionSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = TestSession
        fields = ['id', 'start_time', 'end_time', 'score', 'completed', 'questions']

    def get_questions(self, obj):
        user_responses = UserResponse.objects.filter(test_session=obj)
        return QuestionSerializer([response.question for response in user_responses], many=True).data


class UserResponseSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(write_only=True)
    selected_option = serializers.ChoiceField(choices=Question.OPTION_CHOICES)

    class Meta:
        model = UserResponse
        fields = ['question_id', 'selected_option']

    def validate_question_id(self, value):
        """
        Validate that the question ID exists.
        """
        try:
            question = Question.objects.get(id=value)
        except Question.DoesNotExist:
            raise serializers.ValidationError("Invalid question ID.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        test_session = self.context['test_session']

        question_id = validated_data.get('question_id')
        selected_option = validated_data.get('selected_option')

        user_response, created = UserResponse.objects.update_or_create(
            user=user,
            question_id=question_id,
            test_session=test_session,
            defaults={'selected_option': selected_option}
        )

        return user_response


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'subject', 'worksheet', 'score', 'speed', 'timestamp']
