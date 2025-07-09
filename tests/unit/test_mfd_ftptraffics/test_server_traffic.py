# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

import pytest
from mfd_connect import RPyCConnection, SSHConnection
from mfd_connect.process import RemoteProcess
from mfd_ftp import FTPServerTraffic, ftp_server
from mfd_ftp.util.exceptions import FTPModuleExceptions
from mfd_typing import OSName


class TestFTPServer:
    @pytest.fixture()
    def ftpserver(self, mocker):
        conn = mocker.create_autospec(RPyCConnection)
        conn.get_os_name.return_value = OSName.LINUX
        ftp_server = FTPServerTraffic(
            connection=conn, ip="127.0.0.1", port=21, directory="/", username="admin", password="xxxx"
        )
        ftp_server._process = mocker.create_autospec(RemoteProcess)
        ftp_server._process.log_path = None
        return ftp_server

    @pytest.fixture()
    def ftpserver_ssh(self, mocker):
        conn = mocker.create_autospec(SSHConnection)
        conn.get_os_name.return_value = OSName.LINUX
        ftp_server = FTPServerTraffic(
            connection=conn, ip="127.0.0.1", port=21, directory="/", username="admin", password="xxxx"
        )
        ftp_server._process = mocker.create_autospec(RemoteProcess)
        ftp_server._process.log_path = None
        return ftp_server

    def test_start_server_ssh(self, ftpserver_ssh, mocker):
        with pytest.raises(FTPModuleExceptions, match="Python Executable cannot be None"):
            ftpserver_ssh.start()

    def test_start_server(self, ftpserver, mocker):
        process = mocker.create_autospec(RemoteProcess)
        ftp_server.start_remote_server_as_process = mocker.create_autospec(
            ftp_server.start_remote_server_as_process, return_value=process
        )
        ftpserver.start()
        ftp_server.start_remote_server_as_process.assert_called_once_with(
            connection=ftpserver._connection,
            ip="127.0.0.1",
            port=21,
            directory="/",
            username="admin",
            password="xxxx",
            python_executable=None,
            permissions=None,
        )

    def test_stop(self, ftpserver, mocker):
        ftpserver._process = mocker.MagicMock()
        mock_running = mocker.PropertyMock(side_effect=[True, False])
        type(ftpserver._process).running = mock_running
        timeout_mocker = mocker.patch("mfd_ftp.traffics.base.TimeoutCounter")
        timeout_mocker.return_value.__bool__.return_value = False
        ftpserver.stop()
        ftpserver._process.stop.assert_called_once()
        ftpserver._process.kill.assert_not_called()

    def test_stop_already_stopped(self, ftpserver, mocker):
        ftpserver._process = mocker.MagicMock()
        mock_running = mocker.PropertyMock(return_value=False)
        type(ftpserver._process).running = mock_running
        ftpserver.stop()
        ftpserver._process.stop.assert_not_called()
        ftpserver._process.kill.assert_not_called()

    def test_stop_failure(self, ftpserver, mocker):
        ftpserver._process = mocker.MagicMock()
        mock_running = mocker.PropertyMock(side_effect=[True, True])
        type(ftpserver._process).running = mock_running
        timeout_mocker = mocker.patch("mfd_ftp.traffics.base.TimeoutCounter")
        timeout_mocker.return_value.__bool__.return_value = True
        with pytest.raises(FTPModuleExceptions):
            ftpserver.stop()
        ftpserver._process.stop.assert_called_once()
        ftpserver._process.kill.assert_called_once()

    def test_stop_with_kill(self, ftpserver, mocker):
        ftpserver._process = mocker.MagicMock()
        mock_running = mocker.PropertyMock(side_effect=[True, False])
        type(ftpserver._process).running = mock_running
        timeout_mocker = mocker.patch("mfd_ftp.traffics.base.TimeoutCounter")
        timeout_mocker.return_value.__bool__.side_effect = [True, False]
        ftpserver.stop()
        ftpserver._process.stop.assert_called_once()
        ftpserver._process.kill.assert_called_once()

    def test_run(self, ftpserver, mocker):
        ftpserver.start = mocker.create_autospec(ftpserver.start)
        mock_running = mocker.PropertyMock(return_value=False)
        type(ftpserver._process).running = mock_running
        timeout_mocker = mocker.patch("mfd_ftp.traffics.base.TimeoutCounter")
        timeout_mocker.return_value.__bool__.return_value = False
        ftpserver.run(duration=1)
        ftpserver.start.assert_called_once()
