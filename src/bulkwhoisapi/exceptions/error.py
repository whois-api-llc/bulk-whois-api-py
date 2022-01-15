from json import loads

from ..models.response import ErrorMessage


class BulkWhoisApiError(Exception):
    def __init__(self, message):
        self.message = message

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

    def __str__(self):
        return str(self.__dict__)


class ResponseError(BulkWhoisApiError):
    def __init__(self, message):
        self.message = message
        self.parsed_message = None
        try:
            parsed = loads(message)
            self.parsed_message = ErrorMessage(parsed)
        except Exception:
            pass

    @property
    def parsed_message(self):
        return self._parsed_message

    @parsed_message.setter
    def parsed_message(self, pm):
        self._parsed_message = pm


class ApiAuthError(ResponseError):
    def __init__(self, message):
        super().__init__(message)

        if self.parsed_message.code < 0:
            self.parsed_message.code = 403
            self.parsed_message.message = \
                'Access restricted. Check credits balance ' \
                'or enter a correct API key'


class BadRequestError(ResponseError):
    pass


class EmptyApiKeyError(BulkWhoisApiError):
    pass


class FileError(BulkWhoisApiError):
    pass


class HttpApiError(BulkWhoisApiError):
    pass


class ParameterError(BulkWhoisApiError):
    pass


class UnparsableApiResponseError(BulkWhoisApiError):
    def __init__(self, message, origin_error):
        self.message = message
        self.original_error = origin_error

    @property
    def original_error(self):
        return self._original_error

    @original_error.setter
    def original_error(self, oe):
        self._original_error = oe
