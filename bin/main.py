"""
Utility tool for connecting MAVlink flight controller to Keelson.
"""

import zenoh

import logging
import warnings
import atexit
import json
import time
import keelson
import boat

from utils import map_value
from terminal_inputs import terminal_inputs

from keelson.payloads.TimestampedFloat_pb2 import TimestampedFloat
from keelson.payloads.TimestampedString_pb2 import TimestampedString
from keelson.payloads.FlightControllerTelemetry_pb2 import (
    VFRHUD,
    RawIMU,
    AHRS,
    Vibration,
    BatteryStatus,
)

# from PrioritizedTelemetry_pb2 import TelemetryData
# from Telemetry_pb2 import VFRHUD, RawIMU, AHRS, Vibration, BatteryStatus

from google.protobuf.timestamp_pb2 import Timestamp

vehicle = None
sub_rudder_listener = None
session = None

msg_types = ["VFR_HUD", "RAW_IMU", "AHRS", "VIBRATION", "BATTERY_STATUS"]


def query_set_rudder_prc(query):
    """
    Set rudder angle in percentage with query either for combined, port or starboard rudder

    """
    global vehicle

    key_exp = str(query.selector)
    rudder_id = key_exp.split("/")[5]
    logging.debug(
        f">> [Queryable Rudder] Received Query '{query.selector}' for rudder {rudder_id}"
    )

    values = query.value
    received_at, enclosed_at, content = keelson.uncover(values.payload)
    rudder_input = TimestampedFloat.FromString(content)

    if rudder_id == "*":  # Rudder combined
        logging.debug(
            f">> [Queryable Rudder] COMBI rudder angle in percentage-100 port 100 starboard '{rudder_input}'"
        )
        vehicle.set_rudder(rudder_input)
        # TODO: Implement rudder control forwarding to MAVlink

    elif rudder_id == "0":  # Port rudder
        logging.debug(
            f">> [Queryable Rudder] PORT rudder angle in percentage -100 port 100 starboard  '{rudder_input}'"
        )
        # TODO: Implement rudder control forwarding to MAVlink

    elif rudder_id == "0":  # Starboard rudder
        logging.debug(
            f">> [Queryable Rudder] STARBOARD rudder angle in percentage -100 port 100 starboard '{rudder_input}'"
        )
        # TODO: Implement rudder control forwarding to MAVlink

    # TODO: Respond with actual set value
    query.respond(zenoh.StatusCode.OK, None)


def query_set_engine_prc(query):
    """
    Set engine power in percentage with query either for combined, port or starboard engine
    """
    key_exp = str(query.selector)
    engine_id = key_exp.split("/")[5]
    logging.debug(
        f">> [Queryable ENGINE] Received Query '{query.selector}' for engine {engine_id}"
    )

    values = query.value
    received_at, enclosed_at, content = keelson.uncover(values.payload)
    engine_input = TimestampedFloat.FromString(content)

    if engine_id == "*":  # Engine combined
        logging.debug(
            f">> [Queryable ENGINE] COMBINED power in percentage -100 astern 100 ahead '{engine_input}'"
        )
        # TODO: Implement control forwarding to MAVlink

    elif engine_id == "0":  # Port
        logging.debug(
            f">> [Queryable ENGINE] PORT power in percentage -100 astern 100 ahead '{engine_input}'"
        )
        # TODO: Implement control forwarding to MAVlink

    elif engine_id == "0":  # Starboard
        logging.debug(
            f">> [Queryable ENGINE] STARBOARD power in percentage -100 astern 100 ahead '{engine_input}'"
        )
        # TODO: Implement control forwarding to MAVlink

    # TODO: Respond with actual set value
    query.respond(zenoh.StatusCode.OK, None)


def query_set_thruster_prc(query):
    """
    Set thruster power in percentage with query either for combined, bow or stern
    """
    key_exp = str(query.selector)
    thruster_id = key_exp.split("/")[5]
    logging.debug(
        f">> [Queryable THRUSTER] Received Query '{query.selector}' for thruster {thruster_id}"
    )

    values = query.value
    received_at, enclosed_at, content = keelson.uncover(values.payload)
    thruster_input = TimestampedFloat.FromString(content)

    if thruster_id == "*":  # Combined
        logging.debug(
            f">> [Queryable THRUSTER] COMBINED power in percentage -100 moving vessel to port to 100 moving vessel to starboard '{thruster_input}'"
        )
        # TODO: Implement control forwarding to MAVlink

    elif thruster_id == "0":  # Bow
        logging.debug(
            f">> [Queryable THRUSTER] BOW power in percentage -100 moving vessel to port to 100 moving vessel to starboard '{thruster_input}'"
        )
        # TODO: Implement control forwarding to MAVlink

    elif thruster_id == "0":  # Stern
        logging.debug(
            f">> [Queryable THRUSTER] STERN power in percentage -100 moving vessel to port to 100 moving vessel to starboard '{thruster_input}'"
        )
        # TODO: Implement control forwarding to MAVlink

    # TODO: Respond with actual set value
    query.respond(zenoh.StatusCode.OK, None)


