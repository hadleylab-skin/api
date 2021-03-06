from apps.accounts.factories import DoctorFactory, CoordinatorFactory, \
    SiteFactory, PatientFactory
from apps.accounts.models import SiteJoinRequest, JoinStateEnum
from apps.main.tests import APITestCase
from apps.moles.factories.study import StudyFactory
from apps.moles.factories.study_invitation import StudyInvitationFactory


class DoctorViewSetTest(APITestCase):
    def setUp(self):
        super(DoctorViewSetTest, self).setUp()
        self.other_doctor = DoctorFactory.create()
        self.coordinator = DoctorFactory.create()
        self.coordinator_ptr = CoordinatorFactory.create(
            doctor_ptr=self.coordinator)

    def test_forbidden_unauthorized(self):
        resp = self.client.get('/api/v1/doctor/')
        self.assertUnauthorized(resp)

    def test_forbidden_doctor(self):
        self.authenticate_as_doctor()
        resp = self.client.get('/api/v1/doctor/')
        self.assertForbidden(resp)

    def test_list_coordinator(self):
        self.authenticate_as_doctor(self.coordinator)
        resp = self.client.get('/api/v1/doctor/')
        self.assertSuccessResponse(resp)
        self.assertEqual(len(resp.data), 3)
        self.assertSetEqual(
            set([item['pk'] for item in resp.data]),
            {self.doctor.pk, self.other_doctor.pk, self.coordinator.pk}
        )

    def test_public_keys(self):
        self.other_doctor.public_key = 'public_key_value'
        self.other_doctor.save()

        self.authenticate_as_doctor(self.coordinator)
        resp = self.client.get(
            '/api/v1/doctor/public_keys/?doctors={0}'.format(
                self.other_doctor.pk))
        self.assertSuccessResponse(resp)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['public_key'], 'public_key_value')

    def test_list_with_sites(self):
        site = SiteFactory.create(site_coordinator=self.coordinator_ptr)
        SiteJoinRequest.objects.create(
            doctor=self.other_doctor,
            site=site)
        SiteJoinRequest.objects.create(
            doctor=self.doctor,
            site=site,
            state=JoinStateEnum.CONFIRMED)
        self.authenticate_as_doctor(self.coordinator)
        resp = self.client.get('/api/v1/doctor/')
        self.assertSuccessResponse(resp)

        for doctor in resp.data:
            if doctor['pk'] == self.other_doctor.pk:
                self.assertListEqual(doctor['sites'], [])

            if doctor['pk'] == self.doctor.pk:
                self.assertListEqual(doctor['sites'], [site.pk])

    def test_get_by_email_forbidden(self):
        resp = self.client.get(
            '/api/v1/doctor/get_by_email/?email={0}'.format(self.doctor.email))
        self.assertUnauthorized(resp)

    def test_get_by_email_success(self):
        self.authenticate_as_doctor()
        resp = self.client.get(
            '/api/v1/doctor/get_by_email/?email={0}'.format(self.doctor.email))
        self.assertSuccessResponse(resp)
        self.assertEqual(self.doctor.pk, resp.data['pk'])

    def test_get_by_email_not_exists(self):
        self.authenticate_as_doctor()
        resp = self.client.get(
            '/api/v1/doctor/get_by_email/?email=not-existing-email@mail.ru')
        self.assertSuccessResponse(resp)
        self.assertDictEqual(resp.data, {})

    def test_get_by_email_for_exists_patient(self):
        self.authenticate_as_doctor()
        study = StudyFactory.create()
        patient = PatientFactory.create(doctor=self.doctor)
        StudyInvitationFactory.create(
            email='123@mail.ru',
            doctor=self.doctor,
            study=study,
            patient=patient)
        resp = self.client.get(
            '/api/v1/doctor/get_by_email/?email=123@mail.ru')
        self.assertBadRequest(resp)
