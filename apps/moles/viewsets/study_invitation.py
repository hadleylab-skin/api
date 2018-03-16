from rest_framework import viewsets, mixins
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.accounts.models import DoctorToPatient, PatientConsent
from apps.accounts.permissions.is_partipicant import IsParticipant
from ..models import StudyInvitation, StudyInvitationStatus, StudyToPatient
from ..serializers import StudyInvitationSerializer


class StudyInvitationViewSet(viewsets.GenericViewSet,
                             mixins.ListModelMixin):
    queryset = StudyInvitation.objects.all()
    serializer_class = StudyInvitationSerializer
    permission_classes = (IsParticipant,)

    def get_queryset(self):
        qs = super(StudyInvitationViewSet, self).get_queryset()
        return qs.filter(
            email=self.request.user.doctor_role__email,
            status=StudyInvitationStatus.NEW)

    @detail_route(methods=['POST'])
    def approve(self, request, pk):
        invitation = self.get_object()
        invitation.status = StudyInvitationStatus.ACCEPTED
        invitation.save(update_fields=['status'])

        encryption_keys = self.request.data['encryption_keys']
        doctor = invitation.doctor
        if str(doctor.pk) not in encryption_keys:
            raise ValidationError(
                'You doesn\'t not pass encryption key of doctor')

        patient_consent = PatientConsent.objects.get(
            pk=self.request.data['consent_pk'])
        patient = DoctorToPatient.objects.get(
            doctor=self.request.user.doctor_role
        ).patient
        if patient_consent.patient != patient:
            raise ValidationError(
                'Patient in consent does not match request patient')

        DoctorToPatient.objects.update_or_create(
            doctor=doctor,
            patient=patient,
            defaults={'encrypted_key': encryption_keys[str(doctor.pk)]})

        StudyToPatient.objects.create(
            study=invitation.study,
            patient=patient,
            patient_consent=patient_consent)

        return Response(StudyInvitationSerializer(instance=invitation).data)

    @detail_route(methods=['POST'])
    def decline(self, request, pk):
        invitation = self.get_object()
        invitation.status = StudyInvitationStatus.DECLINED
        invitation.save(update_fields=['status'])

        return Response(StudyInvitationSerializer(instance=invitation).data)
