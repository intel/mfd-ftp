# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

from mfd_ftp import ftp_server

p = ftp_server.start_server_as_process(ip="127.0.0.1", port=21, directory="/", username="root", password="***")
