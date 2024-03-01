import datetime
import time
import attribute
from pymavlink import mavutil
from enum import Enum


class Status(Enum):
    ARMED = 1
    DISARMED = 2
    EMERGENCY = 3


class Boat:
    def __init__(self, connection_string, baud):
        """
        Initialize the boat model with a MAVLink connection.
        :param connection_string: Connection string for MAVLink
        """
        self.__connection_string = connection_string
        self.__baud = baud
        self.__vehicle = None
        self.__connected = False
        self.__heartbeat_received = False
        self.__allow_rc_override = True
        self.connect()
        self.__status: Status = Status.ARMED if self.is_armed() else Status.DISARMED

    def send_mavlink_long_cmd(self, command_type, params: list, confirmation=0):
        # type = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM
        self.__vehicle.mav.command_long_send(
            self.__vehicle.target_system, self.__vehicle.target_component,
            command_type, confirmation,
            params[0], params[1], params[2], params[3], params[4], params[5], params[6]
        )

    @property
    def heart_beat_received(self):
        return self.__heartbeat_received

    @property
    def allow_rc_override(self):
        """
        Get the current state of whether RC override is allowed.
        """
        return self.__allow_rc_override

    @allow_rc_override.setter
    def allow_rc_override(self, should_allow):
        """
        Set whether to allow RC override.
        """
        self.__allow_rc_override = should_allow

    def connect(self):
        """
        Establish a MAVLink connection to the vehicle.
        """
        print("Connecting to vehicle on:", self.__connection_string)
        self.__vehicle = mavutil.mavlink_connection(self.__connection_string)
        self.__connected = True

    def wait_for_heartbeat(self):
        """
        Wait for the first heartbeat from the vehicle to confirm connection.
        """
        print("Waiting for vehicle heartbeat")
        if self.__vehicle.wait_heartbeat():
            self.__heartbeat_received = True
            print("Heartbeat received")

    def arm_vehicle(self):
        """
        Arm the vehicle
        :return: true if action succeeded, false otherwise
        """
        print("Arming vehicle")

        self.__vehicle.mav.command_long_send(
            self.__vehicle.target_system, self.__vehicle.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
            1,
            0, 0, 0, 0, 0, 0
        )

        if self.is_armed():
            self.__status = Status.ARMED
            print("VEHICLE ARMED")

            return True

        return False

    def disarm_vehicle(self):
        """
        Disarm the vehicle
        :return: true if action succeeded, false otherwise
        """
        print("DISARMING VEHICLE")

        self.__vehicle.mav.command_long_send(
            self.__vehicle.target_system, self.__vehicle.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
            0,
            0, 0, 0, 0, 0, 0
        )

        if not self.is_armed():
            self.__status = Status.DISARMED
            print("VEHICLE DISARMED")

            return True

        return False

    def is_armed(self):
        """
        Check if the vehicle is armed.
        :return: True if armed, False otherwise
        """
        heartbeat = self.__vehicle.recv_match(type='HEARTBEAT', blocking=True, timeout=1)

        if heartbeat:
            # Check if the vehicle is armed by examining the base_mode field
            armed = heartbeat.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
            return bool(armed)
        else:
            print("No heartbeat message received.")
            return False

    def set_speed(self, speed):
        """
        Set the target speed of the boat.
        :param speed: Speed in m/s
        """
        pass

    def change_heading(self, heading):
        """
        Change the boat's heading.
        :param heading: Heading in degrees
        """
        pass

    def close_connection(self):
        """
        Close the MAVLink connection.
        """
        if self.__vehicle:
            self.__vehicle.close()
            self.__connected = False
            print("Connection closed")

    def set_relay_on(self, relay_number):
        """
        Turns the specified relay on.
        :param vehicle: The vehicle connection
        :param relay_number: The relay number to turn on (default is 0 for Relay1)
        """
        # Send MAV_CMD_DO_SET_RELAY command to turn relay on
        self.__vehicle.mav.command_long_send(
            self.__vehicle.target_system, self.__vehicle.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_RELAY,
            0,
            relay_number, 1, 0, 0, 0, 0, 0
        )
        print(f"Relay{relay_number + 1} turned on")

    def set_relay_off(self, relay_number):
        """
        Turns the specified relay on.
        :param vehicle: The vehicle connection
        :param relay_number: The relay number to turn on (default is 0 for Relay1)
        """
        # Send MAV_CMD_DO_SET_RELAY command to turn relay on
        self.__vehicle.mav.command_long_send(
            self.__vehicle.target_system, self.__vehicle.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_RELAY,
            0,
            relay_number, 0, 0, 0, 0, 0, 0
        )
        print(f"Relay{relay_number + 1} turned off")

    def emergency_stop(self):
        """Emergency stop, calls the disable propulsion function. Named for clarity and to enable additional actions"""
        print("EMERGENCY STOP, DISABLING PROPULSION")
        self.disable_propulsion()

    def disable_propulsion(self):
        """
        Switches off the power to the motors through the beefy relay
        """
        print("DISABLING PROPULSION")
        self.set_relay_off(1)

    def enable_propulsion(self):
        """
        Switches on the power to the motors through the beefy relay
        """
        print("ENABLING PROPULSION")
        self.set_relay_on(1)

    def set_steering(self, steering_value):
        """
        Set the steering of the boat by overriding the RC channel.
        :param steering_value: The PWM value to set for the steering channel (usually between 1000 and 2000)
        """
        if not self.__connected:
            print("Vehicle not connected")
            return

        if self.__allow_rc_override:
            self.__vehicle.mav.rc_channels_override_send(
                self.__vehicle.target_system,  # target_system
                self.__vehicle.target_component,  # target_component
                steering_value,  # RC channel 1 value - steering
                0,  # RC channel 2 value - throttle in some configurations, not overridden here
                0, 0, 0, 0, 0, 0  # Other RC channels not overridden
            )
            print(f"Steering set to {steering_value}")

        else:
            print("Overriding RC channels currently disabled ")

    def set_throttle(self, throttle_value):
        """
        Set the steering of the boat by overriding the RC channel.
        :param steering_value: The PWM value to set for the steering channel (usually between 1000 and 2000)
        """
        if not self.__connected:
            print("Vehicle not connected")
            return

        if self.__allow_rc_override:
            self.__vehicle.mav.rc_channels_override_send(
                self.__vehicle.target_system,  # target_system
                self.__vehicle.target_component,  # target_component
                throttle_value,
                throttle_value,  # RC channel 2 value - throttle in some configurations, not overridden here
                throttle_value, throttle_value, throttle_value, throttle_value, throttle_value, throttle_value
                # Other RC channels not overridden
            )
            print(f"Throttle set to {throttle_value}")

        else:
            print("Overriding RC channels currently disabled ")

    # def check_rc_channel_for_override(self):
    #     """
    #     Continuously check the state of RC11 to determine if overrides are allowed.
    #     """
    #     while True:
    #         rc_channels_msg = self.__vehicle.recv_match(type='RC_CHANNELS', blocking=False)
    #         if rc_channels_msg:
    #             # Assuming RC11 is at index 10 (channels are 1-indexed in MAVLink, but 0-indexed in pymavlink arrays)
    #             rc11_value = rc_channels_msg.chan11_raw
    #
    #             # Assuming a threshold value to determine if the switch is high (e.g., > 1500)
    #             allow_override = rc11_value > 1500
    #             self.set_allow_override_rc(True)
    #
    #             if self.__allow_rc_override:
    #                 print("Override allowed based on RC11")
    #             else:
    #                 print("Override not allowed based on RC11")
    #
    #         time.sleep(0.1)


