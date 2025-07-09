# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

"""Module for testing FTPUtils."""

import ftplib

import pytest

from mfd_ftp.util import FTPUtils
from mfd_ftp.util.exceptions import FTPModuleExceptions


class TestFTPUtils:
    @pytest.fixture()
    def ftputil(self):
        return FTPUtils("10.10.10.10", "test", "test")

    @pytest.fixture()
    def ftplib_fixture(self, mocker):
        mock_ftplib = mocker.MagicMock()
        mocker.patch("ftplib.FTP", new=mock_ftplib)

    @pytest.mark.usefixtures("ftplib_fixture")
    def test__ftp_login(self, ftputil):
        assert ftputil._ftp_login() is not None

    def test__ftp_login_failure(self, ftputil, mocker):
        mock_ftplib = mocker.MagicMock(side_effect=ftplib.all_errors)
        mocker.patch("ftplib.FTP", new=mock_ftplib)
        with pytest.raises(FTPModuleExceptions):
            ftputil._ftp_login()

    @pytest.mark.parametrize(
        "folder_to_check, return_folder, status", [("test", "test", True), ["test", "test2", False]]
    )
    def test_is_directory_on_ftp(self, ftputil, mocker, folder_to_check, return_folder, status):
        ftputil.return_dirs = mocker.Mock(return_value=[return_folder])
        assert ftputil.is_directory_on_ftp(folder_to_check) is status

    @pytest.mark.usefixtures("ftplib_fixture")
    def test_copy_files_to_ftp(self, ftputil, mocker):
        mocker.patch("os.listdir", new=mocker.Mock(return_value=["test"]))
        path_os = mocker.Mock()
        mocker.patch("os.path", new=path_os)
        mocker.patch("builtins.open", new=mocker.mock_open())
        path_os.join.return_value = "test"
        assert ftputil.copy_files_to_ftp("", "") is True

    def test_copy_files_to_ftp_failure(self, ftputil, mocker):
        mock_ftplib = mocker.MagicMock(side_effect=ftplib.all_errors)
        mocker.patch("ftplib.FTP", new=mock_ftplib)
        with pytest.raises(FTPModuleExceptions):
            ftputil.copy_files_to_ftp("", "")

    def test_return_dirs_failure(self, ftputil, mocker):
        mock_ftplib = mocker.MagicMock(side_effect=ftplib.all_errors)
        mocker.patch("ftplib.FTP", new=mock_ftplib)
        with pytest.raises(FTPModuleExceptions):
            ftputil.return_dirs()

    def test_return_dirs(self, ftputil, mocker):
        mock_ftplib = mocker.MagicMock()
        mocker.patch("ftplib.FTP", new=mock_ftplib)
        assert ftputil.return_dirs() == []
        assert mock_ftplib().__enter__().retrlines.called
