# Copyright 2018 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import mock
import os

from os_vif import objects
from oslo_config import cfg

from kuryr_kubernetes.objects import vif
from kuryr_kubernetes.tests import base as test_base
from kuryr_kubernetes.tests.unit import kuryr_fixtures as k_fix
from kuryr_kubernetes import utils

CONF = cfg.CONF


class TestUtils(test_base.TestCase):
    @mock.patch('socket.gethostname')
    def test_get_node_name_socket(self, m_gethostname):
        try:
            del os.environ['KUBERNETES_NODE_NAME']
        except KeyError:
            pass

        m_gethostname.return_value = 'foo'
        res = utils.get_node_name()
        self.assertEqual('foo', res)
        m_gethostname.assert_called_once_with()

    @mock.patch('socket.gethostname')
    def test_get_node_name_envvar(self, m_gethostname):
        os.environ['KUBERNETES_NODE_NAME'] = 'bar'
        m_gethostname.return_value = 'foo'
        res = utils.get_node_name()
        self.assertEqual('bar', res)
        m_gethostname.assert_not_called()

    @mock.patch('requests.get')
    def test_get_leader_name(self, m_get):
        m_get.return_value = mock.Mock(json=mock.Mock(
            return_value={'name': 'foo'}))
        res = utils.get_leader_name()
        m_get.assert_called_once_with(
            'http://localhost:%d' % CONF.kubernetes.controller_ha_elector_port)
        self.assertEqual('foo', res)

    @mock.patch('requests.get')
    def test_get_leader_name_malformed(self, m_get):
        m_get.return_value = mock.Mock(json=mock.Mock(
            return_value={'name2': 'foo'}))
        res = utils.get_leader_name()
        m_get.assert_called_once_with(
            'http://localhost:%d' % CONF.kubernetes.controller_ha_elector_port)
        self.assertIsNone(res)

    @mock.patch('requests.get')
    def test_get_leader_name_exc(self, m_get):
        m_get.side_effect = Exception
        res = utils.get_leader_name()
        m_get.assert_called_once_with(
            'http://localhost:%d' % CONF.kubernetes.controller_ha_elector_port)
        self.assertIsNone(res)

    @mock.patch('kuryr_kubernetes.os_vif_util.neutron_to_osvif_network')
    @mock.patch('kuryr_kubernetes.os_vif_util.neutron_to_osvif_subnet')
    def test_get_subnet(self, m_osv_subnet, m_osv_network):
        neutron = self.useFixture(k_fix.MockNeutronClient()).client

        subnet = mock.MagicMock()
        network = mock.MagicMock()
        subnet_id = mock.sentinel.subnet_id
        network_id = mock.sentinel.network_id

        neutron_subnet = {'network_id': network_id}
        neutron_network = mock.sentinel.neutron_network

        neutron.show_subnet.return_value = {'subnet': neutron_subnet}
        neutron.show_network.return_value = {'network': neutron_network}

        m_osv_subnet.return_value = subnet
        m_osv_network.return_value = network

        ret = utils.get_subnet(subnet_id)

        self.assertEqual(network, ret)
        neutron.show_subnet.assert_called_once_with(subnet_id)
        neutron.show_network.assert_called_once_with(network_id)
        m_osv_subnet.assert_called_once_with(neutron_subnet)
        m_osv_network.assert_called_once_with(neutron_network)
        network.subnets.objects.append.assert_called_once_with(subnet)

    def test_extract_pod_annotation(self):
        vif_obj = objects.vif.VIFBase()
        ps = vif.PodState(default_vif=vif_obj)
        d = ps.obj_to_primitive()
        result = utils.extract_pod_annotation(d)
        self.assertEqual(vif.PodState.obj_name(), result.obj_name())
        self.assertEqual(vif_obj, result.default_vif)

    def test_extract_pod_annotation_convert(self):
        vif_obj = objects.vif.VIFBase()
        d = vif_obj.obj_to_primitive()
        result = utils.extract_pod_annotation(d)
        self.assertEqual(vif.PodState.obj_name(), result.obj_name())
        self.assertEqual(vif_obj, result.default_vif)
