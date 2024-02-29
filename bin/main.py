"""
Utility tool for connecting MAVlink flight controller to Keelson.
"""

import zenoh
import argparse
import logging
import warnings
import atexit
import json
import time
import keelson
import boat

from utils import translate

from keelson.payloads.TimestampedFloat_pb2 import TimestampedFloat

connection_string = "/dev/ttyACM0"
vehicle = boat.Boat(connection_string=connection_string, baud=57600)
vehicle.connect()
vehicle.wait_for_heartbeat()



def query_set_rudder_prc(query):
    logging.debug(f">> [Queryable ] Received Query '{query.selector}'")
    parameters = query.decode_parameters()
    values = query.value
    logging.debug(f">> [Queryable ] Received values '{values}'")
    logging.debug(f">> [Queryable ] Received Query '{parameters}'")


def query_set_engine_prc(query):
    logging.debug(f">> [Queryable ] Received Query '{query.selector}'")
    parameters = query.decode_parameters()
    values = query.value
    logging.debug(f">> [Queryable ] Received values '{values}'")
    logging.debug(f">> [Queryable ] Received Query '{parameters}'")


def query_set_thruster_prc(query):
    logging.debug(f">> [Queryable ] Received Query '{query.selector}'")
    parameters = query.decode_parameters()
    values = query.value
    logging.debug(f">> [Queryable ] Received values '{values}'")
    logging.debug(f">> [Queryable ] Received Query '{parameters}'")





def query_set_rudder_sub(data: zenoh.Sample):
    # unpack brefv
    res = brefv.uncover(data.payload)

    # create base payload, so we can add the actual values from the received brefv payload
    payload = TimestampedFloat()
    payload.ParseFromString(res[2])
    print(payload.value)

    # map the 0-100 value from keelson steering thing to value that the ardupilot understands when we override
    # the rc channel

    steering_value = int(translate(int(payload.value), 1, 99, 1200, 1800))
    vehicle.set_steering(steering_value)


"""
Arguments: and configurations are set in docker-compose.yml
"""
if __name__ == "__main__":

    # Input arguments and configurations
    parser = argparse.ArgumentParser(
        prog="mavlink",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--log-level",
        type=int,
        default=logging.WARNING,
        help="Log level 10=DEBUG, 20=INFO, 30=WARN, 40=ERROR, 50=CRITICAL 0=NOTSET",
    )
    parser.add_argument(
        "--connect",
        action="append",
        type=str,
        help="Endpoints to connect to, in case multicast is not working.",
    )
    parser.add_argument(
        "-r",
        "--realm",
        type=str,
        required=True,
        help="Unique id for a domain/realm to connect",
    )
    parser.add_argument(
        "-e",
        "--entity-id",
        type=str,
        required=True,
        help="Unique id for a entity to connect",
    )
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


    # Keelson setup queryable and subscriber
    try:
        key_base = args.realm + "/" + args.keelson_version + "/" + args.entity_id
       
        logging.info("Base key: %s", key_base)


        # Set RUDDER
        queryable_set_rudder_0 = session.declare_queryable(
            key_base + "/set_rudder_angle_percentage/rudder/0", query_set_rudder_prc, False
        )        
        queryable_set_rudder_1 = session.declare_queryable(
            key_base + "/set_rudder_angle_percentage/rudder/1", query_set_rudder_prc, False
        )
        queryable_set_rudder_0_and_1 = session.declare_queryable(
            key_base + "/set_rudder_angle_percentage/rudder/combined", query_set_rudder_prc, False
        )
        queryable_set_rudder_sub_0_and_1 = session.declare_queryable(
            key_base + "/set_rudder_listener_key/rudder/combined", query_set_rudder_sub, False
        )

        # Set ENGINE
        queryable_set_engine_0 = session.declare_queryable(
            key_base + "/set_engine_power_percentage/engine/0", query_set_engine_prc, False
        )        
        queryable_set_engine_1 = session.declare_queryable(
            key_base + "/set_engine_power_percentage/engine/1", query_set_engine_prc, False
        )
        queryable_set_engine_0_and_1 = session.declare_queryable(
            key_base + "/set_engine_power_percentage/engine/combined", query_set_engine_prc, False
        )

        # Set BOW THRUSTERS 
        queryable_set_engine_0 = session.declare_queryable(
            key_base + "/set_thruster_power_percentage/thruster/0", query_set_rudder_prc, False
        )        
        queryable_set_engine_1 = session.declare_queryable(
            key_base + "/set_thruster_power_percentage/thruster/1", query_set_rudder_prc, False
        )
        queryable_set_engine_0_and_1 = session.declare_queryable(
            key_base + "/set_thruster_power_percentage/thruster/combined", query_set_rudder_prc, False
        )
        
        # Set GENERAL SYSTEMS
        queryable_set_state_of_propulsion_system = session.declare_queryable(
            key_base + "/set_state_of_propulsion_system", query_set_rudder_prc, False
        )

        query_engine = session.declare_queryable(
            key_base + "/engine/0", query_engine_callback, False
        )

        subable = session.declare_subscriber(
            "rise/masslab/haddock/masslab-5/lever_position_pct/arduino/right/azimuth/vertical",
            sub_callback,
        )

        # puub = session.declare_publisher(key_base+"/pub1")

        while True:
            time.sleep(1)
            # forever loop

    except KeyboardInterrupt:
        logging.info("Program ended due to user request (Ctrl-C)")
        pass

    finally:
        session.close()
