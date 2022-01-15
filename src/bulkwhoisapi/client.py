from json import loads, JSONDecodeError
from uuid import UUID

import re

from .exceptions.error import EmptyApiKeyError, FileError, ParameterError, \
    UnparsableApiResponseError
from .models.response import ResponseCreate, ResponseRecords, ResponseRequests
from .net.http import ApiRequester


class Client:
    __default_url = 'https://www.whoisxmlapi.com/BulkWhoisLookup/bulkServices'
    _api_requester: ApiRequester or None
    _api_key: str

    _re_api_key = re.compile(r'^at_[a-z0-9]{29}$', re.IGNORECASE)

    _PARSABLE_FORMAT = 'json'

    _PATH_CREATE = '/bulkWhois'
    _PATH_DOWNLOAD = '/download'
    _PATH_REQUESTS = '/getUserRequests'
    _PATH_RECORDS = '/getRecords'

    JSON_FORMAT = 'json'
    XML_FORMAT = 'xml'

    SEARCH_ALL = 'all'
    SEARCH_NO_ERROR = 'noerror'

    def __init__(self, api_key: str, **kwargs):
        """
        :param api_key: str: Your API key
        :key base_url: str: (optional) API endpoint URL
        :key timeout: float: (optional) API call timeout in seconds
        """

        self._api_key = ''

        self.api_key = api_key

        if 'base_url' not in kwargs:
            kwargs['base_url'] = Client.__default_url

        self.api_requester = ApiRequester(**kwargs)

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        self._api_key = Client._validate_api_key(value)

    @property
    def api_requester(self) -> ApiRequester or None:
        return self._api_requester

    @api_requester.setter
    def api_requester(self, value: ApiRequester):
        self._api_requester = value

    @property
    def base_url(self) -> str:
        return self._api_requester.base_url

    @base_url.setter
    def base_url(self, value: str or None):
        if value is None:
            self._api_requester.base_url = Client.__default_url
        else:
            self._api_requester.base_url = value

    @property
    def timeout(self) -> float:
        return self._api_requester.timeout

    @timeout.setter
    def timeout(self, value: float):
        self._api_requester.timeout = value

    def create_request(self, **kwargs) -> ResponseCreate:
        """
        Create bulk domain names processing request
        :key domains: Required. list[str]
        :return: `ResponseCreate` instance
        :raises ConnectionError:
        :raises BulkWhoisApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400, 417 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        kwargs['output_format'] = Client._PARSABLE_FORMAT

        response = self.create_request_raw(**kwargs)

        try:
            parsed = loads(str(response))
            if 'requestId' in parsed:
                return ResponseCreate(parsed)
            raise UnparsableApiResponseError(
                "Could not find the correct root element.", None)
        except JSONDecodeError as error:
            raise UnparsableApiResponseError(
                    "Could not parse API response",
                    error)

    def download(self, **kwargs):
        """
        Download processing results CSV and save to file
        :key request_id: Required. str. Request ID
        :key search_type: Optional.
                Supported options: SEARCH_ALL, SEARCH_NO_ERROR.
                SEARCH_ALL by default
        :raises ConnectionError:
        :raises BulkWhoisApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400, 417 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        filename = None

        kwargs['output_format'] = Client._PARSABLE_FORMAT

        if 'filename' in kwargs:
            filename = kwargs['filename']

        if type(filename) is not str or not filename:
            raise ParameterError('Output file name required')

        try:
            result_file = open(filename, 'w')
        except Exception:
            raise FileError('Cannot open output file')

        result_file.close()

        response = self.download_raw(**kwargs)

        try:
            result_file = open(filename, 'w')
            result_file.write(response)
        except Exception:
            raise FileError('Cannot write result to file')
        finally:
            result_file.close()

    def get_records(self, **kwargs) -> ResponseRecords:
        """
        Get Whois records
        :key request_id: Required. str. Request ID
        :key max_records: Required. int. Max number of records to return.
                Min: 1
        :key start_index: Optional. int. First record to be returned.
                Min: 1. Use for pagination
        :return: `ResponseRecords` instance
        :raises ConnectionError:
        :raises BulkWhoisApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400, 417 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        kwargs['output_format'] = Client._PARSABLE_FORMAT

        response = self.get_records_raw(**kwargs)

        try:
            parsed = loads(str(response))
            if 'whoisRecords' in parsed:
                return ResponseRecords(parsed)
            raise UnparsableApiResponseError(
                'Cannot find the correct root element', None)
        except JSONDecodeError as error:
            raise UnparsableApiResponseError(
                    'Could not parse API response',
                    error)

    def get_requests(self, **kwargs) -> ResponseRequests:
        """
        Get a list of your requests
        :return: `ResponseRequests` instance
        :raises ConnectionError:
        :raises BulkWhoisApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400, 417 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        kwargs['output_format'] = Client._PARSABLE_FORMAT

        response = self.get_requests_raw(**kwargs)

        try:
            parsed = loads(str(response))
            if 'userRequests' in parsed:
                return ResponseRequests(parsed)
            raise UnparsableApiResponseError(
                'Cannot find the correct root element', None)
        except JSONDecodeError as error:
            raise UnparsableApiResponseError(
                    'Could not parse API response',
                    error)

    def create_request_raw(self, **kwargs) -> str:
        """
        Get raw create response
        :key domains: Required. list[str]
        :key output_format: Optional. Response output format.
                Supported options: JSON_FORMAT, XML_FORMAT.
                JSON_FORMAT by default
        :return: str
        :raises ConnectionError:
        :raises BulkWhoisApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400, 417 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        domains = None

        if self.api_key == '':
            raise EmptyApiKeyError('')

        if 'domains' in kwargs:
            domains = Client._validate_domains(kwargs['domains'])

        if not domains:
            raise ParameterError('Domain names required')

        if 'response_format' in kwargs:
            kwargs['output_format'] = kwargs['response_format']
        if 'output_format' in kwargs:
            output_format = Client._validate_output_format(
                kwargs['output_format'])
        else:
            output_format = Client._PARSABLE_FORMAT

        return self._api_requester.post(
            self._PATH_CREATE,
            self._build_payload(self.api_key, output_format, domains)
        )

    def download_raw(self, **kwargs) -> str:
        """
        Get raw download response
        :key request_id: Required. str. Request ID
        :key search_type: Optional.
                Supported options: SEARCH_ALL, SEARCH_NO_ERROR.
                SEARCH_ALL by default
        :return: str
        :raises ConnectionError:
        :raises BulkWhoisApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400, 417 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        request_id, search_type = [None] * 2

        if self.api_key == '':
            raise EmptyApiKeyError('')

        if 'request_id' in kwargs:
            request_id = Client._validate_request_id(kwargs['request_id'])

        if not request_id:
            raise ParameterError('Request ID required')

        if 'search_type' in kwargs:
            search_type = Client._validate_search_type(kwargs['search_type'])

        return self._api_requester.post(
            self._PATH_DOWNLOAD,
            self._build_payload(
                api_key=self.api_key,
                request_id=request_id,
                search_type=search_type
            )
        )

    def get_records_raw(self, **kwargs) -> str:
        """
        Get raw records response
        :key request_id: Required. str. Request ID
        :key max_records: Required. int. Max number of records to return.
                Min: 1
        :key start_index: Optional. int. First record to be returned.
                Min: 1. Use for pagination
        :key output_format: Optional. Response output format.
                Supported options: JSON_FORMAT, XML_FORMAT.
                JSON_FORMAT by default
        :return: str
        :raises ConnectionError:
        :raises BulkWhoisApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400, 417 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        request_id, max_records, start_index = [None] * 3

        if self.api_key == '':
            raise EmptyApiKeyError('')

        if 'request_id' in kwargs:
            request_id = Client._validate_request_id(kwargs['request_id'])

        if not request_id:
            raise ParameterError('Request ID required')

        if 'max_records' in kwargs:
            max_records = Client._validate_max_records(kwargs['max_records'])

        if not max_records:
            raise ParameterError('Max record number required')

        if 'start_index' in kwargs:
            start_index = Client._validate_start_index(kwargs['start_index'])

        if 'response_format' in kwargs:
            kwargs['output_format'] = kwargs['response_format']
        if 'output_format' in kwargs:
            output_format = Client._validate_output_format(
                kwargs['output_format'])
        else:
            output_format = Client._PARSABLE_FORMAT

        return self._api_requester.post(
            self._PATH_RECORDS,
            self._build_payload(
                self.api_key,
                output_format,
                None,
                request_id,
                max_records,
                start_index
            )
        )

    def get_requests_raw(self, **kwargs) -> str:
        """
        Get raw list response
        :key output_format: Optional. Response output format.
                Supported options: JSON_FORMAT, XML_FORMAT.
                JSON_FORMAT by default
        :return: str
        :raises ConnectionError:
        :raises BulkWhoisApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400, 417 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        if self.api_key == '':
            raise EmptyApiKeyError('')

        if 'response_format' in kwargs:
            kwargs['output_format'] = kwargs['response_format']
        if 'output_format' in kwargs:
            output_format = Client._validate_output_format(
                kwargs['output_format'])
        else:
            output_format = Client._PARSABLE_FORMAT

        return self._api_requester.post(
            self._PATH_REQUESTS,
            self._build_payload(self.api_key, output_format)
        )

    @staticmethod
    def _build_payload(
            api_key,
            output_format=None,
            domains=None,
            request_id=None,
            max_records=None,
            start_index=None,
            search_type=None
    ) -> dict:
        tmp = {
            'apiKey': api_key,
            'outputFormat': output_format,
            'domains': domains,
            'requestId': request_id,
            'maxRecords': max_records,
            'startIndex': start_index,
            'searchType': search_type
        }

        payload = {}
        for k, v in tmp.items():
            if v is not None:
                payload[k] = v
        return payload

    @staticmethod
    def _validate_api_key(api_key) -> str:
        if Client._re_api_key.search(str(api_key)) is not None:
            return str(api_key)
        else:
            raise ParameterError('Invalid API key format')

    @staticmethod
    def _validate_domains(value) -> list:
        if value is None:
            raise ParameterError('Domain name list cannot be None')
        elif type(value) is list:
            if len(value) < 1:
                raise ParameterError('Domain name list cannot be empty')
            for item in value:
                if type(item) is not str:
                    raise ParameterError('Incorrect domain name value')
            return value

        raise ParameterError('Expected a list of domain names')

    @staticmethod
    def _validate_max_records(value: int) -> int:
        if type(value) is int and value > 0:
            return value

        raise ParameterError('Max records value must be greater than 0')

    @staticmethod
    def _validate_output_format(value: str):
        if type(value) is str \
                and value.lower() in [Client.JSON_FORMAT, Client.XML_FORMAT]:
            return value.lower()

        raise ParameterError(
            f'Response format must be {Client.JSON_FORMAT} '
            f'or {Client.XML_FORMAT}')

    @staticmethod
    def _validate_request_id(request_id) -> str:
        try:
            UUID(request_id)
            return request_id
        except ValueError:
            raise ParameterError('Invalid request ID format')

    @staticmethod
    def _validate_search_type(value: str):
        if type(value) is str \
                and value.lower() in \
                [Client.SEARCH_ALL, Client.SEARCH_NO_ERROR]:
            return value.lower()

        raise ParameterError(
            f'Search type type must be {Client.SEARCH_ALL} '
            f'or {Client.SEARCH_NO_ERROR}')

    @staticmethod
    def _validate_start_index(value: int) -> int:
        if type(value) is int and value > 0:
            return value

        raise ParameterError('Start index must be greater than or equal to 1')
