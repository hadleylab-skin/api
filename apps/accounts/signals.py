from django.db.models.signals import post_save
from django.dispatch import receiver
from versatileimagefield.image_warmer import VersatileImageFieldWarmer

from .models import Patient, Doctor


@receiver(post_save, sender=Patient)
@receiver(post_save, sender=Doctor)
def warm_patient_photo(sender, instance, **kwargs):
    """Crop and create photos"""
    VersatileImageFieldWarmer(
        instance_or_queryset=instance,
        rendition_key_set='main_set',
        image_attr='photo').warm()