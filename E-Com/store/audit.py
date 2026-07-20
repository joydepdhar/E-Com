import logging

from .models import AuditLog


audit_logger = logging.getLogger('store.audit')


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def create_audit_log(request, *, action, object_type, object_id):
    user = getattr(request, 'user', None)
    if not getattr(user, 'is_authenticated', False):
        user = None

    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            object_type=object_type,
            object_id=str(object_id),
            ip_address=get_client_ip(request),
        )
    except Exception:
        audit_logger.exception(
            'audit_log_create_failed action=%s object_type=%s object_id=%s',
            action,
            object_type,
            object_id,
        )
