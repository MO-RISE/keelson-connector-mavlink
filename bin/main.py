"""
Command line utility tool for linking mavlink controller to keelson.
"""

import zenoh
import argparse
import logging
import warnings
import atexit
import json
import time
import brefv
import boat

connection_string = '/dev/ttyACM0'
vehicle = boat.Boat(connection_string=connection_string, baud=57600)
vehicle.connect()
vehicle.wait_for_heartbeat()

from TimestampedFloat_pb2 import TimestampedFloat


def queryable_callback(query):
    logging.debug(f">> [Queryable ] Received Query '{query.selector}'")
    parameters = query.decode_parameters()
    values = query.value
    logging.debug(f">> [Queryable ] Received values '{values}'")
    logging.debug(f">> [Queryable ] Received Query '{parameters}'")


def query_engine_callback(query):
    logging.debug(f">> [Queryable ] Received Query '{query.selector}'")
    parameters = query.decode_parameters()
    values = query.value
    logging.debug(f">> [Queryable ] Received values '{values}'")
    logging.debug(f">> [Queryable ] Received Query '{parameters}'")


def translate(value, leftMin, leftMax, rightMin, rightMax):  # from stackoverflow
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def sub_callback(data: zenoh.Sample):
    # unpack brefv
    res = brefv.uncover(data.payload)

    # create base payload, so we can add the actual values from the received brefv payload
    payload = TimestampedFloat()
    payload.ParseFromString(res[2])
    print(payload.value)

    # map the 0-100 value from keelson steering thing to value that the ardupilot understands when we override
    #the rc channel

    steering_value = int(translate(int(payload.value), 1, 99, 1200, 1800))
    vehicle.set_steering(steering_value)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="mavlink",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--log-level", type=int, default=logging.WARNING,
                        help="Log level 10=DEBUG, 20=INFO, 30=WARN, 40=ERROR, 50=CRITICAL 0=NOTSET")
    parser.add_argument(
        "--connect",
        action="append",
        type=str,
        help="Endpoints to connect to, kind a if multicast is not working.",
    )
    parser.add_argument("-r", "--realm", type=str, required=True, help="Unique id for a domain/realm to connect")
    parser.add_argument("-kv", "--keelson-verison", type=str, required=True, help="Major version of keelson protocol")
    parser.add_argument("-e", "--entity-id", type=str, required=True, help="Unique id for a entity to connect")

    ## Parse arguments and start doing our thing
    args = parser.parse_args()

    # Setup logger
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s", level=args.log_level
    )
    logging.captureWarnings(True)
    warnings.filterwarnings("once")

    ## Construct session
    logging.info("Opening Zenoh session...")
    conf = zenoh.Config()

    if args.connect is not None:
        conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
    session = zenoh.open(conf)


    def _on_exit():
        session.close()


    atexit.register(_on_exit)

    logging.info(f"Zenoh session: {session.info()}")

    try:

        key_base = args.realm + "/" + args.keelson_verison + "/" + args.entity_id
        logging.info("Base key: %s", key_base)

        queryable = session.declare_queryable(key_base + "/query1", queryable_callback, False)

        query_engine = session.declare_queryable(key_base + "/engine/0", query_engine_callback, False)

        subable = session.declare_subscriber(
            "rise/masslab/haddock/masslab-5/lever_position_pct/arduino/right/azimuth/vertical", sub_callback)

        # puub = session.declare_publisher(key_base+"/pub1")

        while True:
            time.sleep(1)
            # forever loop

    except KeyboardInterrupt:
        logging.info("Program ended due to user request (Ctrl-C)")
        pass

    finally:
        session.close()