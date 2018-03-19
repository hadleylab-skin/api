from rest_framework import serializers

from apps.accounts.serializers import DoctorSerializer
from ..models import ConsentDoc, Study


class ConsentDocSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = ConsentDoc
        fields = ('pk', 'file', 'thumbnail', 'attachment_name')


class StudyBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = ('pk', 'title', 'consent_docs')


class StudyListSerializer(serializers.ModelSerializer):
    consent_docs = ConsentDocSerializer(many=True)
    doctors = DoctorSerializer(many=True)

    class Meta(StudyBaseSerializer.Meta):
        fields = ('pk', 'title', 'doctors', 'patients', 'consent_docs')
