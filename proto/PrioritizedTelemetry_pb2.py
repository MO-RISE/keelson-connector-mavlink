# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: PrioritizedTelemetry.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import Telemetry_pb2 as Telemetry__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1aPrioritizedTelemetry.proto\x12\ttelemetry\x1a\x0fTelemetry.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"\x80\x02\n\rTelemetryData\x12-\n\ttimestamp\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\"\n\x07vfr_hud\x18\x02 \x01(\x0b\x32\x11.telemetry.VFRHUD\x12\"\n\x07raw_imu\x18\x03 \x01(\x0b\x32\x11.telemetry.RawIMU\x12\x1d\n\x04\x61hrs\x18\x04 \x01(\x0b\x32\x0f.telemetry.AHRS\x12\'\n\tvibration\x18\x05 \x01(\x0b\x32\x14.telemetry.Vibration\x12\x30\n\x0e\x62\x61ttery_status\x18\x06 \x01(\x0b\x32\x18.telemetry.BatteryStatusb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'PrioritizedTelemetry_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_TELEMETRYDATA']._serialized_start=92
  _globals['_TELEMETRYDATA']._serialized_end=348
# @@protoc_insertion_point(module_scope)
