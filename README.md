# Keelson Connector Mavlink

Keelson connector for Mavlink

[MAVLink developer guide](https://mavlink.io/en/)
Primary package [pymavlink](https://pypi.org/project/pymavlink/)

## Get started development

Requires:

- python >= 3.11
- docker and docker-compose

Install the python requirements in a virtual environment:

```cmd
python3 -m venv env
source venv/bin/activate
pip install -r requirements_dev.txt
```

To generate functions from .proto file use [protoc generator](https://pypi.org/project/protoc-wheel-0/)

## Keytopics (Keelson 0.3.1)

Rudde
0 = Port rudder
1 = Starboard rudder

zenoh info

zenoh network

## Start command example  

```bash
python bin/main.py -r rise -e boatswain -di /dev/ttyACM0 --log-level 10 

# Start with active subscription to HW controller 
python bin/main.py -r rise -e boatswain -di /dev/ttyACM0 --log-level 10 -sub start
```

## Truble shooting / Lessons learned  

```bash
# If you do not have access rights to read devise 
sudo chmod a+rw /dev/ttyACM0
```

## Telemetry data example from Speedybee

### POWER_STATUS
| Parameter | Value |
| --------- | ----- |
| Vcc       | 0     |
| Vservo    | 0     |
| flags     | 0     |

### MEMINFO
| Parameter | Value |
| --------- | ----- |
| brkval    | 0     |
| freemem   | 46240 |
| freemem32 | 46240 |

### MISSION_CURRENT
| Parameter     | Value |
| ------------- | ----- |
| seq           | 0     |
| total         | 0     |
| mission_state | 0     |
| mission_mode  | 0     |

### SERVO_OUTPUT_RAW
| Parameter   | Value      |
| ----------- | ---------- |
| time_usec   | 1854881584 |
| port        | 0          |
| servo1_raw  | 1500       |
| servo2_raw  | 1500       |
| servo3_raw  | 0          |
| ...         | ...        |
| servo16_raw | 0          |

### RC_CHANNELS
| Parameter    | Value   |
| ------------ | ------- |
| time_boot_ms | 1854881 |
| chancount    | 16      |
| chan1_raw    | 1500    |
| chan2_raw    | 1500    |
| ...          | ...     |
| chan18_raw   | 0       |
| rssi         | 255     |

### RAW_IMU
| Parameter   | Value      |
| ----------- | ---------- |
| time_usec   | 1854881692 |
| xacc        | -888       |
| yacc        | 17         |
| zacc        | -459       |
| xgyro       | 0          |
| ygyro       | 0          |
| zgyro       | 0          |
| xmag        | 0          |
| ymag        | 0          |
| zmag        | 0          |
| id          | 0          |
| temperature | 3369       |

### SCALED_PRESSURE
| Parameter              | Value           |
| ---------------------- | --------------- |
| time_boot_ms           | 1854881         |
| press_abs              | 1019.5732421875 |
| press_diff             | 0.0             |
| temperature            | 3656            |
| temperature_press_diff | 0               |

### GPS_RAW_INT
| Parameter          | Value |
| ------------------ | ----- |
| time_usec          | 0     |
| fix_type           | 0     |
| lat                | 0     |
| lon                | 0     |
| alt                | 0     |
| eph                | 65535 |
| epv                | 65535 |
| vel                | 0     |
| cog                | 0     |
| satellites_visible | 0     |
| alt_ellipsoid      | 0     |
| h_acc              | 0     |
| v_acc              | 0     |
| vel_acc            | 0     |
| hdg_acc            | 0     |
| yaw                | 0     |

### SYSTEM_TIME
| Parameter      | Value   |
| -------------- | ------- |
| time_unix_usec | 0       |
| time_boot_ms   | 1854881 |

### AHRS
| Parameter    | Value                   |
| ------------ | ----------------------- |
| omegaIx      | -0.00020578244584612548 |
| omegaIy      | 1.7825033864937723e-05  |
| omegaIz      | 0.00021514587569981813  |
| accel_weight | 0.0                     |
| renorm_val   | 0.0                     |
| error_rp     | 0.00012932810932397842  |
| error_yaw    | 1.0                     |

### EKF_STATUS_REPORT
| Parameter            | Value                 |
| -------------------- | --------------------- |
| flags                | 167                   |
| velocity_variance    | 0.0                   |
| pos_horiz_variance   | 0.0003704401315189898 |
| pos_vert_variance    | 0.0030375404749065638 |
| compass_variance     | 0.0                   |
| terrain_alt_variance | 0.0                   |
| airspeed_variance    | 0.0                   |

### VIBRATION
| Parameter   | Value                |
| ----------- | -------------------- |
| time_usec   | 1854900660           |
| vibration_x | 0.009094780310988426 |
| vibration_y | 0.006576085463166237 |
| vibration_z | 0.00686581851914525  |
| clipping_0  | 0                    |
| clipping_1  | 0                    |
| clipping_2  | 0                    |

### BATTERY_STATUS
| Parameter         | Value              |
| ----------------- | ------------------ |
| id                | 0                  |
| battery_function  | 0                  |
| type              | 0                  |
| temperature       | 32767              |
| voltages          | [4966, 65535, ...] |
| current_battery   | 44                 |
| current_consumed  | 229                |
| energy_consumed   | 41                 |
| battery_remaining | 93                 |
| time_remaining    | 0                  |
| charge_state      | 1                  |
| voltages_ext      | [0, 0, 0, 0]       |
| mode              | 0                  |
| fault_bitmask     | 0                  |
