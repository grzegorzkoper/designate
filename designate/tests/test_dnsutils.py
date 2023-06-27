# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Author: Endre Karlson <endre.karlson@hpe.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from unittest import mock

import dns
import dns.query
import dns.tsigkeyring
from oslo_config import cfg

from designate import dnsutils
from designate.mdns import handler
from designate import storage
import designate.tests

CONF = cfg.CONF


class TestSerializationMiddleware(designate.tests.TestCase):
    def setUp(self):
        super(TestSerializationMiddleware, self).setUp()
        storage_driver = CONF['service:central'].storage_driver
        self.storage = storage.get_storage(storage_driver)
        self.tg = mock.Mock()

    def test_with_tsigkeyring(self):
        self.create_tsigkey(fixture=1)

        query = dns.message.make_query(
            'example.com.', dns.rdatatype.SOA,
        )
        query.use_tsig(dns.tsigkeyring.from_text(
            {'test-key-two': 'AnotherSecretKey'})
        )
        payload = query.to_wire()

        application = handler.RequestHandler(self.storage, self.tg)
        application = dnsutils.SerializationMiddleware(
            application, dnsutils.TsigKeyring(self.storage)
        )

        self.assertTrue(next(application(
            {'payload': payload, 'addr': ['192.0.2.1', 5353]}
        )))

    def test_without_tsigkeyring(self):
        query = dns.message.make_query(
            'example.com.', dns.rdatatype.SOA,
        )
        payload = query.to_wire()

        application = handler.RequestHandler(self.storage, self.tg)
        application = dnsutils.SerializationMiddleware(
            application, dnsutils.TsigKeyring(self.storage)
        )

        self.assertTrue(next(application(
            {'payload': payload, 'addr': ['192.0.2.1', 5353]}
        )))


class TestTsigUtils(designate.tests.TestCase):
    def setUp(self):
        super(TestTsigUtils, self).setUp()
        storage_driver = CONF['service:central'].storage_driver
        self.storage = storage.get_storage(storage_driver)
        self.tsig_keyring = dnsutils.TsigKeyring(self.storage)

    def test_tsig_keyring(self):
        expected_result = b'J\x89\x9e:WRy\xca\xde\xb4\xa7\xb2'

        self.create_tsigkey(fixture=0)

        query = dns.message.make_query(
            'example.com.', dns.rdatatype.SOA,
        )
        query.use_tsig(dns.tsigkeyring.from_text(
            {'test-key-one': 'SomeOldSecretKey'})
        )

        self.assertEqual(expected_result, self.tsig_keyring.get(query.keyname))
        self.assertEqual(expected_result, self.tsig_keyring[query.keyname])

    def test_tsig_keyring_not_found(self):
        query = dns.message.make_query(
            'example.com.', dns.rdatatype.SOA,
        )
        query.use_tsig(dns.tsigkeyring.from_text(
            {'test-key-one': 'SomeOldSecretKey'})
        )

        self.assertIsNone(self.tsig_keyring.get(query.keyname))
