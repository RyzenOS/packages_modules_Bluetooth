#!/usr/bin/env python3
#
#   Copyright 2019 - The Android Open Source Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from gd_device_base import GdDeviceBase
from gd_device_base import replace_vars

from cert.event_stream import EventStream
from hal import facade_pb2_grpc as hal_facade_pb2_grpc

ACTS_CONTROLLER_CONFIG_NAME = "GdDevice"
ACTS_CONTROLLER_REFERENCE_NAME = "gd_devices"

def create(configs):
    if not configs:
        raise GdDeviceConfigError("Configuration is empty")
    elif not isinstance(configs, list):
        raise GdDeviceConfigError("Configuration should be a list")
    return get_instances_with_configs(configs)


def destroy(devices):
    for device in devices:
        try:
            device.clean_up()
        except:
            device.log.exception("Failed to clean up properly.")


def get_info(devices):
    return []


def get_instances_with_configs(configs):
    print(configs)
    devices = []
    for config in configs:
        resolved_cmd = []
        for entry in config["cmd"]:
            resolved_cmd.append(replace_vars(entry, config))
        devices.append(GdDevice(config["grpc_port"], resolved_cmd, config["label"]))
    return devices

class GdDevice(GdDeviceBase):
    def __init__(self, grpc_port, cmd, label):
        super().__init__(grpc_port, cmd, label, ACTS_CONTROLLER_CONFIG_NAME)
        self.hal = hal_facade_pb2_grpc.HciHalFacadeStub(self.grpc_channel)
        self.hal.hci_event_stream = EventStream(self.hal.FetchHciEvent)
        self.hal.hci_acl_stream = EventStream(self.hal.FetchHciAcl)
        self.hal.hci_sco_stream = EventStream(self.hal.FetchHciSco)
