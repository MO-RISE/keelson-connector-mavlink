# Keelson Connector Mavlink

Keelson connector for Mavlink, mostly used to connect towards flightcontrollers. 

[MAVLink developer guide](https://mavlink.io/en/)

Primary package [pymavlink](https://pypi.org/project/pymavlink/) 


# Get started development 

Requires:
- python >= 3.11
- docker and docker-compose

Install the python requirements in a virtual environment:

```cmd
python3 -m venv env
source venv/bin/activate
pip install -r requirements_dev.txt
```

To generate from proto use [protoc generator](https://pypi.org/project/protoc-wheel-0/)



RC model config 

Rudder 
0 = Port rudder
1 = Starboard rudder




zenoh info

zenoh network


## Start command example  

```
python bin/main.py -r rise -e masslab -di dev --log-level 10 

python bin/main.py -r rise -e masslab -di dev --log-level 10 -sub start
```

sudo chmod a+rw /dev/ttyACM0


data example 

POWER_STATUS {Vcc : 0, Vservo : 0, flags : 0}
MEMINFO {brkval : 0, freemem : 46240, freemem32 : 46240}
MISSION_CURRENT {seq : 0, total : 0, mission_state : 0, mission_mode : 0}
SERVO_OUTPUT_RAW {time_usec : 1854881584, port : 0, servo1_raw : 1500, servo2_raw : 1500, servo3_raw : 0, servo4_raw : 0, servo5_raw : 1500, servo6_raw : 1500, servo7_raw : 0, servo8_raw : 0, servo9_raw : 0, servo10_raw : 0, servo11_raw : 0, servo12_raw : 0, servo13_raw : 0, servo14_raw : 0, servo15_raw : 0, servo16_raw : 0}
RC_CHANNELS {time_boot_ms : 1854881, chancount : 16, chan1_raw : 1500, chan2_raw : 1500, chan3_raw : 1530, chan4_raw : 1500, chan5_raw : 999, chan6_raw : 999, chan7_raw : 999, chan8_raw : 999, chan9_raw : 999, chan10_raw : 2000, chan11_raw : 999, chan12_raw : 999, chan13_raw : 880, chan14_raw : 880, chan15_raw : 1980, chan16_raw : 2011, chan17_raw : 0, chan18_raw : 0, rssi : 255}
RAW_IMU {time_usec : 1854881692, xacc : -888, yacc : 17, zacc : -459, xgyro : 0, ygyro : 0, zgyro : 0, xmag : 0, ymag : 0, zmag : 0, id : 0, temperature : 3369}
SCALED_PRESSURE {time_boot_ms : 1854881, press_abs : 1019.5732421875, press_diff : 0.0, temperature : 3656, temperature_press_diff : 0}
GPS_RAW_INT {time_usec : 0, fix_type : 0, lat : 0, lon : 0, alt : 0, eph : 65535, epv : 65535, vel : 0, cog : 0, satellites_visible : 0, alt_ellipsoid : 0, h_acc : 0, v_acc : 0, vel_acc : 0, hdg_acc : 0, yaw : 0}
SYSTEM_TIME {time_unix_usec : 0, time_boot_ms : 1854881}
AHRS {omegaIx : -0.00020578244584612548, omegaIy : 1.7825033864937723e-05, omegaIz : 0.00021514587569981813, accel_weight : 0.0, renorm_val : 0.0, error_rp : 0.00012932810932397842, error_yaw : 1.0}
EKF_STATUS_REPORT {flags : 167, velocity_variance : 0.0, pos_horiz_variance : 0.0003704401315189898, pos_vert_variance : 0.0030375404749065638, compass_variance : 0.0, terrain_alt_variance : 0.0, airspeed_variance : 0.0}
VIBRATION {time_usec : 1854900660, vibration_x : 0.009094780310988426, vibration_y : 0.006576085463166237, vibration_z : 0.00686581851914525, clipping_0 : 0, clipping_1 : 0, clipping_2 : 0}
BATTERY_STATUS {id : 0, battery_function : 0, type : 0, temperature : 32767, voltages : [4966, 65535, 65535, 65535, 65535, 65535, 65535, 65535, 65535, 65535], current_battery : 44, current_consumed : 229, energy_consumed : 41, battery_remaining : 93, time_remaining : 0, charge_state : 1, voltages_ext : [0, 0, 0, 0], mode : 0, fault_bitmask : 0}
RC_CHANNELS_SCALED {time_boot_ms : 1854900, port : 0, chan1_scaled : 0, chan2_scaled : 0, chan3_scaled : 0, chan4_scaled : 0, chan5_scaled : 0, chan6_scaled : 0, chan7_scaled : 0, chan8_scaled : 0, rssi : 255}
ATTITUDE {time_boot_ms : 1854901, roll : -0.06466211378574371, pitch : -1.1010041236877441, yaw : 0.16111764311790466, rollspeed : 0.00012597451859619468, pitchspeed : -0.00015750486636534333, yawspeed : -6.186332029756159e-05}
VFR_HUD {airspeed : 0.0, groundspeed : 0.0009112635161727667, heading : 9, throttle : 0, alt : 0.6699999570846558, climb : -0.008379140868782997}
AHRS2 {roll : -0.06874044984579086, pitch : -1.1033830642700195, yaw : 0.3230848014354706, altitude : 0.6699999570846558, lat : 0, lng : 0}
ATTITUDE {time_boot_ms : 1855160, roll : -0.06460968405008316, pitch : -1.1010148525238037, yaw : 0.16108573973178864, rollspeed : 0.00017336032760795206, pitchspeed : 6.511509127449244e-05, yawspeed : -0.00015719463408458978}
VFR_HUD {airspeed : 0.0, groundspeed : 0.0010552617022767663, heading : 9, throttle : 0, alt : 0.6699999570846558, climb : -0.007802832871675491}
AHRS2 {roll : -0.06869062036275864, pitch : -1.103387713432312, yaw : 0.32308223843574524, altitude : 0.6699999570846558, lat : 0, lng : 0}
GLOBAL_POSITION_INT {time_boot_ms : 1855381, lat : 0, lon : 0, alt : 660, relative_alt : 661, vx : 0, vy : 0, vz : 0, hdg : 922}
SYS_STATUS {onboard_control_sensors_present : 321969167, onboard_control_sensors_enabled : 35684367, onboard_control_sensors_health : 53510155, load : 56, voltage_battery : 4966, current_battery : 44, battery_remaining : 93, drop_rate_comm : 0, errors_comm : 0, errors_count1 : 0, errors_count2 : 0, errors_count3 : 0, errors_count4 : 0}
POWER_STATUS {Vcc : 0, Vservo : 0, flags : 0}