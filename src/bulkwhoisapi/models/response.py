import copy
import datetime
import sys

from whoisapi.models.base import BaseModel
from whoisapi import WhoisRecord, RegistryData

if sys.version_info < (3, 9):
    import typing


def _bool_value(values: dict, key: str) -> bool:
    if key in values and values[key]:
        return bool(values[key])
    return False


def _int_value(values: dict, key: str) -> int:
    if key in values and values[key]:
        return int(values[key])
    return 0


def _list_of_objects(values: dict, key: str, classname: str) -> list:
    r = []
    if key in values and type(values[key]) is list:
        r = [globals()[classname](x) for x in values[key]]
    return r


def _list_value(values: dict, key: str) -> list:
    if key in values and type(values[key]) is list:
        return copy.deepcopy(values[key])
    return []


def _string_value(values: dict, key: str) -> str:
    if key in values and values[key]:
        return str(values[key])
    return ''


def _timestamp2datetime(timestamp) -> datetime.datetime or None:
    if timestamp is not None:
        return datetime.datetime.utcfromtimestamp(timestamp)
    return None


class BaseModel(BaseModel):
    def __repr__(self):
        return self.__str__()


class RegistryData(RegistryData):
    def __init__(self, values):
        super().__init__(values)

        self.custom1_field_name = _string_value(values, 'customField1Name')
        self.custom1_field_value = _string_value(values, 'customField1Value')
        self.custom2_field_name = _string_value(values, 'customField2Name')
        self.custom2_field_value = _string_value(values, 'customField2Value')
        self.custom3_field_name = _string_value(values, 'customField3Name')
        self.custom3_field_value = _string_value(values, 'customField3Value')


class WhoisRecord(WhoisRecord):
    registry_data: RegistryData or None

    def __init__(self, values):
        super().__init__(values)

        self.custom1_field_name = _string_value(values, 'customField1Name')
        self.custom1_field_value = _string_value(values, 'customField1Value')
        self.custom2_field_name = _string_value(values, 'customField2Name')
        self.custom2_field_value = _string_value(values, 'customField2Value')
        self.custom3_field_name = _string_value(values, 'customField3Name')
        self.custom3_field_value = _string_value(values, 'customField3Value')

        if values is not None:
            if 'registryData' in values:
                self.registry_data = RegistryData(values['registryData'])


class BulkRequest(BaseModel):
    request_id: str
    time: datetime.datetime or None
    status: str
    total_records: int
    fetched_records: int

    def __init__(self, values):
        super().__init__()
        self.request_id = ''
        self.time = None
        self.status = ''
        self.total_records = 0
        self.fetched_records = 0

        if values is not None:
            self.request_id = _string_value(values, 'requestId')
            self.time = _timestamp2datetime(_int_value(values, 'time')/1000)
            self.status = _string_value(values, 'status')
            self.total_records = _int_value(values, 'totalRecords')
            self.fetched_records = _int_value(values, 'fetchedRecords')


class BulkWhoisRecord(BaseModel):
    domain_name: str
    domain_status: str
    whois_record_status: int
    domain_fetched_time: datetime.datetime or None
    index: int
    whois_record: WhoisRecord or None

    def __init__(self, values):
        super().__init__()
        self.domain_name = ''
        self.domain_status = ''
        self.whois_record_status = -1
        self.domain_fetched_time = None
        self.index = 0
        self.whois_record = None

        if values is not None:
            self.domain_name = _string_value(values, 'domainName')
            self.domain_status = _string_value(values, 'domainStatus')

            if 'whoisRecordStatus' in values:
                self.whois_record_status = \
                    _int_value(values, 'whoisRecordStatus')

            if 'domainFetchedTime' in values:
                self.domain_fetched_time = _timestamp2datetime(
                    int(_string_value(values, 'domainFetchedTime'))/1000
                )

            self.index = _int_value(values, 'index')

            if 'whoisRecord' in values:
                self.whois_record = WhoisRecord(values['whoisRecord'])


class ErrorMessage(BaseModel):
    code: int
    message: str

    def __init__(self, values):
        super().__init__()

        self.code = 0
        self.message = ''

        if values is not None:
            self.code = _int_value(values, 'messageCode')
            self.message = _string_value(values, 'message')


class ResponseCreate(BaseModel):
    request_id: str

    if sys.version_info < (3, 9):
        invalid_domains: typing.List[str]
    else:
        invalid_domains: [str]

    def __init__(self, values):
        super().__init__()

        self.invalid_domains = []
        self.request_id = ''

        if values is not None:
            self.invalid_domains = _list_value(values, 'invalidDomains')
            self.request_id = _string_value(values, 'requestId')


class ResponseRecords(BaseModel):
    no_data_available: bool
    request_id: str
    total_records: int
    records_left: int
    records_processed: int

    if sys.version_info < (3, 9):
        domain_list: typing.List[str]
        whois_records: typing.List[BulkWhoisRecord]
    else:
        domain_list: [str]
        whois_records: [BulkWhoisRecord]

    def __init__(self, values):
        super().__init__()

        self.no_data_available = False
        self.request_id = ''
        self.total_records = 0
        self.records_left = 0
        self.records_processed = 0
        self.domain_list = []
        self.whois_records = []

        if values is not None:
            self.no_data_available = _bool_value(values, 'noDataAvailable')
            self.request_id = _string_value(values, 'requestId')
            self.total_records = _int_value(values, 'totalRecords')
            self.records_left = _int_value(values, 'recordsLeft')
            self.records_processed = _int_value(values, 'recordsProcessed')
            self.domain_list = _list_value(values, 'domainList')

            self.whois_records = \
                _list_of_objects(values, 'whoisRecords', 'BulkWhoisRecord')


class ResponseRequests(BaseModel):
    if sys.version_info < (3, 9):
        user_requests: typing.List[BulkRequest]
    else:
        user_requests: [BulkRequest]

    def __init__(self, values):
        super().__init__()

        self.user_requests = []

        if values is not None:
            self.user_requests = \
                _list_of_objects(values, 'userRequests', 'BulkRequest')
