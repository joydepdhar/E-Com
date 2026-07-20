import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Payment


payment_logger = logging.getLogger('store.payments')


@receiver(pre_save, sender=Payment)
def remember_previous_payment_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_status = None
        return

    instance._previous_status = sender.objects.filter(
        pk=instance.pk
    ).values_list('status', flat=True).first()


@receiver(post_save, sender=Payment)
def log_payment_terminal_status(sender, instance, created, **kwargs):
    previous_status = getattr(instance, '_previous_status', None)
    if previous_status == instance.status:
        return

    if instance.status == Payment.Status.SUCCESSFUL:
        payment_logger.info(
            'payment_success order_id=%s payment_id=%s',
            instance.order_id,
            instance.id,
        )
    elif instance.status == Payment.Status.FAILED:
        payment_logger.warning(
            'payment_failure order_id=%s payment_id=%s',
            instance.order_id,
            instance.id,
        )
