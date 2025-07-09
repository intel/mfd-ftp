# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

import logging
from textwrap import dedent

import pytest
from mfd_connect import RPyCConnection, SSHConnection
from mfd_connect.process import RemoteProcess
from mfd_ftp import FTPClientTraffic, ftp_client
from mfd_ftp.util.exceptions import FTPModuleExceptions
from mfd_typing import OSName


def validate_files_transmitted(ftp_results: str, files_transmitted: int) -> bool:
    """Validate Files transmitted.

    :param results: Result from FTP Process
    :param files_transmitted: expected number of files transmitted
    :return: status of validation
    """
    ftp_files_transmitted = ftp_results.count("File was sent")
    if ftp_files_transmitted != files_transmitted:
        logging.debug("Number of files transmitted are not as expected")
        return False
    return True


class TestFTPClient:
    @pytest.fixture()
    def ftpclient(self, mocker):
        conn = mocker.create_autospec(RPyCConnection)
        conn.get_os_name.return_value = OSName.LINUX
        ftp_client = FTPClientTraffic(
            connection=conn,
            ip="127.0.0.1",
            port=21,
            username="admin",
            password="xxxx",
            task="send",
            source="source.txt",
            destination="destination.txt",
        )
        ftp_client._process = mocker.create_autospec(RemoteProcess)
        ftp_client._process.log_path = None
        return ftp_client

    @pytest.fixture()
    def ftpclient_ssh(self, mocker):
        conn = mocker.create_autospec(SSHConnection)
        conn.get_os_name.return_value = OSName.LINUX
        ftp_client = FTPClientTraffic(
            connection=conn,
            ip="127.0.0.1",
            port=21,
            username="admin",
            password="xxxx",
            task="send",
            source="source.txt",
            destination="destination.txt",
        )
        ftp_client._process = mocker.create_autospec(RemoteProcess)
        ftp_client._process.log_path = None
        return ftp_client

    def test_start_client_ssh(self, ftpclient_ssh, mocker):
        with pytest.raises(FTPModuleExceptions, match="Python Executable cannot be None"):
            ftpclient_ssh.start()

    def test_start_client(self, ftpclient, mocker):
        process = mocker.create_autospec(RemoteProcess)
        ftp_client.start_remote_client_as_process = mocker.create_autospec(
            ftp_client.start_remote_client_as_process, return_value=process
        )
        ftpclient.start()
        ftp_client.start_remote_client_as_process.assert_called_once_with(
            connection=ftpclient._connection,
            ip="127.0.0.1",
            port=21,
            username="admin",
            password="xxxx",
            task="send",
            source="source.txt",
            destination="destination.txt",
            python_executable=None,
            timeout=None,
        )

    def test_validate(self, ftpclient, mocker):
        mock_running = mocker.PropertyMock(return_value=False)
        type(ftpclient._process).running = mock_running
        output = dedent(
            """
            Sending file
            elapsed_time: 0.0015755221247673035, transfer_speed: 0
            File was sent"""
        )
        process_output = mocker.PropertyMock(return_value=output)
        type(ftpclient._process).stdout_text = process_output
        assert ftpclient.validate() is True
        validation_criteria = {validate_files_transmitted: {"files_transmitted": 0}}
        assert ftpclient.validate(validation_criteria) is False
        validation_criteria = {validate_files_transmitted: {"files_transmitted": 1}}
        assert ftpclient.validate(validation_criteria) is True

    def test_validate_process_still_running(self, ftpclient, mocker):
        mock_running = mocker.PropertyMock(return_value=True)
        type(ftpclient._process).running = mock_running
        output = dedent(
            """
            Sending file
            elapsed_time: 0.0015755221247673035, transfer_speed: 0
            File was sent"""
        )
        process_output = mocker.PropertyMock(return_value=output)
        type(ftpclient._process).stdout_text = process_output
        with pytest.raises(FTPModuleExceptions, match="Process is still running"):
            ftpclient.validate()

    def test_stop(self, ftpclient, mocker):
        ftpclient._process = mocker.MagicMock()
        mock_running = mocker.PropertyMock(side_effect=[True, False])
        type(ftpclient._process).running = mock_running
        timeout_mocker = mocker.patch("mfd_ftp.traffics.base.TimeoutCounter")
        timeout_mocker.return_value.__bool__.return_value = False
        ftpclient.stop()
        ftpclient._process.stop.assert_called_once()
        ftpclient._process.kill.assert_not_called()

    def test_stop_already_stopped(self, ftpclient, mocker):
        ftpclient._process = mocker.MagicMock()
        mock_running = mocker.PropertyMock(return_value=False)
        type(ftpclient._process).running = mock_running
        ftpclient.stop()
        ftpclient._process.stop.assert_not_called()
        ftpclient._process.kill.assert_not_called()

    def test_stop_failure(self, ftpclient, mocker):
        ftpclient._process = mocker.MagicMock()
        mock_running = mocker.PropertyMock(side_effect=[True, True])
        type(ftpclient._process).running = mock_running
        timeout_mocker = mocker.patch("mfd_ftp.traffics.base.TimeoutCounter")
        timeout_mocker.return_value.__bool__.return_value = True
        with pytest.raises(FTPModuleExceptions):
            ftpclient.stop()
        ftpclient._process.stop.assert_called_once()
        ftpclient._process.kill.assert_called_once()

    def test_stop_with_kill(self, ftpclient, mocker):
        ftpclient._process = mocker.MagicMock()
        mock_running = mocker.PropertyMock(side_effect=[True, False])
        type(ftpclient._process).running = mock_running
        timeout_mocker = mocker.patch("mfd_ftp.traffics.base.TimeoutCounter")
        timeout_mocker.return_value.__bool__.side_effect = [True, False]
        ftpclient.stop()
        ftpclient._process.stop.assert_called_once()
        ftpclient._process.kill.assert_called_once()

    def test_run(self, ftpclient, mocker):
        ftpclient.start = mocker.create_autospec(ftpclient.start)
        mock_running = mocker.PropertyMock(return_value=False)
        type(ftpclient._process).running = mock_running
        timeout_mocker = mocker.patch("mfd_ftp.traffics.base.TimeoutCounter")
        timeout_mocker.return_value.__bool__.return_value = False
        ftpclient.run(duration=1)
        ftpclient.start.assert_called_once()
