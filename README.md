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