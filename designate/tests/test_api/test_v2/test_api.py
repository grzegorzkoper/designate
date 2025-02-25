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

from designate.tests.test_api.test_v2 import ApiV2TestCase


class ApiV2DisableTest(ApiV2TestCase):
    def setUp(self):
        self.config(enable_api_v2=False, group='service:api')
        super(ApiV2DisableTest, self).setUp()

    def test_disable_v2_api(self):
        urls = ['zones', 'pools', 'service_statuses']

        for url in urls:
            response = self.client.get('/%s/' % url, expect_errors=True)

            self.assertEqual(404, response.status_code)
            self.assertEqual(b'', response.body)
