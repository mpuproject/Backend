from rest_framework import serializers
from .models import Question, Answer
from user.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']

class AnswerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Answer
        fields = ['answer_id', 'user', 'content', 'created_time']
        read_only_fields = ['answer_id', 'created_time']

class QuestionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    answers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['question_id', 'user', 'content', 'created_time', 'answers', 'answers_count']
        read_only_fields = ['question_id', 'created_time']
    
    def get_answers_count(self, obj):
        return obj.answers.count() 