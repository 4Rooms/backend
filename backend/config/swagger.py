from pathlib import Path


def get_api_description():
    docs_dir = Path(__file__).resolve().parent.parent.parent / "doc"
    with open(docs_dir / "README.md", "r") as f:
        return f.read()


SPECTACULAR_SETTINGS = {
    "TITLE": "4Room API",
    "DESCRIPTION": get_api_description(),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # Runs exemplary schema generation and emits warnings as part of "./manage.py check --deploy"
    "ENABLE_DJANGO_DEPLOY_CHECK": True,
    "POSTPROCESSING_HOOKS": ["drf_standardized_errors.openapi_hooks.postprocess_schema_enums"],
    "ENUM_NAME_OVERRIDES": {
        "ValidationErrorEnum": "drf_standardized_errors.openapi_serializers.ValidationErrorEnum.values",
        "ClientErrorEnum": "drf_standardized_errors.openapi_serializers.ClientErrorEnum.values",
        "ServerErrorEnum": "drf_standardized_errors.openapi_serializers.ServerErrorEnum.values",
        "ErrorCode401Enum": "drf_standardized_errors.openapi_serializers.ErrorCode401Enum.values",
        "ErrorCode403Enum": "drf_standardized_errors.openapi_serializers.ErrorCode403Enum.values",
        "ErrorCode404Enum": "drf_standardized_errors.openapi_serializers.ErrorCode404Enum.values",
        "ErrorCode405Enum": "drf_standardized_errors.openapi_serializers.ErrorCode405Enum.values",
        "ErrorCode406Enum": "drf_standardized_errors.openapi_serializers.ErrorCode406Enum.values",
        "ErrorCode415Enum": "drf_standardized_errors.openapi_serializers.ErrorCode415Enum.values",
        "ErrorCode429Enum": "drf_standardized_errors.openapi_serializers.ErrorCode429Enum.values",
        "ErrorCode500Enum": "drf_standardized_errors.openapi_serializers.ErrorCode500Enum.values",
    },
}

DRF_STANDARDIZED_ERRORS = {
    # enable the standardized errors when DEBUG=True for unhandled exceptions.
    "ENABLE_IN_DEBUG_FOR_UNHANDLED_EXCEPTIONS": True,
    # https://drf-standardized-errors.readthedocs.io/en/latest/openapi.html#hide-error-responses-that-show-in-every-operation
    "ALLOWED_ERROR_STATUS_CODES": ["400", "403", "404", "429"],
}
