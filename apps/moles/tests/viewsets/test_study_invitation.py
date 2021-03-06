import json

from apps.accounts.factories import PatientConsentFactory, CoordinatorFactory
from apps.main.tests import APITestCase
from apps.moles.factories.study import StudyFactory
from apps.moles.models import StudyToPatient
from apps.moles.models.study_invitation import StudyInvitation, \
    StudyInvitationStatus
from apps.accounts.models import DoctorToPatient, SexEnum, RaceEnum
from apps.accounts.factories.doctor import DoctorFactory
from apps.accounts.factories.participant import ParticipantFactory
from apps.accounts.factories.patient import PatientFactory
from apps.moles.factories.study_invitation import StudyInvitationFactory


class StudyInvitationViewSetTest(APITestCase):
    def test_permission(self):
        resp = self.client.get('/api/v1/study/invites/')
        self.assertUnauthorized(resp)
        self.authenticate_as_doctor()
        resp = self.client.get('/api/v1/study/invites/')
        self.assertForbidden(resp)

    def test_list(self):
        StudyInvitationFactory.create()
        StudyInvitationFactory.create()
        self.assertEqual(len(StudyInvitation.objects.all()), 2)

    def test_approve(self):
        coordinator = DoctorFactory.create()
        coordinator_ptr = CoordinatorFactory.create(doctor_ptr=coordinator)
        doctor = DoctorFactory.create(my_coordinator=coordinator_ptr)
        participant = DoctorFactory.create()
        ParticipantFactory.create(doctor_ptr=participant)
        patient = PatientFactory.create(doctor=participant)
        study = StudyFactory.create()
        study_invitation = StudyInvitationFactory.create(
            study=study,
            email=participant.email,
            doctor=doctor)
        self.authenticate_as_doctor(doctor=participant)
        consent = PatientConsentFactory.create(patient=patient)
        resp = self.client.post(
            '/api/v1/study/invites/{0}/approve/'.format(study_invitation.pk), {
                'doctor_encryption_key': 'qwertyuiop',
                'coordinator_encryption_key': 'iqwjgipwqjeg',
                'consent_pk': consent.pk
            },
            format='json')
        self.assertSuccessResponse(resp)
        study.refresh_from_db()
        study_invitation.refresh_from_db()
        self.assertEqual(study_invitation.status,
                         StudyInvitationStatus.ACCEPTED)

        doc_to_patient = DoctorToPatient.objects.get(
            doctor=doctor,
            patient=patient)
        self.assertEqual(doc_to_patient.encrypted_key, 'qwertyuiop')

        coordinator_to_patient = DoctorToPatient.objects.get(
            doctor=coordinator,
            patient=patient)
        self.assertEqual(coordinator_to_patient.encrypted_key, 'iqwjgipwqjeg')

        study_to_patient = StudyToPatient.objects.get(
            study=study,
            patient=patient
        )
        self.assertEqual(study_to_patient.patient_consent.pk, consent.pk)
        self.assertListEqual(list(study.patients.all()), [patient])

    def test_approve_without_coordinator(self):
        coordinator = DoctorFactory.create()
        coordinator_ptr = CoordinatorFactory.create(doctor_ptr=coordinator)
        doctor = DoctorFactory.create(my_coordinator=coordinator_ptr)
        participant = DoctorFactory.create()
        ParticipantFactory.create(doctor_ptr=participant)
        patient = PatientFactory.create(doctor=participant)
        study = StudyFactory.create()
        study_invitation = StudyInvitationFactory.create(
            study=study,
            email=participant.email,
            doctor=doctor)
        self.authenticate_as_doctor(doctor=participant)
        consent = PatientConsentFactory.create(patient=patient)
        resp = self.client.post(
            '/api/v1/study/invites/{0}/approve/'.format(study_invitation.pk), {
                'doctor_encryption_key': 'qwertyuiop',
                'consent_pk': consent.pk
            },
            format='json')
        self.assertSuccessResponse(resp)
        study.refresh_from_db()
        study_invitation.refresh_from_db()
        self.assertEqual(study_invitation.status,
                         StudyInvitationStatus.ACCEPTED)

    def test_approve_with_invalid_id(self):
        doctor = DoctorFactory.create()
        participant = DoctorFactory.create()
        ParticipantFactory.create(doctor_ptr=participant)
        PatientFactory.create(doctor=participant)
        study_invitation = StudyInvitationFactory.create(
            email=participant.email,
            doctor=doctor)
        consent = PatientConsentFactory.create()
        self.authenticate_as_doctor(doctor=participant)
        resp = self.client.post(
            '/api/v1/study/invites/{0}/approve/'.format(study_invitation.pk), {
                'doctor_encryption_key': 'qwertyuiop',
                'consent_pk': consent.pk
            },
            format='json')
        self.assertBadRequest(resp)

    def test_approve_invalid_consent(self):
        doctor = DoctorFactory.create()
        participant = DoctorFactory.create()
        ParticipantFactory.create(doctor_ptr=participant)
        PatientFactory.create(doctor=participant)
        study = StudyFactory.create()
        study_invitation = StudyInvitationFactory.create(
            study=study,
            email=participant.email,
            doctor=doctor)
        self.authenticate_as_doctor(doctor=participant)
        consent = PatientConsentFactory.create()
        resp = self.client.post(
            '/api/v1/study/invites/{0}/approve/'.format(study_invitation.pk), {
                'doctor_encryption_key': 'qwertyuiop',
                'consent_pk': consent.pk
            },
            format='json')
        self.assertBadRequest(resp)

    def test_decline(self):
        doctor = DoctorFactory.create()
        participant = DoctorFactory.create()
        ParticipantFactory.create(doctor_ptr=participant)
        study_invitation = StudyInvitationFactory.create(
            email=participant.email,
            doctor=doctor)
        self.authenticate_as_doctor(doctor=participant)
        resp = self.client.post('/api/v1/study/invites/{0}/decline/'
                                .format(study_invitation.pk),
                                format='json')
        self.assertSuccessResponse(resp)
        self.assertEqual(StudyInvitation.objects.all().first().status,
                         StudyInvitationStatus.DECLINED)


