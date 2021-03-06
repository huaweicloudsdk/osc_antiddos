#   Copyright 2016 Huawei, Inc. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
import random
import uuid

import datetime
import mock
from antiddosclient.common import exceptions
from antiddosclient.common import resource as base_resource
from antiddosclient.osc.v1 import antiddos
from antiddosclient.tests import base
from antiddosclient.v1 import antiddos_mgr
from antiddosclient.v1 import resource
from keystoneauth1 import exceptions as execs


class TestAntiDDos(base.AntiDDosV1BaseTestCase):
    """"""

    instances = [
        {
            "floating_ip_id": "1867f954-fc11-4202-8247-6af2144867ea",
            "floating_ip_address": "192.168.42.221",
            "network_type": "EIP",
            "status": "notConfig"
        },
        {
            "floating_ip_id": "49c6af49-9ace-42e6-ab89-1eee1f4ac821",
            "floating_ip_address": "192.168.35.152",
            "network_type": "EIP",
            "status": "normal"
        },
        {
            "floating_ip_id": "7a8dc957-083b-499d-b7cf-6fa48f4880c5",
            "floating_ip_address": "192.168.42.222",
            "network_type": "EIP",
            "status": "notConfig"
        },
        {
            "floating_ip_id": "7c6676a0-b281-4163-9d0d-cb6485ae9860",
            "floating_ip_address": "192.168.44.69",
            "network_type": "EIP",
            "status": "normal"
        },
        {
            "floating_ip_id": "969c1d48-6a92-4ef1-b66c-b17c7e7d7ce7",
            "floating_ip_address": "192.168.47.192",
            "network_type": "EIP",
            "status": "notConfig"
        }
    ]

    antiddos = {
        "enable_L7": True,
        "traffic_pos_id": 1,
        "http_request_pos_id": 1,
        "cleaning_access_pos_id": 1,
        "app_type_id": 1,
        "floating_ip_id": "floating_ip_id_1"
    }

    daily_report = [
        {
            "period_start": 1472713370609,
            "bps_in": 0,
            "bps_attack": 0,
            "total_bps": 0,
            "pps_in": 0,
            "pps_attack": 0,
            "total_pps": 0
        },
        {
            "period_start": 1472713670609,
            "bps_in": 0,
            "bps_attack": 0,
            "total_bps": 0,
            "pps_in": 0,
            "pps_attack": 0,
            "total_pps": 0
        }
    ]

    def __init__(self, *args, **kwargs):
        super(TestAntiDDos, self).__init__(*args, **kwargs)

    def setUp(self):
        super(TestAntiDDos, self).setUp()
        self._antiddos = self.get_fake_antiddos()
        self.mocked_find = mock.patch.object(
            antiddos_mgr.AntiDDosManager, "find", return_value=self._antiddos
        )

    def get_fake_antiddos_list(self, count=0):
        if count == 0:
            results = [resource.AntiDDos(None, instance, attached=True)
                       for instance in self.instances]
        else:
            results = [resource.AntiDDos(None, instance, attached=True)
                       for instance in self.instances[:count]]
        return base_resource.ListWithMeta(results, "Request-Id")

    def get_fake_antiddos(self, instance=None):
        if instance:
            _antiddos = resource.AntiDDos(None, instance, attached=True)
        else:
            _antiddos = resource.AntiDDos(None, self.antiddos, attached=True)
        return _antiddos

    def get_fake_task_response(self, task_id=None):
        return {
            "task_id": task_id or uuid.uuid4().hex,
        }


