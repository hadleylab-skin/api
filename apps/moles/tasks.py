import requests

from celery import shared_task
from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from apps.accounts.models import Doctor
from .models import MoleImage, Study
from .models.study import ParticipantNotificationDocConsentUpdate, \
    DoctorNotificationDocConsentUpdate


class GetPredictionError(Exception):
    pass


@shared_task
def get_mole_image_prediction(pk):
    mole_image = MoleImage.objects.get(pk=pk)

    payload = {
        'image_url': mole_image.photo.url,
    }
    url = 'http://52.36.205.204/mole_classifier_url'
    r = requests.post(url, json=payload)

    if r.json()['status'] == 'success':
        mole_image.prediction = r.json()['prediction']
        mole_image.prediction_accuracy = Decimal(r.json()['probability'])
        mole_image.save()
    else:
        raise GetPredictionError(r)


def get_study_context(study):
    return {
        'study_title': study.title,
        'study_date_of_change': timezone.now().strftime('%m/%d/%Y %H:%M'),
        'study_coordinator': study.author.doctor_ptr.get_full_name(),
        'study_coordinator_email': study.author.doctor_ptr.email
    }


@shared_task
def send_participant_consent_changed(study_pk, participant_pk):
    study = Study.objects.get(pk=study_pk)
    participant = Doctor.objects.get(pk=participant_pk)

    consent_docs_urls = []
    for doc in study.consent_docs.all():
        url = doc.file.url
        if not url.startswith('http'):  # pragma: no cover
            # no cover, because we don't use S3 in tests, and aways true here
            url = '{0}://{1}{2}'.format(
                settings.PROTOCOL,
                settings.DOMAIN,
                url)
        consent_docs_urls.append(url)

    context = get_study_context(study)
    context['consent_docs_urls'] = consent_docs_urls

    ParticipantNotificationDocConsentUpdate(
        context=context).send([participant.email])


@shared_task
def send_doctor_consent_changed(study_pk, doctor_pk):
    study = Study.objects.get(pk=study_pk)
    doctor = Doctor.objects.get(pk=doctor_pk)

    context = get_study_context(study)
    context.update({'user_full_name': doctor.get_full_name()})
    DoctorNotificationDocConsentUpdate(context=context).send([doctor.email])