class StudyInvitationForDoctorViewSetTest(APITestCase):
    def setUp(self):
        super(StudyInvitationForDoctorViewSetTest, self).setUp()

        doctor = DoctorFactory.create()
        self.study = StudyFactory.create()
        self.patient = PatientFactory.create(doctor=self.doctor)
        self.participant = DoctorFactory.create(
            email='123@mail.ru',
            public_key='public_key_123')
        ParticipantFactory.create(doctor_ptr=self.participant)
        self.invitation = StudyInvitationFactory.create(
            email='123@mail.ru',
            doctor=self.doctor,
            study=self.study,
            patient=self.patient)
        StudyInvitationFactory.create(
            email='456@mail.ru',
            doctor=self.doctor,
            study=self.study)
        StudyInvitationFactory.create(
            email='789@mail.ru',
            doctor=doctor,
            study=self.study)

    def test_permission(self):
        resp = self.client.get('/api/v1/study/invites_doctor/')
        self.assertUnauthorized(resp)
        participant = DoctorFactory.create()
        ParticipantFactory.create(doctor_ptr=participant)
        self.authenticate_as_doctor(doctor=participant)
        resp = self.client.get('/api/v1/study/invites_doctor/')
        self.assertForbidden(resp)

    def test_list_success(self):
        self.authenticate_as_doctor()
        resp = self.client.get('/api/v1/study/invites_doctor/')
        self.assertSuccessResponse(resp)
        self.assertEqual(len(resp.data), 1)

        item = resp.data[0]
        self.assertEqual(item['pk'], self.invitation.pk)
        self.assertEqual(item['email'], '123@mail.ru')
        self.assertEqual(item['study']['pk'], self.study.pk)
        self.assertEqual(item['participant']['pk'], self.participant.pk)
        self.assertEqual(item['participant']['public_key'], 'public_key_123')

    def test_list_without_participant(self):
        patient = PatientFactory.create(doctor=self.doctor)
        new_invitation = StudyInvitationFactory.create(
            email='777@mail.ru',
            doctor=self.doctor,
            study=self.study,
            patient=patient)
        self.authenticate_as_doctor()
        resp = self.client.get('/api/v1/study/invites_doctor/')
        self.assertSuccessResponse(resp)
        self.assertEqual(len(resp.data), 2)
        self.assertSetEqual(
            {self.invitation.pk, new_invitation.pk},
            set([item['pk'] for item in resp.data]))

        item = next(item for item in resp.data
                    if item['pk'] == new_invitation.pk)
        self.assertIsNone(item['participant'])

    def test_decline(self):
        self.authenticate_as_doctor()
        resp = self.client.post(
            '/api/v1/study/invites_doctor/{0}/decline/'.format(
                self.invitation.pk))
        self.assertSuccessResponse(resp)

        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, StudyInvitationStatus.DECLINED)

    def test_approve(self):
        self.authenticate_as_doctor()
        self.assertFalse(DoctorToPatient.objects.filter(
            doctor=self.participant,
            patient=self.patient).exists())

        patient_data = {
            'encryption_keys': json.dumps({
                self.doctor.pk: 'some new key',
                self.participant.pk: 'participant_key'
            }),
        }

        with self.fake_media():
            resp = self.client.post(
                '/api/v1/study/invites_doctor/{0}/approve/'.format(
                    self.invitation.pk),
                patient_data)

        self.assertSuccessResponse(resp)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, StudyInvitationStatus.ACCEPTED)

        self.assertTrue(DoctorToPatient.objects.filter(
            doctor=self.participant,
            patient=self.patient).exists())

    def test_create(self):
        self.authenticate_as_doctor()
        resp = self.client.post(
            '/api/v1/study/invites_doctor/', {
                'email': 'pro@pro.com',
                'study': self.study.pk
            })
        self.assertSuccessResponse(resp)
        invite = StudyInvitation.objects.get(email='pro@pro.com')

        self.assertEqual(invite.status, StudyInvitationStatus.NEW)

    def test_create_duplicate_fail(self):
        self.authenticate_as_doctor()
        resp = self.client.post(
            '/api/v1/study/invites_doctor/', {
                'email': 'pro@pro.com',
                'study': self.study.pk
            })
        self.assertSuccessResponse(resp)

        resp = self.client.post(
            '/api/v1/study/invites_doctor/', {
                'email': 'pro@pro.com',
                'study': self.study.pk
            })
        self.assertBadRequest(resp)
