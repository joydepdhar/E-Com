import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.db import DatabaseError, IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    Throttled,
    UnsupportedMediaType,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler


logger = logging.getLogger('store')


CLIENT_ERROR_MESSAGES = {
    ValidationError: 'Validation error.',
    AuthenticationFailed: 'Authentication failed.',
    NotAuthenticated: 'Authentication credentials were not provided.',
    PermissionDenied: 'Permission denied.',
    NotFound: 'Not found.',
    MethodNotAllowed: 'Method not allowed.',
    ParseError: 'Malformed request.',
    UnsupportedMediaType: 'Unsupported media type.',
    Throttled: 'Request was throttled.',
}


def error_response(*, message, errors=None, status_code=status.HTTP_400_BAD_REQUEST, headers=None):
    return Response(
        {
            'success': False,
            'message': message,
            'errors': errors or {},
            'status_code': status_code,
        },
        status=status_code,
        headers=headers,
    )


def custom_exception_handler(exc, context):
    if isinstance(exc, IntegrityError):
        logger.exception('database_integrity_error')
        return error_response(
            message='A data integrity error occurred.',
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, DatabaseError):
        logger.exception('database_error')
        return error_response(
            message='A database error occurred.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, Http404):
        exc = NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = PermissionDenied()

    response = exception_handler(exc, context)
    if response is not None:
        status_code = response.status_code
        return error_response(
            message=_message_for_exception(exc, status_code),
            errors=_errors_for_exception(exc, response.data),
            status_code=status_code,
            headers=response.headers,
        )

    request = context.get('request')
    view = context.get('view')
    logger.exception(
        'unexpected_exception view=%s method=%s path=%s',
        view.__class__.__name__ if view else None,
        getattr(request, 'method', None),
        getattr(request, 'path', None),
    )
    return error_response(
        message='An unexpected error occurred.',
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _message_for_exception(exc, status_code):
    for exception_class, message in CLIENT_ERROR_MESSAGES.items():
        if isinstance(exc, exception_class):
            return message

    if isinstance(exc, APIException):
        return 'API error.'

    return {
        status.HTTP_400_BAD_REQUEST: 'Bad request.',
        status.HTTP_401_UNAUTHORIZED: 'Authentication required.',
        status.HTTP_403_FORBIDDEN: 'Permission denied.',
        status.HTTP_404_NOT_FOUND: 'Not found.',
        status.HTTP_405_METHOD_NOT_ALLOWED: 'Method not allowed.',
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: 'Unsupported media type.',
        status.HTTP_429_TOO_MANY_REQUESTS: 'Request was throttled.',
    }.get(status_code, 'Request failed.')


def _errors_for_exception(exc, response_data):
    if isinstance(exc, ValidationError):
        return response_data

    if isinstance(response_data, dict) and 'detail' not in response_data:
        return response_data

    return {}
