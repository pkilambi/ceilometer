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
"""Tests for ceilometer.meter.notifications
"""

import datetime
import mock

from oslo_config import fixture as fixture_config

from ceilometer.meter import notifications
from ceilometer import sample
from ceilometer.tests import base as test


def fake_uuid(x):
    return '%s-%s-%s-%s' % (x * 8, x * 4, x * 4, x * 12)


NOW = datetime.datetime.isoformat(datetime.datetime.utcnow())

NOTIFICATION_SEND = {
    u'event_type': u'image.send',
    u'timestamp': NOW,
    u'message_id': fake_uuid('a'),
    u'priority': u'INFO',
    u'publisher_id': u'images.example.com',
    u'payload': {u'receiver_tenant_id': fake_uuid('b'),
                 u'destination_ip': u'1.2.3.4',
                 u'bytes_sent': 42,
                 u'image_id': fake_uuid('c'),
                 u'receiver_user_id': fake_uuid('d'),
                 u'owner_id': fake_uuid('e')}
}


NOTIFICATION_L3_METER = {
    u'_context_roles': [u'admin'],
    u'_context_read_deleted': u'no',
    u'event_type': u'l3.meter',
    u'timestamp': u'2013-08-22 13:14:06.880304',
    u'_context_tenant_id': None,
    u'payload': {u'first_update': 1377176476,
                 u'bytes': 10,
                 u'label_id': u'383244a7-e99b-433a-b4a1-d37cf5b17d15',
                 u'last_update': 1377177246,
                 u'host': u'precise64',
                 u'tenant_id': u'admin',
                 u'time': 30,
                 u'pkts': 0},
    u'priority': u'INFO',
    u'_context_is_admin': True,
    u'_context_timestamp': u'2013-08-22 13:01:06.614635',
    u'_context_user_id': None,
    u'publisher_id': u'metering.precise64',
    u'message_id': u'd7aee6e8-c7eb-4d47-9338-f60920d708e4',
    u'_unique_id': u'd5a3bdacdcc24644b84e67a4c10e886a',
    u'_context_project_id': None}

INSTANCE_CREATE_END = {
    u'_context_auth_token': u'3d8b13de1b7d499587dfc69b77dc09c2',
    u'_context_is_admin': True,
    u'_context_project_id': u'7c150a59fe714e6f9263774af9688f0e',
    u'_context_quota_class': None,
    u'_context_read_deleted': u'no',
    u'_context_remote_address': u'10.0.2.15',
    u'_context_request_id': u'req-d68b36e0-9233-467f-9afb-d81435d64d66',
    u'_context_roles': [u'admin'],
    u'_context_timestamp': u'2012-05-08T20:23:41.425105',
    u'_context_user_id': u'1e3ce043029547f1a61c1996d1a531a2',
    u'event_type': u'compute.instance.create.end',
    u'message_id': u'dae6f69c-00e0-41c0-b371-41ec3b7f4451',
    u'payload': {u'created_at': u'2012-05-08 20:23:41',
                 u'deleted_at': u'',
                 u'disk_gb': 0,
                 u'display_name': u'testme',
                 u'fixed_ips': [{u'address': u'10.0.0.2',
                                 u'floating_ips': [],
                                 u'meta': {},
                                 u'type': u'fixed',
                                 u'version': 4}],
                 u'image_ref_url': u'http://10.0.2.15:9292/images/UUID',
                 u'instance_id': u'9f9d01b9-4a58-4271-9e27-398b21ab20d1',
                 u'instance_type': u'm1.tiny',
                 u'instance_type_id': 2,
                 u'launched_at': u'2012-05-08 20:23:47.985999',
                 u'memory_mb': 512,
                 u'state': u'active',
                 u'state_description': u'',
                 u'tenant_id': u'7c150a59fe714e6f9263774af9688f0e',
                 u'user_id': u'1e3ce043029547f1a61c1996d1a531a2',
                 u'reservation_id': u'1e3ce043029547f1a61c1996d1a531a3',
                 u'vcpus': 1,
                 u'root_gb': 0,
                 u'ephemeral_gb': 0,
                 u'host': u'compute-host-name',
                 u'availability_zone': u'1e3ce043029547f1a61c1996d1a531a4',
                 u'os_type': u'linux?',
                 u'architecture': u'x86',
                 u'image_ref': u'UUID',
                 u'kernel_id': u'1e3ce043029547f1a61c1996d1a531a5',
                 u'ramdisk_id': u'1e3ce043029547f1a61c1996d1a531a6',
                 },
    u'priority': u'INFO',
    u'publisher_id': u'compute.vagrant-precise',
    u'timestamp': u'2012-05-08 20:23:48.028195',
}

