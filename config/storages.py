from storages.backends.s3boto3 import S3Boto3Storage
from mimetypes import guess_type
from django.conf import settings

class StaticStorage(S3Boto3Storage):
    location = "static"
    querystring_auth = False

    @property
    def custom_domain(self):
        return settings.AWS_CLOUDFRONT_DNS

    def _save(self, name, content):
        content_type, _ = guess_type(name)
        if content_type:
            content.content_type = content_type
        return super()._save(name, content)