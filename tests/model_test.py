from json import loads

import unittest

from bulkwhoisapi import BulkRequest, BulkWhoisRecord, ErrorMessage, \
    RegistryData, ResponseCreate, ResponseRecords, ResponseRequests, \
    WhoisRecord


_json_response_create_ok = '''{
    "noDataAvailable": false,
    "message": "OK",
    "messageCode": 200,
    "invalidDomains": [
        "foo.bar"
    ],
    "requestId": "12345678-1234-1234-1234-123456789012",
    "whoisRecords": [],
    "domains": []
}'''

_json_response_records_ok = '''{
    "noDataAvailable": false,
    "domainList": [
        "foo.bar"
    ],
    "requestId": "12345678-1234-1234-1234-123456789012",
    "whoisRecords": [
        {
            "domainName": "foo.bar",
            "domainStatus": "I",
            "whoisRecordStatus": 0,
            "domainFetchedTime": "1642158864782",
            "whoisRecord": {
                "registrant": {
                    "rawText": "...",
                    "organization": "foo",
                    "state": "CA",
                    "country": "UNITED STATES",
                    "parseCode": 1
                },
                "administrativeContact": {
                    "rawText": "...",
                    "organization": "foo",
                    "state": "CA",
                    "country": "UNITED STATES",
                    "parseCode": 1
                },
                "technicalContact": {
                    "rawText": "...",
                    "organization": "foo",
                    "state": "CA",
                    "country": "UNITED STATES",
                    "parseCode": 1
                },
                "audit": {},
                "nameServers": {
                    "rawText": "ns1.foo.bar",
                    "hostNames": [
                        {
                            "numeric": false,
                            "str": "ns1.foo.bar"
                        }
                    ]
                },
                "createdDate": "1997-09-15T07:00:00+0000",
                "updatedDate": "2019-09-09T15:39:04+0000",
                "expiresDate": "2028-09-13T07:00:00+0000",
                "domainName": "foo.bar",
                "status": "clientUpdateProhibited",
                "rawText": "...",
                "header": "",
                "strippedText": "...",
                "footer": "",
                "customField1Name": "RegistrarContactEmail",
                "customField1Value": "foo@bar.baz",
                "registrarName": "bar",
                "registrarIANAID": "111111111111111",
                "whoisServer": "foo.bar.baz",
                "createdDateNormalized": "1997-09-15 07:00:00 UTC",
                "updatedDateNormalized": "2019-09-09 15:39:04 UTC",
                "expiresDateNormalized": "2028-09-13 07:00:00 UTC",
                "dataErrorFlag": 0,
                "parseCode": 3579,
                "registryData": {
                    "audit": {},
                    "nameServers": {
                        "rawText": "ns1.foo.bar",
                        "hostNames": [
                            {
                                "numeric": false,
                                "str": "ns1.foo.bar"
                            }
                        ]
                    },
                    "createdDate": "1997-09-15T04:00:00Z",
                    "updatedDate": "2019-09-09T15:39:04Z",
                    "expiresDate": "2028-09-14T04:00:00Z",
                    "domainName": "foo.bar",
                    "status": "clientDeleteProhibited",
                    "rawText": "...",
                    "header": "",
                    "strippedText": "...",
                    "footer": "",
                    "customField1Name": "RegistrarContactEmail",
                    "customField1Value": "foo@bar.baz",
                    "registrarName": "bar",
                    "registrarIANAID": "1111111111111",
                    "whoisServer": "foo.bar.baz",
                    "createdDateNormalized": "1997-09-15 04:00:00 UTC",
                    "updatedDateNormalized": "2019-09-09 15:39:04 UTC",
                    "expiresDateNormalized": "2028-09-14 04:00:00 UTC",
                    "dataErrorFlag": 0,
                    "parseCode": 251
                },
                "contactEmail": "foo@bar.baz",
                "domainNameExt": ".bar",
                "estimatedDomainAge": 8887
            },
            "index": 1
        }
    ],
    "totalRecords": 1,
    "recordsLeft": 0,
    "recordsProcessed": 1
}'''

_json_response_requests_ok = '''{
    "userRequests": [
        {
            "requestId": "12345678-1234-1234-1234-123456789012",
            "time": 1641985855887,
            "status": "Completed",
            "totalRecords": 2,
            "fetchedRecords": 0
        },
        {
            "requestId": "12345678-1234-1234-1234-123456789013",
            "time": 1611308168576,
            "status": "Completed",
            "totalRecords": 1,
            "fetchedRecords": 0
        }
    ]
}'''

_json_response_error = '''{
    "message": "Domain list can not be empty!",
    "messageCode": 417
}'''


class TestModel(unittest.TestCase):

    def test_response_create_parsing(self):
        response = loads(_json_response_create_ok)
        parsed = ResponseCreate(response)
        self.assertEqual(parsed.request_id, response['requestId'])
        self.assertIsInstance(parsed.invalid_domains, list)

        self.assertEqual(parsed.invalid_domains[0],
                         response['invalidDomains'][0])

    def test_response_records_parsing(self):
        response = loads(_json_response_records_ok)
        parsed = ResponseRecords(response)
        self.assertEqual(parsed.request_id, response['requestId'])
        self.assertIsInstance(parsed.whois_records, list)
        self.assertIsInstance(parsed.whois_records[0], BulkWhoisRecord)

        self.assertIsInstance(parsed.whois_records[0].whois_record,
                              WhoisRecord)

        self.assertIsInstance(
            parsed.whois_records[0].whois_record.registry_data,
            RegistryData
        )

        self.assertEqual(
            parsed.whois_records[0].whois_record.registry_data.domain_name,
            response['whoisRecords'][0]
                    ['whoisRecord']['registryData']['domainName']
        )

        self.assertEqual(
            parsed.whois_records[0].whois_record.registrant.organization,
            response['whoisRecords'][0]
                    ['whoisRecord']['registrant']['organization']
        )

    def test_response_requests_parsing(self):
        response = loads(_json_response_requests_ok)
        parsed = ResponseRequests(response)
        self.assertIsInstance(parsed.user_requests, list)
        self.assertIsInstance(parsed.user_requests[0], BulkRequest)

        self.assertEqual(len(parsed.user_requests),
                         len(response['userRequests']))

        self.assertEqual(parsed.user_requests[1].request_id,
                         response['userRequests'][1]['requestId'])

    def test_error_parsing(self):
        error = loads(_json_response_error)
        parsed_error = ErrorMessage(error)
        self.assertEqual(parsed_error.code, error['messageCode'])
        self.assertEqual(parsed_error.message, error['message'])
