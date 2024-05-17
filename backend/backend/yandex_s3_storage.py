from storages.backends.s3boto3 import S3Boto3Storage

from backend.settings import YANDEX_BUCKET_NAME


class ClientDocsStorage(S3Boto3Storage):
    bucket_name = YANDEX_BUCKET_NAME
    file_overwrite = False

    def url(self, name, parameters=None, expire=None):
        url = super().url(name, parameters, expire)
        pure_url = url.split("?")[0]
        return pure_url
