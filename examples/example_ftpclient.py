# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

from mfd_ftp import ftp_client


def ftp_client_send_file() -> None:
    client = ftp_client.start_client_as_process(
        ip="0.0.0.0",
        port=21,
        task="send",
        source="source.txt",
        destination="destination.txt",
        username="root",
        password="root",
    )


def ftp_client_receive_file() -> None:
    client = ftp_client.start_client_as_process(
        ip="0.0.0.0",
        port=21,
        task="receive",
        source="source.txt",
        destination="destination.txt",
        username="root",
        password="root",
    )


if __name__ == "__main__":
    ftp_client_send_file()