@mock.patch.object(antiddos_mgr.AntiDDosManager, "_get")
class TestAntiDDosConfig(TestAntiDDos):
    def setUp(self):
        super(TestAntiDDosConfig, self).setUp()
        self.cmd = antiddos.QueryAntiDDosConfig(self.app, None)

    def test_antiddos_config_list(self, mocked_get):
        configs = {
            "traffic_limited_list": [
                {
                    "traffic_pos_id": 1,
                    "traffic_per_second": 10,
                    "packet_per_second": 2000
                },
                {
                    "traffic_pos_id": 2,
                    "traffic_per_second": 30,
                    "packet_per_second": 6000
                }
            ],
            "http_limited_list": [
                {
                    "http_request_pos_id": 1,
                    "http_packet_per_second": 100
                },
                {
                    "http_request_pos_id": 2,
                    "http_packet_per_second": 150
                }
            ],
            "connection_limited_list": [
                {
                    "cleaning_access_pos_id": 1,
                    "new_connection_limited": 10,
                    "total_connection_limited": 30
                },
                {
                    "cleaning_access_pos_id": 2,
                    "new_connection_limited": 20,
                    "total_connection_limited": 100
                },
                {
                    "cleaning_access_pos_id": 3,
                    "new_connection_limited": 30,
                    "total_connection_limited": 200
                },
                {
                    "cleaning_access_pos_id": 4,
                    "new_connection_limited": 40,
                    "total_connection_limited": 250
                }
            ]
        }

        mocked_get.return_value = resource.AntiDDosConfig(None, configs)
        columns, data = self.cmd.take_action(None)
        mocked_get.assert_called_once_with(
            "/antiddos/query_config_list",
            resource_class=resource.AntiDDosConfig
        )

        self.assertEquals(columns, ["Traffic limited list",
                                    "HTTP limited list",
                                    "Connection limited list", ])

        expected = (
            "\n".join(("packet_per_second='2000', traffic_per_second='10', "
                       "traffic_pos_id='1'",
                       "packet_per_second='6000', traffic_per_second='30', "
                       "traffic_pos_id='2'",
                       )),
            "\n".join(("http_packet_per_second='100', http_request_pos_id='1'",
                       "http_packet_per_second='150', http_request_pos_id='2'",
                       )),
            "\n".join(
                ("cleaning_access_pos_id='1', new_connection_limited='10', "
                 "total_connection_limited='30'",
                 "cleaning_access_pos_id='2', new_connection_limited='20', "
                 "total_connection_limited='100'",
                 "cleaning_access_pos_id='3', new_connection_limited='30', "
                 "total_connection_limited='200'",
                 "cleaning_access_pos_id='4', new_connection_limited='40', "
                 "total_connection_limited='250'",
                 )),
        )
        self.assertEquals(expected, data)


@mock.patch.object(antiddos_mgr.AntiDDosManager, "_delete")
class TestAntiDDosClose(TestAntiDDos):
    def setUp(self):
        super(TestAntiDDosClose, self).setUp()
        self.cmd = antiddos.CloseAntiDDos(self.app, None)

    def test_antiddos_close(self, mocked_delete):
        args = ["floating_ip_id_1"]
        verify_args = [("floating_ip", "floating_ip_id_1"), ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)

        with self.mocked_find:
            task_id = "fake_task_id"
            mocked_delete.return_value = self.get_fake_task_response(task_id)
            result = self.cmd.take_action(parsed_args)
            url = "/antiddos/" + self._antiddos.floating_ip_id
            mocked_delete.assert_called_once_with(url)
            self.assertEqual(result, "Request Received, task id: %s" % task_id)


@mock.patch.object(antiddos_mgr.AntiDDosManager, "_create")
class TestAntiDDosOpen(TestAntiDDos):
    def setUp(self):
        super(TestAntiDDosOpen, self).setUp()
        self.cmd = antiddos.OpenAntiDDos(self.app, None)

    def test_antiddos_open_with_enabled_l7(self, mocked):
        args = [
            "floating_ip_id_1",
            "--enable-CC",
            "--maximum-service-traffic", "70",
            "--http-request-rate", "240",
        ]
        verify_args = [
            ("floating_ip", "floating_ip_id_1"),
            ("enable_l7", True),
            ("maximum_service_traffic", 70),
            ("http_request_rate", 240),
        ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)

        with self.mocked_find:
            task_id = "fake_task_id"
            mocked.return_value = self.get_fake_task_response(task_id)
            result = self.cmd.take_action(parsed_args)
            url = "/antiddos/" + self._antiddos.floating_ip_id

            data = {
                "enable_L7": True,
                "traffic_pos_id": 4,
                "http_request_pos_id": 3,
                "cleaning_access_pos_id": 8,
                "app_type_id": 1
            }
            mocked.assert_called_once_with(url, data=data, raw=True)
            self.assertEqual(result, "Request Received, task id: %s" % task_id)

    def test_antiddos_open_with_disabled_l7(self, mocked):
        args = [
            "floating_ip_id_1",
            "--disable-CC",
            "--maximum-service-traffic", "10",
            "--http-request-rate", "100",
        ]
        verify_args = [
            ("floating_ip", "floating_ip_id_1"),
            ("enable_l7", False),
            ("maximum_service_traffic", 10),
            ("http_request_rate", 100),
        ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)

        with self.mocked_find:
            task_id = "fake_task_id"
            mocked.return_value = self.get_fake_task_response(task_id)
            result = self.cmd.take_action(parsed_args)
            url = "/antiddos/" + self._antiddos.floating_ip_id

            data = {
                "enable_L7": False,
                "traffic_pos_id": 1,
                "http_request_pos_id": 15,
                "cleaning_access_pos_id": 8,
                "app_type_id": 1
            }
            mocked.assert_called_once_with(url, data=data, raw=True)
            self.assertEqual(result, "Request Received, task id: %s" % task_id)


