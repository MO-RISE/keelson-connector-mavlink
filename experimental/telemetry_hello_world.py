import time
from bin.boat import Boat
from proto.PrioritizedTelemetry_pb2 import TelemetryData
from proto.Telemetry_pb2 import VFRHUD, RawIMU
from google.protobuf.timestamp_pb2 import Timestamp
import zenoh

session = zenoh.open()

vehicle = Boat(connection_string='/dev/ttyACM0', baud=115200)

msg_types = ['VFR_HUD', 'RAW_IMU', 'AHRS', 'VIBRATION', 'BATTERY_STATUS']

key = 'myhome/kitchen/temp'
pub = session.declare_publisher(key)

while True:
    telemetry_data = TelemetryData()
    for msg_type in msg_types:
        msg = vehicle.get_vehicle().recv_match(type=msg_type, blocking=True)

        if msg:
            print(msg)
            if msg_type == 'VFR_HUD':
                telemetry_data.vfr_hud.CopyFrom(VFRHUD(airspeed=msg.airspeed, groundspeed=msg.groundspeed,
                                                       heading=msg.heading, throttle=msg.throttle,
                                                       alt=msg.alt, climb=msg.climb))

                print('GOT VFR')
            elif msg_type == 'RAW_IMU':
                telemetry_data.raw_imu.CopyFrom(RawIMU(time_usec=msg.time_usec, xacc=msg.xacc,
                                                       yacc=msg.yacc, zacc=msg.zacc, xgyro=msg.xgyro,
                                                       ygyro=msg.ygyro, zgyro=msg.zgyro, xmag=msg.xmag,
                                                       ymag=msg.ymag, zmag=msg.zmag, temperature=msg.temperature))
                print('GOT IMU')

            now = Timestamp()
            now.GetCurrentTime()
            telemetry_data.timestamp.CopyFrom(now)

            # serialize to bytes
            data_bytes = telemetry_data.SerializeToString()

            pub.put(data_bytes)

        #time.sleep(1)



session.close()
