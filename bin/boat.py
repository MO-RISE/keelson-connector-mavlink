import datetime
import time
from pymavlink import mavutil

class Boat:
    def __init__(self, connection_string, baud):
        """
        Initialize the boat model with a MAVLink connection.
        :param connection_string: Connection string for MAVLink
        """
        self.connection_string = connection_string
        self.baud = baud
        self.vehicle = None
        self.connected = False
        self.heartbeat_received = False

    def connect(self):
        """
        Establish a MAVLink connection to the vehicle.
        """
        print("Connecting to vehicle on:", self.connection_string)
        self.vehicle = mavutil.mavlink_connection(self.connection_string)
        self.connected = True

    def wait_for_heartbeat(self):
        """
        Wait for the first heartbeat from the vehicle to confirm connection.
        """
        print("Waiting for vehicle heartbeat")
        if self.vehicle.wait_heartbeat():
            self.heartbeat_received = True
            print("Heartbeat received")

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
        if self.vehicle:
            self.vehicle.close()
            self.connected = False
            print("Connection closed")

    def set_relay_on(self, relay_number=1):
        """
        Turns the specified relay on.
        :param vehicle: The vehicle connection
        :param relay_number: The relay number to turn on (default is 0 for Relay1)
        """
        # Send MAV_CMD_DO_SET_RELAY command to turn relay on
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system, self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_RELAY,
            0,
            relay_number, 1, 0, 0, 0, 0, 0
        )
        print(f"Relay{relay_number + 1} turned on")

    def set_relay_off(self, relay_number=1):
        """
        Turns the specified relay on.
        :param vehicle: The vehicle connection
        :param relay_number: The relay number to turn on (default is 0 for Relay1)
        """
        # Send MAV_CMD_DO_SET_RELAY command to turn relay on
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system, self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_RELAY,
            0,
            relay_number, 0, 0, 0, 0, 0, 0
        )
        print(f"Relay{relay_number + 1} turned off")

    def set_steering(self, steering_value):
        """
        Set the steering of the boat by overriding the RC channel.
        :param steering_value: The PWM value to set for the steering channel (usually between 1000 and 2000)
        """
        if not self.connected:
            print("Vehicle not connected")
            return

        self.vehicle.mav.rc_channels_override_send(
            self.vehicle.target_system,  # target_system
            self.vehicle.target_component,  # target_component
            steering_value,  # RC channel 1 value - steering
            0,  # RC channel 2 value - throttle in some configurations, not overridden here
            0, 0, 0, 0, 0, 0  # Other RC channels not overridden
        )
        print(f"Steering set to {steering_value}")


# if __name__ == "__main__":
#     connection_string = '/dev/ttyACM0'
#     boat = Boat(connection_string=connection_string, baud=57600)
#     boat.connect()
#     boat.wait_for_heartbeat()
#
#     boat.set_relay_on()
#     time.sleep(1)
#     boat.set_relay_off()
#     boat.set_steering(1600)
#     time.sleep(1)
#
#     while True:
#         attitude_msg = boat.vehicle.recv_match(type='ATTITUDE', blocking=True, timeout=0.1)
#         gps_msg = boat.vehicle.recv_match(type='GPS_RAW_INT', blocking=True, timeout=0.1)
#         battery_msg = boat.vehicle.recv_match(type='BATTERY_STATUS', blocking=True, timeout=0.1)
#         vfr_hud_msg = boat.vehicle.recv_match(type='VFR_HUD', blocking=True, timeout=0.1)
#         radio_status_msg = boat.vehicle.recv_match(type='RADIO_STATUS', blocking=True, timeout=0.1)
#         date = datetime.datetime.now()
#         timestamp = date.strftime('%H:%M:%S')
#         if vfr_hud_msg:
#             print(f"[{timestamp}] Heading: {vfr_hud_msg.heading} degrees")
#         if attitude_msg:
#             print(f"[{timestamp}] Pitch: {attitude_msg.pitch}, Roll: {attitude_msg.roll}, Yaw: {attitude_msg.yaw}")
#         if gps_msg:
#             print(
#                 f"[{timestamp}] GPS Lat: {gps_msg.lat / 1e7}, Lon: {gps_msg.lon / 1e7}, Alt: {gps_msg.alt / 1e3} meters")
#         if battery_msg:
#             battery_voltage = battery_msg.voltages[0] / 1000.0  # Convert millivolts to volts
#             print(f"[{timestamp}] Battery Voltage: {battery_voltage}V")
#         if radio_status_msg:
#             print(
#                 f"[{timestamp}] Radio: RSSI {radio_status_msg.rssi}/255, Remote RSSI {radio_status_msg.remrssi}/255, Noise {radio_status_msg.noise}/255, Remote Noise {radio_status_msg.remnoise}/255, TX Buffer {radio_status_msg.txbuf}%")
#         time.sleep(1)
#
#
#
#     boat.close_connection()


