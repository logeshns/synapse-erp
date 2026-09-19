class ToolExecutionError(Exception):
    """Raised by a tool handler on a known, structured failure. Caught by
    tool_guard.execute_tool and converted into a result dict — never
    propagates up to crash the agent loop or the HTTP response."""

    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message
        super().__init__(message)