def query_set_rudder_listener(query):
    global sub_rudder_listener, session
    logging.debug(f">> [Queryable Rudder] Received Query '{query}'")

    key_exp = str(query.selector)

    values = query.value
    received_at, enclosed_at, content = keelson.uncover(values.payload)
    message = TimestampedString.FromString(content)
    new_key = message.value

    logging.debug(f">> [SET Sub Rudder] New key: {new_key}")

    if len(new_key) > 5:
        logging.debug(f"Setting up RUDDER subscriber: {new_key}")

        sub_rudder_listener = session.declare_subscriber(
            new_key,
            subscriber_rudder,
        )
    else:
        logging.debug(f"Undeclaring RUDDER subscriber: {new_key}")
        try:
            sub_rudder_listener.undeclare()
        except Exception as e:
            logging.error(f"Error undeclaring sub_rudder_listner: {e}")

    # query.reply(zenoh.Sample(key_exp, 'OK'))


def subscriber_rudder(data):
    res = keelson.uncover(data.payload)

    # create base payload, so we can add the actual values from the received brefv payload
    payload = TimestampedFloat()
    payload.ParseFromString(res[2])

    logging.debug(f">> [Subscriber Rudder] Received value {payload.value}")
    # map the 0-100 value from keelson steering thing to value that the ardupilot understands when we override
    # the rc channel
    vehicle.set_rudder(map_value(payload.value, -99, 99, 1100, 1900))


def subscriber_engine(data):
    res = keelson.uncover(data.payload)
    # create base payload, so we can add the actual values from the received brefv payload
    payload = TimestampedFloat()
    payload.ParseFromString(res[2])

    logging.debug(f">> [Subscriber Engine] Received value {payload.value}")

    # map the 0-100 value from keelson steering thing to value that the ardupilot understands when we override
    # the rc channel
    vehicle.set_throttle(map_value(payload.value, -99, 99, 1100, 1900))


