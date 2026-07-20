from rest_framework.versioning import URLPathVersioning


class APIVersioning(URLPathVersioning):
    """URL path versioning that supports explicit /api/v1/ route includes."""

    def determine_version(self, request, *args, **kwargs):
        version = kwargs.get(self.version_param)
        if version:
            return self.is_allowed_version(version) and version

        segments = request.path_info.strip('/').split('/')
        if len(segments) >= 2 and segments[0] == 'api':
            version = segments[1]
            if self.is_allowed_version(version):
                return version

        return self.default_version
