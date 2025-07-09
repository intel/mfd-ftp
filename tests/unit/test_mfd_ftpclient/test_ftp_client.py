from mfd_ftp import ftp_client


class TestFTPClient:
    def test_popen_called(self, mocker):
        popen_mock = mocker.patch("mfd_ftp.client.ftp_client.subprocess.Popen", instance=True)
        mocker.patch("mfd_ftp.client.ftp_client.sys.executable", create_autospec=True)
        ftp_client.start_client_as_process(
            ip="127.0.0.1",
            port=69,
            task="send",
            source="/",
            destination="/",
            username="unittest",
            password="unittestpass",
        )
        popen_mock.assert_called_once()
