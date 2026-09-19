class AppException(Exception):
    """Base class for every Synapse ERP domain exception.

    Subclasses (ValidationException, BusinessRuleException, AIException,
    PaymentException, etc.) are added phase by phase, each declaring a
    `code` and `status_code` that the global error handler maps to a
    consistent JSON envelope. Nothing in this project should raise a bare
    Exception for an expected failure case — see error_handler.py.
    """

    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code