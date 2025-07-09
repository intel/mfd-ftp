# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

from mfd_ftp.util import FTPUtils
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

util = FTPUtils(ip="1.1.1.1", username="user", password="***")

logger.info(util.return_dirs())
logger.info(util.return_dirs("/dev"))
logger.info(util.is_directory_on_ftp(directory="bin"))