# example usage below

if __name__ == "__main__":
    connection_string = '/dev/ttyACM0'
    boat = Boat(connection_string=connection_string, baud=57600)
    # boat.connect()
    boat.wait_for_heartbeat()

    boat.enable_propulsion()
    time.sleep(1)
    boat.arm_vehicle()

    # time.sleep(1)
    boat.set_steering(1600)
    time.sleep(1)
    boat.set_steering(1500)

    time.sleep(1)
    boat.set_throttle(1800)

    time.sleep(2)

    boat.close_connection()

    # while True:

    # attitude_msg = boat.vehicle.recv_match(type='ATTITUDE', blocking=True, timeout=0.1)
    # gps_msg = boat.vehicle.recv_match(type='GPS_RAW_INT', blocking=True, timeout=0.1)
    # battery_msg = boat.vehicle.recv_match(type='BATTERY_STATUS', blocking=True, timeout=0.1)
    # vfr_hud_msg = boat.vehicle.recv_match(type='VFR_HUD', blocking=True, timeout=0.1)
    # radio_status_msg = boat.vehicle.recv_match(type='RADIO_STATUS', blocking=True, timeout=0.1)
    # date = datetime.datetime.now()
    # timestamp = date.strftime('%H:%M:%S')
    # if vfr_hud_msg:
    #     print(f"[{timestamp}] Heading: {vfr_hud_msg.heading} degrees")
    # if attitude_msg:
    #     print(f"[{timestamp}] Pitch: {attitude_msg.pitch}, Roll: {attitude_msg.roll}, Yaw: {attitude_msg.yaw}")
    # if gps_msg:
    #     print(
    #         f"[{timestamp}] GPS Lat: {gps_msg.lat / 1e7}, Lon: {gps_msg.lon / 1e7}, Alt: {gps_msg.alt / 1e3} meters")
    # if battery_msg:
    #     battery_voltage = battery_msg.voltages[0] / 1000.0  # Convert millivolts to volts
    #     print(f"[{timestamp}] Battery Voltage: {battery_voltage}V")
    # if radio_status_msg:
    #     print(
    #         f"[{timestamp}] Radio: RSSI {radio_status_msg.rssi}/255, Remote RSSI {radio_status_msg.remrssi}/255, Noise {radio_status_msg.noise}/255, Remote Noise {radio_status_msg.remnoise}/255, TX Buffer {radio_status_msg.txbuf}%")
    # time.sleep(1)

    # boat.close_connection()
