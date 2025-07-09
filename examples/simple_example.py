# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Example for FTP."""

import logging
from mfd_connect import RPyCConnection
from mfd_ftp import FTPClientTraffic, FTPServerTraffic
from mfd_traffic_manager import TrafficManager, Stream


def validate_files_transmitted(results: str, files_transmitted: int) -> bool:
    """Validate Files transmitted.

    :param results: Results from FTP Process
    :param files_transmitted: expected number of files transmitted
    :return: status of validation
    """
    ftp_files_transmitted = results.count("File was sent")
    if ftp_files_transmitted != files_transmitted:
        logging.debug("Number of files transmitted are not as expected")
        return False
    return True


server_conn = RPyCConnection(ip="x.x.x.x")
client_conn = RPyCConnection(ip="x.x.x.x")
ftp_server = FTPServerTraffic(
    connection=server_conn, ip="x.x.x.x", port=21, directory="/", username="xxxx", password="xxxx"
)
ftp_client = FTPClientTraffic(
    connection=client_conn,
    ip="x.x.x.x",
    port=21,
    username="xxxx",
    password="xxxx",
    task="send",
    source="source.txt",
    destination="destination.txt",
)
manager = TrafficManager()
stream = Stream(clients=[ftp_client], server=ftp_server, name="Stream1")
manager.add_stream(stream)
manager.start(name="Stream1")
manager.stop(name="Stream1")
validation_criteria = {validate_files_transmitted: {"files_transmitted": 1}}
print(manager.validate(name="Stream1", clients_validation_criteria=validation_criteria))
