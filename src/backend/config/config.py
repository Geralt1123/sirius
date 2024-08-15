from config.settings import (
    ApplicationSettings,
    DataBaseSessionSettings,
    UvicornSettings,
    DataBaseSettings,
    S3Settings,
    S3TransferSettings,
    JsonSerializerSettings
)

s3_config = S3Settings()
uvicorn_config = UvicornSettings()
application_config = ApplicationSettings()
database_settings = DataBaseSettings()
database_session_settings = DataBaseSessionSettings()
s3_transfer_config = S3TransferSettings()
json_serializer_config = JsonSerializerSettings()