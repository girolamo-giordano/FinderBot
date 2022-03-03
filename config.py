#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "6c26d8ff-2f35-4a3c-83a7-f5a0ced62ae6")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "~TMht.SFhT_v.2GY2YD2.U6IYGURB9Cfhc")