IMAGE_META = {u'status': u'saving',
              u'name': u'fake image #3',
              u'deleted': False,
              u'container_format': u'ovf',
              u'created_at': u'2012-09-18T10:13:44.571370',
              u'disk_format': u'vhd',
              u'updated_at': u'2012-09-18T10:13:44.623120',
              u'properties': {u'key2': u'value2',
                              u'key1': u'value1'},
              u'min_disk': 0,
              u'protected': False,
              u'id': fake_uuid('c'),
              u'location': None,
              u'checksum': u'd990432ef91afef3ad9dbf4a975d3365',
              u'owner': "fake",
              u'is_public': False,
              u'deleted_at': None,
              u'min_ram': 0,
              u'size': 19}


NOTIFICATION_UPDATE = {"message_id": "0c65cb9c-018c-11e2-bc91-5453ed1bbb5f",
                       "publisher_id": "images.example.com",
                       "event_type": "image.update",
                       "priority": "info",
                       "payload": IMAGE_META,
                       "timestamp": NOW}


NOTIFICATION_UPLOAD = {"message_id": "0c65cb9c-018c-11e2-bc91-5453ed1bbb5f",
                       "publisher_id": "images.example.com",
                       "event_type": "image.upload",
                       "priority": "info",
                       "payload": IMAGE_META,
                       "timestamp": NOW}


NOTIFICATION_DELETE = {"message_id": "0c65cb9c-018c-11e2-bc91-5453ed1bbb5f",
                       "publisher_id": "images.example.com",
                       "event_type": "image.delete",
                       "priority": "info",
                       "payload": IMAGE_META,
                       "timestamp": NOW}


TABLE_CREATE_PAYLOAD = {
    u'table_uuid': fake_uuid('r'),
    u'index_count': 2,
    u'table_name': u'email_data'
    }

NOTIFICATION_TABLE_CREATE = {
    u'_context_request_id': u'req-d6e9b7ec-976f-443f-ba6e-e2b89b18aa75',
    u'_context_tenant': fake_uuid('t'),
    u'_context_user': fake_uuid('u'),
    u'_context_auth_token': u'',
    u'_context_show_deleted': False,
    u'_context_is_admin': u'False',
    u'_context_read_only': False,
    'payload': TABLE_CREATE_PAYLOAD,
    'publisher_id': u'magnetodb.winterfell.com',
    'message_id': u'3d71fb8a-f1d7-4a4e-b29f-7a711a761ba1',
    'event_type': u'magnetodb.table.create.end',
    'timestamp': NOW,
    'priority': 'info'
    }


