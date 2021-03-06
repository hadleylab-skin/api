from skin.utils import generate_filename


def distant_photo_path(instance, filename):
    anatomical_site = instance.anatomical_site
    patient = instance.patient

    new_filename = generate_filename(
        filename,
        prefix='{0}_{1}_regional_photo'.format(
            instance.pk, anatomical_site.pk))

    return '/'.join([
        'patients', str(patient.pk),
        'anatomical_sites', str(instance.pk),
        'regional_photo', new_filename,
    ])


def mole_image_photo_path(instance, filename):
    mole_image = instance
    mole = mole_image.mole
    patient = mole.patient

    new_filename = generate_filename(
        filename,
        prefix='{0}_photo'.format(mole.pk))

    return '/'.join([
        'patients', str(patient.pk),
        'skin_images', str(mole.pk), new_filename,
    ])


def study_consent_docs_path(instance, filename):
    instance.original_filename = filename

    new_filename = generate_filename(
        filename,
        prefix='doc')

    return '/'.join([
        'study_consent_docs', new_filename
    ])
