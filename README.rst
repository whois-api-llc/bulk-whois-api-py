.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :alt: bulk-whois-api-py license
    :target: https://opensource.org/licenses/MIT

.. image:: https://img.shields.io/pypi/v/bulk-whois-api.svg
    :alt: bulk-whois-api-py release
    :target: https://pypi.org/project/bulk-whois-api

.. image:: https://github.com/whois-api-llc/bulk-whois-api-py/workflows/Build/badge.svg
    :alt: bulk-whois-api-py build
    :target: https://github.com/whois-api-llc/bulk-whois-api-py/actions

========
Overview
========

The client library for
`Bulk Whois API <https://whois.whoisxmlapi.com/bulk-api>`_
in Python language.

The minimum Python version is 3.6.

Installation
============

.. code-block:: shell

    pip install bulk-whois-api

Examples
========

Full API documentation available `here <https://whois.whoisxmlapi.com/bulk-api/documentation/making-requests>`_

Create a new client
-------------------

.. code-block:: python

    from bulkwhoisapi import *

    client = Client('Your API key')

Create bulk request
-------------------

.. code-block:: python

    domains = [
        'example.com',
        'example.org'
    ]

    result = client.create_request(domains=domains)

    # Used for further requests
    request_id = result.request_id

Get Whois records
-------------------

.. code-block:: python

    result = client.get_records(
        request_id=request_id,
        max_records=len(domains)
    )

    # Finished once result.records_left == 0
    print(result)

List your requests
-------------------

.. code-block:: python

    result = client.get_requests()

Download CSV result
-------------------

.. code-block:: python

    client.download(filename='records.csv', request_id=request_id)

Extras
-------------------

.. code-block:: python

    # Paginate over processed records and get results in XML
    result = client.get_records_raw(
        request_id=request_id,
        max_records=1,
        start_index=2,
        output_format=Client.XML_FORMAT
    )

Response model overview
-----------------------

.. code-block:: python

    ResponseCreate:
        - request_id: str
        - invalid_domains: [str]

    ResponseRecords:
        - no_data_available: bool
        - request_id: str
        - total_records: int
        - records_left: int
        - records_processed: int
        - domain_list: [str]
        - whois_records: [BulkWhoisRecord]

    ResponseRequests:
        - user_requests: [BulkRequest]