class TestNotifications(test.BaseTestCase):

    def setUp(self):
        super(TestNotifications, self).setUp()
        self.CONF = self.useFixture(fixture_config.Config()).conf
        self.CONF.set_override(
            'definitions_cfg_file',
            self.path_get('etc/ceilometer/meters.yaml'), group='meter')
        self.handler = notifications.ProcessMeterNotifications(mock.Mock())

    def _verify_common_counter(self, c, name, volume, resource_id):
        self.assertIsNotNone(c)
        self.assertEqual(name, c.name)
        self.assertEqual(resource_id, c.resource_id)
        self.assertEqual(NOW, c.timestamp)
        self.assertEqual(volume, c.volume)

    def test_metering_report(self):
        samples = list(self.handler.process_notification(
            NOTIFICATION_L3_METER))
        self.assertEqual(1, len(samples))
        self.assertEqual("bandwidth", samples[0].name)

    def test_image_download(self):
        counters = list(self.handler.process_notification(
            NOTIFICATION_SEND))
        self.assertEqual(2, len(counters))
        download = [item for item in counters
                    if item.name == "image.download"][0]
        self._verify_common_counter(download,
                                    'image.download', 42, fake_uuid('c'))
        self.assertEqual(fake_uuid('d'), download.user_id)
        self.assertEqual(fake_uuid('b'), download.project_id)
        self.assertEqual(sample.TYPE_DELTA, download.type)

    def test_image_serve(self):
        counters = list(self.handler.process_notification(NOTIFICATION_SEND))
        self.assertEqual(2, len(counters))
        serve = [item for item in counters if item.name == "image.serve"][0]
        self._verify_common_counter(serve, 'image.serve', 42, fake_uuid('c'))
        self.assertEqual(fake_uuid('e'), serve.project_id)
        self.assertEqual(fake_uuid('d'),
                         serve.resource_metadata.get('receiver_user_id'))
        self.assertEqual(fake_uuid('b'),
                         serve.resource_metadata.get('receiver_tenant_id'))
        self.assertEqual(sample.TYPE_DELTA, serve.type)

    def test_image_size_on_upload(self):
        counters = list(self.handler.process_notification(
            NOTIFICATION_UPLOAD))
        self.assertEqual(1, len(counters))
        upload = counters[0]
        self._verify_common_counter(upload, 'image.size',
                                    IMAGE_META['size'], fake_uuid('c'))
        self.assertEqual(sample.TYPE_GAUGE, upload.type)

    def test_image_size_on_update(self):
        counters = list(self.handler.process_notification(
            NOTIFICATION_UPDATE))
        self.assertEqual(1, len(counters))
        update = counters[0]
        self._verify_common_counter(update, 'image.size',
                                    IMAGE_META['size'], fake_uuid('c'))
        self.assertEqual(sample.TYPE_GAUGE, update.type)

    def test_image_size_on_delete(self):
        counters = list(self.handler.process_notification(
            NOTIFICATION_DELETE))
        self.assertEqual(1, len(counters))
        delete = counters[0]
        self._verify_common_counter(delete, 'image.size',
                                    IMAGE_META['size'], fake_uuid('c'))
        self.assertEqual(sample.TYPE_GAUGE, delete.type)

    def test_index_count(self):
        counters = list(self.handler.process_notification(
                        NOTIFICATION_TABLE_CREATE))
        self.assertEqual(1, len(counters))
        table = counters[0]
        self._verify_common_counter(table, 'magnetodb.table.index.count',
                                    2, fake_uuid('r'))
        self.assertEqual(fake_uuid('u'), table.user_id)
        self.assertEqual(fake_uuid('t'), table.project_id)
        self.assertEqual(sample.TYPE_GAUGE, table.type)

    def test_instance_create_ephemeral_disk_size(self):
        counters = list(self.handler.process_notification(
            INSTANCE_CREATE_END))
        self.assertEqual(4, len(counters))
        c = [item for item in counters
             if item.name == "disk.ephemeral.size"][0]
        self.assertEqual(INSTANCE_CREATE_END['payload']['ephemeral_gb'],
                         c.volume)

    def test_instance_create_memory(self):
        counters = list(self.handler.process_notification(
            INSTANCE_CREATE_END))
        self.assertEqual(4, len(counters))
        c = [item for item in counters if item.name == "memory"][0]
        self.assertEqual(INSTANCE_CREATE_END['payload']['memory_mb'],
                         c.volume)

    def test_instance_create_vcpus(self):
        counters = list(self.handler.process_notification(
            INSTANCE_CREATE_END))
        c = [item for item in counters if item.name == "vcpus"][0]
        self.assertEqual(INSTANCE_CREATE_END['payload']['vcpus'], c.volume)

    def test_instance_create_root_disk_size(self):
        counters = list(self.handler.process_notification(
            INSTANCE_CREATE_END))
        c = [item for item in counters if item.name == "disk.root.size"][0]
        self.assertEqual(INSTANCE_CREATE_END['payload']['root_gb'], c.volume)
