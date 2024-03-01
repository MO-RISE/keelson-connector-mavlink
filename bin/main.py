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


global vehicle

def query_set_rudder_prc(query):
    '''
    Set rudder angle in percentage with query either for combined, port or starboard rudder

    '''
    key_exp = str(query.selector)
    rudder_id = key_exp.split("/")[5]
    logging.debug(f">> [Queryable Rudder] Received Query '{query.selector}' for rudder {rudder_id}")
        
    values = query.value
    received_at, enclosed_at, content = keelson.uncover(values.payload)
    rudder_input = TimestampedFloat.FromString(content)

    if rudder_id == "*": # Rudder combined 
        logging.debug(f">> [Queryable Rudder] COMBI rudder angle in percentage-100 port 100 starboard '{rudder_input}'")
        # TODO: Implement rudder control forwarding to MAVlink 
        
    elif rudder_id == "0": # Port rudder
        logging.debug(f">> [Queryable Rudder] PORT rudder angle in percentage -100 port 100 starboard  '{rudder_input}'")
        # TODO: Implement rudder control forwarding to MAVlink 

    elif rudder_id == "0": # Starboard rudder
        logging.debug(f">> [Queryable Rudder] STARBOARD rudder angle in percentage -100 port 100 starboard '{rudder_input}'")
        # TODO: Implement rudder control forwarding to MAVlink 
    
    # TODO: Respond with actual set value
    query.respond(zenoh.StatusCode.OK, None)



def query_set_engine_prc(query):
    '''
    Set engine power in percentage with query either for combined, port or starboard engine
    '''
    key_exp = str(query.selector)
    engine_id = key_exp.split("/")[5]
    logging.debug(f">> [Queryable ENGINE] Received Query '{query.selector}' for engine {engine_id}")
        
    values = query.value
    received_at, enclosed_at, content = keelson.uncover(values.payload)
    engine_input = TimestampedFloat.FromString(content)

    if engine_id == "*": # Engine combined 
        logging.debug(f">> [Queryable ENGINE] COMBINED power in percentage -100 astern 100 ahead '{engine_input}'")
        # TODO: Implement control forwarding to MAVlink 
        
    elif engine_id == "0": # Port 
        logging.debug(f">> [Queryable ENGINE] PORT power in percentage -100 astern 100 ahead '{engine_input}'")
        # TODO: Implement control forwarding to MAVlink 

    elif engine_id == "0": # Starboard 
        logging.debug(f">> [Queryable ENGINE] STARBOARD power in percentage -100 astern 100 ahead '{engine_input}'")
        # TODO: Implement control forwarding to MAVlink

    # TODO: Respond with actual set value     
    query.respond(zenoh.StatusCode.OK, None)



def query_set_thruster_prc(query):
    '''
    Set thruster power in percentage with query either for combined, bow or stern 
    '''
    key_exp = str(query.selector)
    thruster_id = key_exp.split("/")[5]
    logging.debug(f">> [Queryable THRUSTER] Received Query '{query.selector}' for thruster {thruster_id}")
        
    values = query.value
    received_at, enclosed_at, content = keelson.uncover(values.payload)
    thruster_input = TimestampedFloat.FromString(content)

    if thruster_id == "*": # Combined 
        logging.debug(f">> [Queryable THRUSTER] COMBINED power in percentage -100 moving vessel to port to 100 moving vessel to starboard '{thruster_input}'")
        # TODO: Implement control forwarding to MAVlink 
        
    elif thruster_id == "0": # Bow 
        logging.debug(f">> [Queryable THRUSTER] BOW power in percentage -100 moving vessel to port to 100 moving vessel to starboard '{thruster_input}'")
        # TODO: Implement control forwarding to MAVlink 

    elif thruster_id == "0": # Stern 
        logging.debug(f">> [Queryable THRUSTER] STERN power in percentage -100 moving vessel to port to 100 moving vessel to starboard '{thruster_input}'")
        # TODO: Implement control forwarding to MAVlink

    # TODO: Respond with actual set value     
    query.respond(zenoh.StatusCode.OK, None)


def query_set_rudder_listener(data: zenoh.Sample):
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


    # CONNECT TO MAVLINK supported FLIGHT CONTROLLER
    try:
        vehicle = boat.Boat(connection_string=args.device_id, baud=57600)
        # vehicle.connect() # no longer needed as the boat connects automatically now
        vehicle.wait_for_heartbeat() # blocking

        if not vehicle.heart_beat_received:
            raise TimeoutError("Timed out waiting for heartbeat from FlightController")


    except Exception as e:
        logging.error("Error connecting to flight controller: %s", e)


    # Keelson setup queryable and subscriber
    try:

        ### RUDDER ###

        # SET  ANGLE QUERYABLE   
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

        # SET RUDDER LISTENER QUERYABLE
        key_exp_lister_rudder =  keelson.construct_req_rep_key(
                realm=args.realm,
                entity_id=args.entity_id,
                responder_id="rudder/*",
                procedure="set_rudder_listener_key",
            )
        
        logging.info(f"Setting up queryable: {key_exp_set_rudder}")
        queryable_set_listener_rudder = session.declare_queryable(
            key_exp_lister_rudder,
            query_set_rudder_listener,
            False,
        )

         ### ENGINE ###


        # Set 
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
            query_set_rudder_listener,
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