"""
Arguments / configurations are set in docker-compose.yml
"""
if __name__ == "__main__":
    # Input arguments and configurations

    args = terminal_inputs()

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
        vehicle = boat.Boat(connection_string=args.device_id, baud=115200)
        # vehicle.connect() # no longer needed as the boat connects automatically now
        vehicle.wait_for_heartbeat()  # blocking

        if not vehicle.heart_beat_received:
            raise TimeoutError("Timed out waiting for heartbeat from FlightController")

        if not vehicle.is_armed():
            vehicle.arm_vehicle()

    except Exception as e:
        logging.error("Error connecting to flight controller: %s", e)

    # Keelson setup queryable and subscriber
    try:
        ### RUDDER ###

        # SET ANGLE QUERYABLE
        key_exp_set_rudder = keelson.construct_req_rep_key(
            realm=args.realm,
            entity_id=args.entity_id,
            responder_id="rudder/*",
            procedure="set_rudder_angle_pct",
        )
        logging.info(f"Setting up RUDDER queryable: {key_exp_set_rudder}")
        queryable_set_rudder_angle = session.declare_queryable(
            key_exp_set_rudder, query_set_rudder_prc, False
        )

        # SET RUDDER LISTENER QUERYABLE
        key_exp_lister_rudder = keelson.construct_req_rep_key(
            realm=args.realm,
            entity_id=args.entity_id,
            responder_id="rudder/*",
            procedure="set_rudder_listener",
        )
        logging.info(f"Setting up RUDDER queryable: {key_exp_lister_rudder}")

        queryable_set_listener_rudder = session.declare_queryable(
            key_exp_lister_rudder,
            query_set_rudder_listener,
            False,
        )

        if args.subscribe:
            # # Setting default subscribers
            key_exp_sub_rudder = keelson.construct_pub_sub_key(
                realm=args.realm,
                entity_id=args.entity_id,
                subject="lever_position_pct",
                source_id="arduino/right/azimuth/horizontal/on_change",
            )
            logging.info(f"Setting up RUDDER subscriber: {key_exp_sub_rudder}")
            sub_rudder_listener = session.declare_subscriber(
                key_exp_sub_rudder,
                subscriber_rudder,
            )

            key_exp_sub_engine = keelson.construct_pub_sub_key(
                realm=args.realm,
                entity_id=args.entity_id,
                subject="lever_position_pct",
                source_id="arduino/right/azimuth/vertical/on_change",
            )
            logging.info(f"Setting up ENGIEN subscriber: {key_exp_sub_rudder}")
            sub_engine_listener = session.declare_subscriber(
                key_exp_sub_engine,
                subscriber_engine,
            )

        #  sub_rudder_listner.undeclare()

        ### ENGINE ###

        # # Set
        # queryable_set_engine_0 = session.declare_queryable(
        #     key_req_rep + "/set_engine_power_percentage/engine/0",
        #     query_set_engine_prc,
        #     False,
        # )
        # queryable_set_engine_1 = session.declare_queryable(
        #     key_req_rep + "/set_engine_power_percentage/engine/1",
        #     query_set_engine_prc,
        #     False,
        # )
        # queryable_set_engine_0_and_1 = session.declare_queryable(
        #     key_req_rep + "/set_engine_power_percentage/engine/combined",
        #     query_set_engine_prc,
        #     False,
        # )

        # # Set BOW THRUSTERS
        # queryable_set_engine_0 = session.declare_queryable(
        #     key_req_rep + "/set_thruster_power_percentage/thruster/0",
        #     query_set_rudder_prc,
        #     False,
        # )
        # queryable_set_engine_1 = session.declare_queryable(
        #     key_req_rep + "/set_thruster_power_percentage/thruster/1",
        #     query_set_rudder_prc,
        #     False,
        # )
        # queryable_set_engine_0_and_1 = session.declare_queryable(
        #     key_req_rep + "/set_thruster_power_percentage/thruster/combined",
        #     query_set_rudder_prc,
        #     False,
        # )

        # # Set GENERAL SYSTEMS
        # queryable_set_state_of_propulsion_system = session.declare_queryable(
        #     key_req_rep + "/set_state_of_propulsion_system", query_set_rudder_prc, False
        # )

        pubKeyTelemetry = keelson.construct_pub_sub_key(
            realm=args.realm,
            entity_id=args.entity_id,
            subject="telemetry",
            source_id="VFR_HUD",
        )
        logging.info(f"Setting up TELEMETRY publisher: {pubKeyTelemetry}")
        pub = session.declare_publisher(pubKeyTelemetry)

        while True:
            # vehicle.check_rc_mode()

            #################################################
            # TEST Telemetry
            #################################################

            for msg_type in msg_types:

                msg = vehicle.get_vehicle().recv_match(
                    type=msg_type, blocking=True
                )  # Only selected set of messages

                # ['VFR_HUD', 'RAW_IMU', 'AHRS', 'VIBRATION', 'BATTERY_STATUS']

                if msg:
                    logging.info(f"Telemetry message': {msg}")

                    match msg_type:
                        case "VFR_HUD":
                            logging.info(f"VFR_HUD MANAGED")

                            payload = VFRHUD(
                                airspeed=msg.airspeed,
                                groundspeed=msg.groundspeed,
                                heading=msg.heading,
                                throttle=msg.throttle,
                                alt=msg.alt,
                                climb=msg.climb,
                            )
                            # serialize to bytes
                            data_bytes = payload.SerializeToString()
                            envelope = keelson.Envelope(data_bytes)
                            pub.put(envelope)

                        # case "RAW_IMU":
                        #     logging.info(f"RAW_IMU MANAGED")
                        #     payload = RawIMU()
                        #     RawIMU(
                        #         time_usec=msg.time_usec,
                        #         xacc=msg.xacc,
                        #         yacc=msg.yacc,
                        #         zacc=msg.zacc,
                        #         xgyro=msg.xgyro,
                        #         ygyro=msg.ygyro,
                        #         zgyro=msg.zgyro,
                        #         xmag=msg.xmag,
                        #         ymag=msg.ymag,
                        #         zmag=msg.zmag,
                        #         temperature=msg.temperature,
                        #     )

                        # case "AHRS":
                        #     logging.info(f"AHRS MANAGED")
                        #     AHRS(
                        #         omegaIx=msg.omegaIx,
                        #         omegaIy=msg.omegaIy,
                        #         omegaIz=msg.omegaIz,
                        #         accel_weight=msg.accel_weight,
                        #         renorm_val=msg.renorm_val,
                        #         error_rp=msg.error_rp,
                        #         error_yaw=msg.error_yaw,
                        #     )

                        # case "VIBRATION":
                        #     logging.info(f"VIBRATION MANAGED")
                        #     Vibration(
                        #         vibration_x=msg.vibration_x,
                        #         vibration_y=msg.vibration_y,
                        #         vibration_z=msg.vibration_z,
                        #         clipping_0=msg.clipping_0,
                        #         clipping_1=msg.clipping_1,
                        #         clipping_2=msg.clipping_2,
                        #     )

                        # case "BATTERY_STATUS":
                        #     logging.info(f"BATTERY_STATUS MANAGED")
                        #     BatteryStatus(
                        #         id=msg.id,
                        #         battery_function=msg.battery_function,
                        #         type=msg.type,
                        #         temperature=msg.temperature,
                        #         voltages=msg.voltages,
                        #         current_battery=msg.current_battery,
                        #         current_consumed=msg.current_consumed,
                        #         energy_consumed=msg.energy_consumed,
                        #         battery_remaining=msg.battery_remaining,
                        #         time_remaining=msg.time_remaining,
                        #         charge_state=msg.charge_state,
                        #         voltages_ext=msg.voltages_ext,
                        #         mode=msg.mode,
                        #         fault_bitmask=msg.fault_bitmask,
                        #     )

                    # now = Timestamp()
                    # now.GetCurrentTime()
                    # telemetry_data.timestamp.CopyFrom(now)

            time.sleep(0.1)
            # forever loop

    except KeyboardInterrupt:
        logging.info("Program ended due to user request (Ctrl-C)")
        pass

    finally:
        session.close()
