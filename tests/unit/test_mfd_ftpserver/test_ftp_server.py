from mfd_ftp import server


class TestFTPServer:
    def test_popen_called(self, mocker):
        popen_mock = mocker.patch("mfd_ftp.server.ftp_server.subprocess.Popen", create_autospec=True)
        mocker.patch("mfd_ftp.server.ftp_server.sys.executable", create_autospec=True)
        server.start_server_as_process(
            ip="127.0.0.1", port=69, directory="/", username="unittest", password="unitpass", permissions="test"
        )
        popen_mock.assert_called_once()
