import os
import unittest

from bulkwhoisapi import ApiAuthError, Client, FileError, ParameterError


class TestClient(unittest.TestCase):
    """
    Final integration tests without mocks.

    Active API_KEY is required.
    """

    correct_filename = 'bulk_whois_lib_test_download.csv'

    def setUp(self) -> None:
        self.client = Client(os.getenv('API_KEY'))

        self.correct_domains = ['example.com', 'example.net', 'test']
        self.correct_max_records = 1
        self.correct_request = os.getenv('BULK_WHOIS_REQUEST')

        self.incorrect_api_key = 'at_00000000000000000000000000000'
        self.incorrect_filename = 'src/does6/not257/exist5e7/8at/44all55'
        self.incorrect_request = '123'

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.correct_filename)

    def test_create_correct_data(self):
        response = self.client.create_request(domains=self.correct_domains)
        self.assertEqual(len(response.invalid_domains), 1)
        self.assertIsNotNone(response.request_id)
        self.assertEqual(response.invalid_domains[0], self.correct_domains[2])

    def test_create_empty_domains(self):
        with self.assertRaises(ParameterError):
            self.client.create_request(domains=[])

    def test_download(self):
        self.client.download(filename=self.correct_filename,
                             request_id=self.correct_request)
        self.assertGreater(os.path.getsize(self.correct_filename), 0)

    def test_empty_api_key_create(self):
        with self.assertRaises(ParameterError):
            client = Client('')
            client.create_request(domains=self.correct_domains)

    def test_empty_api_key_download(self):
        with self.assertRaises(ParameterError):
            client = Client('')
            client.download(request_id=self.correct_request)

    def test_empty_api_key_get_requests(self):
        with self.assertRaises(ParameterError):
            client = Client('')
            client.get_requests()

    def test_empty_api_key_get_records(self):
        with self.assertRaises(ParameterError):
            client = Client('')
            client.get_records(request_id=self.correct_request,
                               max_records=self.correct_max_records)

    def test_empty_filename(self):
        with self.assertRaises(ParameterError):
            self.client.download(request_id=self.correct_request)

    def test_empty_max_records(self):
        with self.assertRaises(ParameterError):
            self.client.get_records(request_id=self.correct_request)

    def test_empty_request_id(self):
        with self.assertRaises(ParameterError):
            self.client.download()

    def test_get_records(self):
        response = self.client.get_records(
            request_id=self.correct_request,
            max_records=self.correct_max_records
        )
        self.assertEqual(len(response.whois_records), 1)
        self.assertIsNotNone(response.request_id)
        self.assertEqual(response.records_processed, 1)

    def test_get_requests(self):
        response = self.client.get_requests()
        self.assertGreater(len(response.user_requests), 0)
        self.assertIsNotNone(response.user_requests[0].time)

    def test_incorrect_api_key_create(self):
        with self.assertRaises(ApiAuthError):
            client = Client(self.incorrect_api_key)
            client.create_request(domains=self.correct_domains)

    def test_incorrect_api_key_get_requests(self):
        with self.assertRaises(ApiAuthError):
            client = Client(self.incorrect_api_key)
            client.get_requests()

    def test_incorrect_api_key_get_records(self):
        with self.assertRaises(ApiAuthError):
            client = Client(self.incorrect_api_key)
            client.get_records(request_id=self.correct_request,
                               max_records=self.correct_max_records)

    def test_incorrect_filename(self):
        with self.assertRaises(FileError):
            self.client.download(filename=self.incorrect_filename,
                                 request_id=self.correct_request)

    def test_incorrect_max_records(self):
        with self.assertRaises(ParameterError):
            self.client.get_records(request_id=self.correct_request,
                                    max_records='foo')

    def test_incorrect_start_index(self):
        with self.assertRaises(ParameterError):
            self.client.get_records(
                request_id=self.correct_request,
                max_records=self.correct_max_records,
                start_index='bar'
            )

    def test_incorrect_search_type(self):
        with self.assertRaises(ParameterError):
            self.client.download(
                filename=self.correct_filename,
                request_id=self.correct_request,
                search_type=123
            )

    def test_raw_create(self):
        response = self.client.create_request_raw(
            domains=self.correct_domains,
            output_format=Client.XML_FORMAT
        )
        self.assertTrue(response.startswith('<?xml'))

    def test_raw_download(self):
        response = self.client.download_raw(request_id=self.correct_request)
        self.assertTrue(response.startswith('domainName'))

    def test_raw_records(self):
        response = self.client.get_records_raw(
            request_id=self.correct_request,
            max_records=self.correct_max_records,
            output_format=Client.XML_FORMAT
        )
        self.assertTrue(response.startswith('<?xml'))

    def test_raw_requests(self):
        response = self.client.get_requests_raw(
            output_format=Client.XML_FORMAT
        )
        self.assertTrue(response.startswith('<?xml'))

    def test_output(self):
        with self.assertRaises(ParameterError):
            self.client.get_requests(response_format='yaml')


if __name__ == '__main__':
    unittest.main()
