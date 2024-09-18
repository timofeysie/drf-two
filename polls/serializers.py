from rest_framework import serializers
from .models import Question, Answer, Vote


class VoteSerializer(serializers.ModelSerializer):
    """
    Serializer for the Vote model. It handles serialization for creating and
    listing votes. Ensures that a user cannot vote more than once per question
    by implementing custom validation.
    """
    class Meta:
        model = Vote
        fields = ['id', 'answer', 'voter', 'created_at']
        read_only_fields = ('voter',)

    def validate(self, data):
        """
        Validate that the user has not already voted for the same question.
        Raises a ValidationError if the user has already voted.
        """
        question = data['answer'].question
        voter = self.context['request'].user
        if Vote.objects.filter(answer__question=question,
                               voter=voter).exists():
            raise serializers.ValidationError(
                "You have already voted on this question.")
        return data

    def save(self, **kwargs):
        kwargs['voter'] = self.context['request'].user
        return super().save(**kwargs)


class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Answer model. Includes a custom method to count votes,
    which is included in the serialization output.
    """
    text = serializers.CharField(required=True, allow_blank=False, error_messages={"blank": "This field may not be left blank."})
    votes_count = serializers.SerializerMethodField()

    def get_votes_count(self, obj):
        return obj.votes.distinct().count()

    class Meta:
        model = Answer
        fields = ['id', 'text', 'created_at', 'votes_count']


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Question model. Handles serialization for creating
    and listing questions. Includes nested AnswerSerializers to represent
    answers associated with the question, and custom methods to handle
    the creation of answers within the same request as a question.
    """
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    owner_username = serializers.ReadOnlyField(source='owner.username')
    votes_count = serializers.IntegerField(read_only=True)
    answers = AnswerSerializer(many=True, required=True)

    def validate_answers(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("At least two answers are required.")
        return value

    class Meta:
        model = Question
        fields = [
            'id', 'owner', 'owner_username', 'text',
            'created_at', 'answers', 'votes_count'
            ]

    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        question = Question.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        return question
