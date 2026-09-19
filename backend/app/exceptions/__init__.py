class AppException(Exception):
    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code


class ValidationException(AppException):
    code = "VALIDATION_ERROR"
    status_code = 400


class AuthenticationException(AppException):
    code = "AUTHENTICATION_FAILED"
    status_code = 401


class AuthorizationException(AppException):
    code = "FORBIDDEN"
    status_code = 403


class NotFoundException(AppException):
    code = "NOT_FOUND"
    status_code = 404


class BusinessRuleException(AppException):
    code = "BUSINESS_RULE_VIOLATION"
    status_code = 409


class AIException(AppException):
    code = "AI_ERROR"
    status_code = 503


class AIProviderException(AIException):
    code = "AI_PROVIDER_UNAVAILABLE"
    status_code = 503


class AITimeoutException(AIException):
    code = "AI_TIMEOUT"
    status_code = 504


class AISchemaException(AIException):
    code = "AI_SCHEMA_VALIDATION_FAILED"
    status_code = 422


class PDFException(AppException):
    code = "PDF_GENERATION_FAILED"
    status_code = 500


class PaymentException(AppException):
    code = "PAYMENT_ERROR"
    status_code = 502


class PaymentProviderException(PaymentException):
    code = "PAYMENT_PROVIDER_ERROR"
    status_code = 502


class PaymentWebhookException(PaymentException):
    code = "PAYMENT_WEBHOOK_INVALID"
    status_code = 400