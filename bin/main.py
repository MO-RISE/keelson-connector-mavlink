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


def query_set_rudder_prc(query):
    key_exp = str(query.selector)
    rudder_id = key_exp.split("/")[5]
    logging.debug(f">> [Queryable Rudder] Received Query '{query.selector}' for rudder {rudder_id}")
        
    values = query.value
    received_at, enclosed_at, content = keelson.uncover(values.payload)

    if rudder_id == "*": # Rudder combined 
        rudder_input = TimestampedFloat.FromString(content)
        logging.debug(f">> [Queryable Rudder] COMBI rudder angle in degrees '{rudder_input}'")
        # TODO: Chane to procentage in fronted (current degrees)
        
    elif rudder_id == "0": # Port rudder
        rudder_input = TimestampedFloat.FromString(content)
        logging.debug(f">> [Queryable Rudder] PORT rudder angle in degrees '{rudder_input}'")

    elif rudder_id == "0": # Starboard rudder
        rudder_input = TimestampedFloat.FromString(content)
        logging.debug(f">> [Queryable Rudder] STARBOARD rudder angle in degrees '{rudder_input}'")




def query_set_engine_prc(query):
    logging.debug(f">> [Queryable Engine] Received Query '{query.selector}'")
    parameters = query.decode_parameters()
    values = query.value
    logging.debug(f">> [Queryable Engine] Received values '{values}'")
    logging.debug(f">> [Queryable Engine] Received Query '{parameters}'")


def query_set_thruster_prc(query):
    logging.debug(f">> [Queryable Thruster] Received Query '{query.selector}'")
    parameters = query.decode_parameters()
    values = query.value
    logging.debug(f">> [Queryable Thruster] Received values '{values}'")
    logging.debug(f">> [Queryable Thruster] Received Query '{parameters}'")


def query_set_rudder_sub(data: zenoh.Sample):
    logging.debug(f">> [Queryable ] Received Query '{data}'")

    # unpack brefv
    res = keelson.uncover(data.payload)

    # create base payload, so we can add the actual values from the received brefv payload
    payload = TimestampedFloat()
    payload.ParseFromString(res[2])
    print(payload.value)

    # map the 0-100 value from keelson steering thing to value that the ardupilot understands when we override
    # the rc channel

    steering_value = int(translate(int(payload.value), 1, 99, 1200, 1800))
    # vehicle.set_steering(steering_value)


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
    parser.add_argument(
        "-di",
        "--device-id",
        type=str,
        required=True,
        help="Connection device string for MAVLink Ex. /dev/ttyACM0",
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

    # try:
    #     # Connect to flight controller
    #     # connection_string = "/dev/ttyACM0"
    #     vehicle = boat.Boat(connection_string=args.device_id, baud=57600)
    #     vehicle.connect()
    #     vehicle.wait_for_heartbeat()
    # except Exception as e:
    #     logging.error("Error connecting to flight controller: %s", e)

    # Keelson setup queryable and subscriber
    try:
        key_pub_sub = keelson.construct_pub_sub_key(
            realm=args.realm,
            entity_id=args.entity_id,
            subject="subject",
            source_id="rc_boat",
        )

        key_req_rep = keelson.construct_req_rep_key(
            realm=args.realm,
            entity_id=args.entity_id,
            responder_id="rc_boat",
            procedure="mavlink",
        )

        logging.info("Base key_pub_sub: %s", key_pub_sub)
        logging.info("Base key_req_rep: %s", key_req_rep)

        # Set RUDDER
        key_exp_set_rudder = keelson.construct_req_rep_key(
            realm=args.realm,
            entity_id=args.entity_id,
            responder_id="rudder/*",
            procedure="set_rudder_angle_pct",
        )
        logging.info(f"Setting up queryable: {key_exp_set_rudder}")

        queryable_set_rudder_angle = session.declare_queryable(
            key_exp_set_rudder, query_set_rudder_prc, False
        )

        queryable_set_listener_rudder = session.declare_queryable(
            keelson.construct_req_rep_key(
                realm=args.realm,
                entity_id=args.entity_id,
                responder_id="rudder/*",
                procedure="set_rudder_listener_key",
            ),
            query_set_rudder_sub,
            False,
        )

        # Set ENGINE
        queryable_set_engine_0 = session.declare_queryable(
            key_req_rep + "/set_engine_power_percentage/engine/0",
            query_set_engine_prc,
            False,
        )
        queryable_set_engine_1 = session.declare_queryable(
            key_req_rep + "/set_engine_power_percentage/engine/1",
            query_set_engine_prc,
            False,
        )
        queryable_set_engine_0_and_1 = session.declare_queryable(
            key_req_rep + "/set_engine_power_percentage/engine/combined",
            query_set_engine_prc,
            False,
        )

        # Set BOW THRUSTERS
        queryable_set_engine_0 = session.declare_queryable(
            key_req_rep + "/set_thruster_power_percentage/thruster/0",
            query_set_rudder_prc,
            False,
        )
        queryable_set_engine_1 = session.declare_queryable(
            key_req_rep + "/set_thruster_power_percentage/thruster/1",
            query_set_rudder_prc,
            False,
        )
        queryable_set_engine_0_and_1 = session.declare_queryable(
            key_req_rep + "/set_thruster_power_percentage/thruster/combined",
            query_set_rudder_prc,
            False,
        )

        # Set GENERAL SYSTEMS
        queryable_set_state_of_propulsion_system = session.declare_queryable(
            key_req_rep + "/set_state_of_propulsion_system", query_set_rudder_prc, False
        )

        # Setting default subscribers
        # logging.info(f"Sub to:{ key_base + "/lever_position_pct/arduino/right/azimuth/vertical"}")
        sub_rudder = session.declare_subscriber(
            key_pub_sub + "/lever_position_pct/arduino/right/azimuth/vertical",
            query_set_rudder_sub,
        )

        # pub = session.declare_publisher(key_base+"/pub1")

        while True:
            time.sleep(1)
            # forever loop

    except KeyboardInterrupt:
        logging.info("Program ended due to user request (Ctrl-C)")
        pass

    finally:
        session.close()
