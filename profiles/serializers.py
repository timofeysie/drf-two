from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Profile
        # to list all fields all in an array or set to '__all__'  
        fields = [
            'id', 'owner', 'created_at', 'updated_at', 'name',
            'content', 'image'
        ]