class TestAntiDDosShow(TestAntiDDos):
    def setUp(self):
        super(TestAntiDDosShow, self).setUp()
        self.cmd = antiddos.ShowAntiDDos(self.app, None)

    @mock.patch.object(antiddos_mgr.AntiDDosManager, "_list")
    @mock.patch.object(antiddos_mgr.AntiDDosManager, "_get")
    def test_antiddos_show_with_ip(self, mocked_get, mocked_list):
        ip = "192.168.42.221"
        args = [ip]
        verify_args = [("floating_ip", ip), ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        antiddos_list = self.get_fake_antiddos_list()
        mocked_list.return_value = antiddos_list

        _antiddos = self.get_fake_antiddos()
        mocked_get.return_value = _antiddos
        columns, data = self.cmd.take_action(parsed_args)
        mocked_list.assert_called_once_with(
            "/antiddos", params={"ip": ip}, key='ddosStatus'
        )
        self.assertEqual(columns, resource.AntiDDos.show_column_names)
        self.assertEqual(data, _antiddos.get_display_data(columns))

    @mock.patch.object(antiddos_mgr.AntiDDosManager, "_list")
    @mock.patch.object(antiddos_mgr.AntiDDosManager, "_get")
    def test_antiddos_find_return_single_result(self, mocked_get, mocked_list):
        ip = "192.168.42.221"
        args = [ip]
        verify_args = [("floating_ip", ip), ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)

        antiddos_list = self.get_fake_antiddos_list(1)
        mocked_list.return_value = antiddos_list

        _antiddos = self.get_fake_antiddos()
        mocked_get.return_value = _antiddos
        columns, data = self.cmd.take_action(parsed_args)
        mocked_list.assert_called_once_with(
            "/antiddos", params={"ip": ip}, key='ddosStatus'
        )
        self.assertEqual(columns, resource.AntiDDos.show_column_names)
        self.assertEqual(data, _antiddos.get_display_data(columns))

    @mock.patch.object(antiddos_mgr.AntiDDosManager, "_list")
    def test_antiddos_show_multiple_ip_matched(self, mocked_list):
        ip = "192.168.42.22"
        args = [ip]
        verify_args = [("floating_ip", ip), ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        mocked_list.return_value = self.get_fake_antiddos_list()
        self.assertRaises(
            exceptions.NotUniqueMatch, self.cmd.take_action, parsed_args
        )

    @mock.patch.object(antiddos_mgr.AntiDDosManager, "_get")
    def test_antiddos_show_with_id(self, mocked_get):
        _antiddos = self.get_fake_antiddos()
        floating_ip_id = _antiddos.floating_ip_id
        verify_args = [("floating_ip", floating_ip_id), ]
        parsed_args = self.check_parser(
            self.cmd, [floating_ip_id], verify_args
        )

        mocked_get.return_value = _antiddos
        columns, data = self.cmd.take_action(parsed_args)
        mocked_get.assert_called_once_with(
            "/antiddos/" + floating_ip_id
        )
        self.assertEqual(columns, resource.AntiDDos.show_column_names)
        self.assertEqual(data, _antiddos.get_display_data(columns))

    @mock.patch.object(antiddos_mgr.AntiDDosManager, "_list")
    def test_antiddos_show_not_found_raised(self, mocked_list):
        ip = "10.10.10.10"
        args = [ip]
        verify_args = [("floating_ip", ip), ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        mocked_list.return_value = base_resource.TupleWithMeta([], "RID")
        self.assertRaises(
            execs.NotFound, self.cmd.take_action, parsed_args
        )


@mock.patch.object(antiddos_mgr.AntiDDosManager, "_update_all")
class TestAntiDDosSet(TestAntiDDos):
    def setUp(self):
        super(TestAntiDDosSet, self).setUp()
        self.cmd = antiddos.SetAntiDDos(self.app, None)

    def test_antiddos_open_with_enabled_l7(self, mocked):
        args = [
            "floating_ip_id_1",
            "--enable-CC",
            "--maximum-service-traffic", "70",
            "--http-request-rate", "240",
        ]
        verify_args = [
            ("floating_ip", "floating_ip_id_1"),
            ("enable_l7", True),
            ("maximum_service_traffic", 70),
            ("http_request_rate", 240),
        ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)

        with self.mocked_find:
            task_id = "fake_task_id"
            mocked.return_value = self.get_fake_task_response(task_id)
            result = self.cmd.take_action(parsed_args)
            url = "/antiddos/" + self._antiddos.floating_ip_id

            data = {
                "enable_L7": True,
                "traffic_pos_id": 4,
                "http_request_pos_id": 3,
                "cleaning_access_pos_id": 8,
                "app_type_id": 1
            }
            mocked.assert_called_once_with(url, data, raw=True)
            self.assertEqual(result, "Request Received, task id: %s" % task_id)


@mock.patch.object(antiddos_mgr.AntiDDosManager, "_get")
class TestAntiDDosTaskShow(TestAntiDDos):
    def setUp(self):
        super(TestAntiDDosTaskShow, self).setUp()
        self.cmd = antiddos.ShowAntiDDosTask(self.app, None)

    def test_antiddos_open_with_enabled_l7(self, mocked):
        args = [
            "fake_task_id",
        ]
        verify_args = [
            ("task_id", "fake_task_id"),
        ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        task = resource.AntiDDosTask(
            None, dict(task_status="running", task_msg=""), "request-id"
        )
        mocked.return_value = task
        columns, data = self.cmd.take_action(parsed_args)
        mocked.assert_called_once_with("/query_task_status",
                                       params={'task_id': 'fake_task_id'},
                                       resource_class=resource.AntiDDosTask)
        self.assertEqual(columns, resource.AntiDDosTask.list_column_names)
        self.assertEqual(data, ("running", ""))


@mock.patch.object(antiddos_mgr.AntiDDosManager, "_list")
class TestAntiDDosStatusList(TestAntiDDos):
    def setUp(self):
        super(TestAntiDDosStatusList, self).setUp()
        self.cmd = antiddos.ListAntiDDosStatus(self.app, None)

    def test_list_antiddos_status_with_all_options(self, mocked_list):
        args = [
            "--ip", "192.168.42.221",
            "--status", "notConfig",
            "--limit", "10",
            "--offset", "10"
        ]
        verify_args = (
            ("ip", "192.168.42.221"),
            ("status", "notConfig"),
            ("limit", 10),
            ("offset", 10),
        )
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        status_list = self.get_fake_antiddos_list()
        mocked_list.return_value = status_list
        columns, data = self.cmd.take_action(parsed_args)

        t = zip(*verify_args)
        mocked_list.assert_called_once_with(
            "/antiddos", params=dict(zip(t[0], t[1])), key='ddosStatus'
        )
        self.assertEqual(columns, resource.AntiDDos.list_column_names)

        expect_data = []
        for instance in self.instances:
            expect_data.append((instance["floating_ip_id"],
                                instance["floating_ip_address"],
                                instance["network_type"],
                                instance["status"]))
        self.assertEqual(list(data), expect_data)


@mock.patch.object(antiddos_mgr.AntiDDosManager, "_get")
class TestAntiDDosStatusShow(TestAntiDDos):
    def setUp(self):
        super(TestAntiDDosStatusShow, self).setUp()
        self.cmd = antiddos.ShowAntiDDosStatus(self.app, None)

    def test_antiddos_show_with_id(self, mocked_get):
        floating_ip_id = self._antiddos.floating_ip_id
        verify_args = [("floating_ip", floating_ip_id), ]
        parsed_args = self.check_parser(
            self.cmd, [floating_ip_id], verify_args
        )

        with self.mocked_find:
            mocked_get.return_value = resource.AntiDDosStatus(
                None, dict(status='status'), attached=True
            )
            columns, data = self.cmd.take_action(parsed_args)
            mocked_get.assert_called_once_with(
                "/antiddos/" + floating_ip_id + "/status",
                resource_class=resource.AntiDDosStatus
            )

            self.assertEqual(columns,
                             resource.AntiDDosStatus.show_column_names)
            self.assertEqual(tuple(data), ('status',))


@mock.patch.object(antiddos_mgr.AntiDDosManager, "_list")
class TestListAntiDDosDailyReport(TestAntiDDos):
    def setUp(self):
        super(TestListAntiDDosDailyReport, self).setUp()
        self.cmd = antiddos.ListAntiDDosDailyReport(self.app, None)

    def test_list_antiddos_daily_reports(self, mocked_list):
        floating_ip_id = self._antiddos.floating_ip_id
        verify_args = [("floating_ip", floating_ip_id), ]
        parsed_args = self.check_parser(
            self.cmd, [floating_ip_id], verify_args
        )

        with self.mocked_find:
            reports = [resource.AntiDDosDailyReport(None, r, attached=True)
                       for r in self.daily_report]

            mocked_list.return_value = reports
            columns, data = self.cmd.take_action(parsed_args)

            mocked_list.assert_called_once_with(
                "/antiddos/" + floating_ip_id + "/daily",
                key="data",
                resource_class=resource.AntiDDosDailyReport
            )
            expect_columns = resource.AntiDDosDailyReport.list_column_names
            self.assertEqual(columns, expect_columns)
            expect_data = (report.get_display_data(columns)
                           for report in reports)
            self.assertEqual(tuple(data), tuple(expect_data))


@mock.patch.object(antiddos_mgr.AntiDDosManager, "_list")
class TestListAntiDDosLogs(TestAntiDDos):
    def __init__(self, *args, **kwargs):
        super(TestListAntiDDosLogs, self).__init__(*args, **kwargs)
        self.logs = [
            {
                "start_time": 1473217200000,
                "end_time": 1473242400000,
                "status": 1,
                "trigger_bps": 51106,
                "trigger_pps": 2600,
                "trigger_http_pps": 3589
            }
        ]

    def setUp(self):
        super(TestListAntiDDosLogs, self).setUp()
        self.cmd = antiddos.ListAntiDDosLogs(self.app, None)

    def test_list_antiddos_logs_with_all_options(self, mocked_list):
        floating_ip_id = self._antiddos.floating_ip_id
        args = [
            "--limit", "10",
            "--offset", "10",
            "--sort-dir", "asc",
            floating_ip_id
        ]
        verify_args = [
            ("floating_ip", floating_ip_id),
            ("limit", 10),
            ("offset", 10),
        ]
        parsed_args = self.check_parser(
            self.cmd, args, verify_args
        )

        with self.mocked_find:
            logs = [resource.AntiDDosLog(None, log, attached=True)
                    for log in self.logs]

            mocked_list.return_value = logs
            columns, data = self.cmd.take_action(parsed_args)
            mocked_list.assert_called_once_with(
                "/antiddos/" + floating_ip_id + "/logs",
                key="logs",
                params=dict(limit=10, offset=10, sort_dir="asc"),
                resource_class=resource.AntiDDosLog
            )
            expect_columns = resource.AntiDDosLog.list_column_names
            self.assertEqual(columns, expect_columns)
            expect_data = (
                (
                    "2016-09-07 11:00:00",
                    "2016-09-07 18:00:00",
                    "Packet Cleaning",
                    51106,
                    2600,
                    3589
                ),
            )

            self.assertEqual(tuple(data), expect_data)


@mock.patch.object(antiddos_mgr.AntiDDosManager, "_get")
class TestListAntiDDosWeeklyReport(TestAntiDDos):
    def setUp(self):
        super(TestListAntiDDosWeeklyReport, self).setUp()
        self.cmd = antiddos.ListAntiDDosWeeklyReport(self.app, None)

    def test_list_antiddos_weekly_reports(self, mocked_list):
        parsed_args = self.check_parser(
            self.cmd,
            ["--start-date", "2017-02-08"],
            [("start_date", datetime.datetime(2017, 2, 8)), ],
        )

        weekly = {
            "ddos_intercept_times": 23,
            "weekdata": [
                {
                    "ddos_intercept_times": 0,
                    "ddos_blackhole_times": 0,
                    "max_attack_bps": 0,
                    "max_attack_conns": 0,
                    "period_start_date": 1474214461651
                },
                {
                    "ddos_intercept_times": 0,
                    "ddos_blackhole_times": 0,
                    "max_attack_bps": 0,
                    "max_attack_conns": 0,
                    "period_start_date": 1474300861651
                }
            ],
            "top10": [
                {
                    "floating_ip_address": "192.168.44.69",
                    "times": 23
                }
            ]
        }

        report = resource.AntiDDosWeeklyReport(None, weekly, attached=True)
        mocked_list.return_value = report
        columns, data = self.cmd.take_action(parsed_args)

        mocked_list.assert_called_once_with(
            "/antiddos/weekly",
            params=dict(period_start_date=1486483200000),
            resource_class=resource.AntiDDosWeeklyReport
        )
        expect_columns = resource.AntiDDosWeeklyReport.show_column_names
        self.assertEqual(columns, expect_columns)

        expected = (
            23,
            (
                "ddos_blackhole_times='0', ddos_intercept_times='0', "
                "max_attack_bps='0', max_attack_conns='0', "
                "period_start_date='2016-09-19 00:01:01'\n"
                "ddos_blackhole_times='0', ddos_intercept_times='0', "
                "max_attack_bps='0', max_attack_conns='0', "
                "period_start_date='2016-09-20 00:01:01'"),
            "floating_ip_address='192.168.44.69', times='23'",
        )
        self.assertEqual(expected, data)
