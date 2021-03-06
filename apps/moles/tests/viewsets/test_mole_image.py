from datetime import timedelta

from django.utils import timezone

from apps.main.tests import patch
from apps.accounts.factories import CoordinatorFactory
from apps.moles.factories.study import StudyFactory
from ...factories import MoleImageFactory
from ...models import MoleImage
from ..moles_test_case import MolesTestCase


class MoleImageViewSetTest(MolesTestCase):
    def get_url(self, patient_pk, mole_pk, mole_image_pk=None):
        url = '/api/v1/patient/{0}/mole/{1}/image/'.format(
            patient_pk, mole_pk)

        if mole_image_pk:
            url += '{0}/'.format(mole_image_pk)

        return url

    def test_get_patient_mole_images_success(self):
        self.authenticate_as_doctor()

        first_patient_mole_image = MoleImageFactory.create(
            mole=self.first_patient_mole)
        resp = self.client.get(
            self.get_url(self.first_patient.pk, self.first_patient_mole.pk))
        self.assertSuccessResponse(resp)

        data = resp.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['pk'], first_patient_mole_image.pk)

    def test_get_patient_mole_images_forbidden_for_not_own_patient(self):
        self.authenticate_as_doctor()

        resp = self.client.get(
            self.get_url(self.another_patient.pk, self.another_patient_mole.pk))
        self.assertForbidden(resp)

    def test_get_patient_mole_images_forbidden_for_unauthorized(self):
        resp = self.client.get(
            self.get_url(self.another_patient.pk, self.another_patient_mole.pk))
        self.assertUnauthorized(resp)

    @patch('apps.moles.tasks.requests')
    def test_create_success(self, mock_requests):
        self.authenticate_as_doctor()

        mole_image_data = {
            'photo': self.get_sample_image_file(),
        }

        with self.fake_media():
            resp = self.client.post(
                self.get_url(self.first_patient.pk, self.first_patient_mole.pk),
                mole_image_data)
        self.assertSuccessResponse(resp)

        data = resp.data
        self.assertIsNotNone(data['pk'])

        mole_image = MoleImage.objects.get(pk=data['pk'])
        self.assertEqual(mole_image.mole, self.first_patient_mole)

        mole = mole_image.mole
        self.assertTrue(mole_image.photo.name.startswith(
            'patients/{0}/skin_images/{1}/{1}_photo'.format(
                mole.patient.pk, mole.pk)))

    def test_create_forbidden_for_patient_without_valid_consent(self):
        self.authenticate_as_doctor()
        self.first_patient_consent.delete()
        resp = self.client.post(
            self.get_url(self.first_patient.pk, self.first_patient_mole.pk))
        self.assertForbidden(resp)

    @patch('apps.moles.tasks.requests')
    def test_create_with_study(self, mock_requests):
        self.authenticate_as_doctor()
        study = StudyFactory.create()

        mole_image_data = {
            'photo': self.get_sample_image_file(),
            'study': study.pk,
        }

        with self.fake_media():
            resp = self.client.post(
                self.get_url(self.first_patient.pk, self.first_patient_mole.pk),
                mole_image_data)
        self.assertSuccessResponse(resp)

        data = resp.data
        mole_image = MoleImage.objects.get(pk=data['pk'])
        self.assertEqual(mole_image.study.pk, study.pk)

    @patch('apps.moles.tasks.requests')
    def test_create_with_study_outdated_consent(self, mock_requests):
        self.authenticate_as_doctor()
        study = StudyFactory.create()

        mole_image_data = {
            'photo': self.get_sample_image_file(),
            'study': study.pk,
        }

        self.first_patient_consent.date_expired = \
            timezone.now() - timedelta(days=1)
        self.first_patient_consent.save()

        with self.fake_media():
            resp = self.client.post(
                self.get_url(self.first_patient.pk, self.first_patient_mole.pk),
                mole_image_data)
        self.assertForbidden(resp)

    @patch('apps.moles.tasks.requests')
    def test_update_success(self, mock_requests):
        self.authenticate_as_doctor()

        yesterday_date = timezone.now() - timedelta(days=1)
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = yesterday_date
            mole_image = MoleImageFactory.create(
                mole=self.first_patient_mole)
        self.assertEqual(mole_image.date_modified, yesterday_date)

        mole_image_data = {
            'biopsy': True,
            'biopsy_data': '{"lens": 1}',
            'clinical_diagnosis': 'clinical_diagnosis',
            'path_diagnosis': 'path_diagnosis',
        }

        resp = self.client.patch(
            self.get_url(
                self.first_patient.pk, self.first_patient_mole.pk,
                mole_image.pk),
            mole_image_data)
        self.assertSuccessResponse(resp)

        mole_image.refresh_from_db()
        self.assertEqual(mole_image.biopsy, mole_image_data['biopsy'])
        # self.assertEqual(mole_image.biopsy_data, mole_image_data['biopsy_data'])
        # biopsy can bee eiter string or object so we have separated tests for this cases
        self.assertEqual(mole_image.clinical_diagnosis,
                         mole_image_data['clinical_diagnosis'])
        self.assertEqual(mole_image.path_diagnosis,
                         mole_image_data['path_diagnosis'])
        self.assertNotEqual(mole_image.date_modified, yesterday_date)

    @patch('apps.moles.tasks.requests')
    def test_update_biopsy_data_as_string_success(self, mock_requests):
        self.authenticate_as_doctor()
        mole_image = MoleImageFactory.create(
            mole=self.first_patient_mole)
        mole_image_data = {
            'biopsy_data': '{"lens": 1}',
        }
        resp = self.client.patch(
            self.get_url(
                self.first_patient.pk, self.first_patient_mole.pk,
                mole_image.pk),
            mole_image_data)
        self.assertSuccessResponse(resp)
        mole_image.refresh_from_db()
        self.assertDictEqual({'lens': 1}, mole_image.biopsy_data)

    @patch('apps.moles.tasks.requests')
    def test_update_biopsy_data_as_dict_success(self, mock_requests):
        self.authenticate_as_doctor()
        mole_image = MoleImageFactory.create(
            mole=self.first_patient_mole)
        mole_image_data = {
            'biopsy_data': {'lens': 1},
        }
        resp = self.client.patch(
            self.get_url(
                self.first_patient.pk, self.first_patient_mole.pk,
                mole_image.pk),
            mole_image_data,
            format='json')
        self.assertSuccessResponse(resp)
        mole_image.refresh_from_db()
        self.assertDictEqual({'lens': 1}, mole_image.biopsy_data)

    @patch('apps.moles.tasks.requests')
    def test_update_allow_for_patient_without_valid_consent(
            self, mock_requests):
        self.authenticate_as_doctor()

        mole_image = MoleImageFactory.create(
            mole=self.first_patient_mole)

        self.first_patient_consent.delete()
        resp = self.client.patch(
            self.get_url(self.first_patient.pk, self.first_patient_mole.pk,
                         mole_image.pk))
        self.assertSuccessResponse(resp)

    def test_delete_not_allowed(self):
        self.authenticate_as_doctor()

        first_patient_mole_image = MoleImageFactory.create(
            mole=self.first_patient_mole)
        resp = self.client.delete(self.get_url(
            self.first_patient.pk,
            self.first_patient_mole.pk,
            first_patient_mole_image.pk))
        self.assertNotAllowed(resp)

    @patch('apps.moles.tasks.requests')
    def test_that_doctor_cant_change_approved_field(self, mock_requests):
        mole_image = MoleImageFactory.create(
            approved=False,
            mole=self.first_patient_mole)

        mole_image_data = {
            'approved': True,
        }

        self.authenticate_as_doctor()
        resp = self.client.patch(
            self.get_url(
                self.first_patient.pk, self.first_patient_mole.pk,
                mole_image.pk),
            mole_image_data)
        self.assertBadRequest(resp)

    @patch('apps.moles.tasks.requests')
    def test_that_coordinator_can_change_approved_field(self, mock_requests):
        mole_image = MoleImageFactory.create(
            approved=False,
            mole=self.first_patient_mole)

        mole_image_data = {
            'approved': True,
        }

        CoordinatorFactory.create(doctor_ptr=self.doctor)

        self.authenticate_as_doctor()
        resp = self.client.patch(
            self.get_url(
                self.first_patient.pk, self.first_patient_mole.pk,
                mole_image.pk),
            mole_image_data)
        self.assertSuccessResponse(resp)

        mole_image.refresh_from_db()
        self.assertTrue(mole_image.approved)
