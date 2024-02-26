from pymavlink import mavutil
import time

connection_string = '/dev/ttyUSB0'
baud_rate = 57600

print(f"Connecting to vehicle on: {connection_string}")
vehicle = mavutil.mavlink_connection(connection_string, baud=baud_rate)

print("Waiting for heartbeat")
vehicle.wait_heartbeat()
print("Heartbeat received")

while True:
    msg = vehicle.recv_match(type='VFR_HUD', blocking=True)
    if msg:
        heading = msg.heading  # heading in degrees
        print(f"Heading: {heading} degrees")
    time.sleep(1)