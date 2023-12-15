import requests
import logging
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from epconf import get_device_auth

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def get_devices_from_fa():
    url = f"http://facilityadmin/api/internal/generic-devices/v2/devices/?page=1"

    headers = {
        'Authorization': 'Token <FA_TOKEN_HERE>'
    }
    data = []
    response = requests.get(url, headers).json()
    data.append(response['results'])
    if response['next']:
        for i in response['next']:
            data.append('i')
    print(data)

def get_teltonika_ubus_session(device:dict):
    identifier = device['identifier']
    if not device['deviceauth']:
        print(f'Teltonika with identifier {identifier} is lacking authentication data.')
        return
    username = device['deviceauth']['username']
    password = device['deviceauth']['password']
    deviceIP = device['networkdevice']['ip_address']
    deviceIPPort = device['networkdevice']['ip_port']
    if not username or not password or not deviceIP or not deviceIPPort:
        print(f'Teltonika with identifier {identifier} is missing some data.')
        return

    url = f"http://{deviceIP}:{deviceIPPort}/"
    auth = device['type']['communication_type']

    if auth == 'http_basic':
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
    elif auth == 'http_digest':
        response = requests.get(url, auth=HTTPDigestAuth(username, password))
    # only this bit will be run on teltonikas, above is for other http devices
    # teltonika will need its own comunication_type, perhaps "ubus"
    elif auth is None:
        data = '{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": [ "00000000000000000000000000000000", "session", "login", { "username": "admin", "password": "PASSWORD_HERE"  } ] }'

        sessionUrl = url + 'ubus'
        try:
            response = requests.post(sessionUrl, data=data)
            response.raise_for_status()
            response = response.json()
        except Exception as e:
            print(f'could not reach {identifier} exception was {e}')
            return

        # print(response)
        # print(response['result'][1]['ubus_rpc_session'])
        ubus_rpc_session = response['result'][1]['ubus_rpc_session']
        return ubus_rpc_session

def get_teltonika_signal(device:dict, url: str):
    sessionUrl = url + 'ubus'
    ubus_rpc_session = get_teltonika_ubus_session(device)
    data= ('{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": ['
           f'"{ubus_rpc_session}"'
           ', "file", "exec", { "command":"gsmctl", "params": ["-q"] } ] }')

    response = requests.post(sessionUrl, data=data).json()

    #print(response)



    stdout = response['result'][1]['stdout']

    #print(stdout)


    stdout_list = response['result'][1]['stdout'].split('\n')
    #print(stdout_list)
    rssi = int(stdout_list[0].split(' ')[1])
    rsrp = int(stdout_list[1].split(' ')[1])
    sinr = int(stdout_list[2].split(' ')[1])
    rsrq = int(stdout_list[3].split(' ')[1])
    #print(rssi, rsrp,sinr, rsrq)


    if rssi < -90:
        #print("Du har dårlig signal - Rød Farge")
        return  f'Red with signal strength {rssi}'
    elif -89 < rssi < -44:
        #print("Du har greit signal - Gul Farge")
        return f'Yellow with signal strength {rssi}'
    elif -44 < rssi:
        #print("Du har bra signal - Grønn Farge")
        return f'Green with signal strength {rssi}'
    else:
        return  f'Uknown with signal strength {rssi}'

def main(identifier = "4505000"):

    url = f"http://facilityadmin/api/internal/generic-devices/v2/devices/?search={identifier}"

    headers = {
        'Authorization': 'Token e65052dd34859b630b8e56fef2a9ac9163f08a70'
    }

    response = requests.get(url=url, headers=headers).json()
    for device in response:

     if 'result' in response and isinstance(response['result'], list) and response['result']:

          logging.error("Teltonikaen har ikke result i sin Ubus: JSON")
          continue
     else:
        get_teltonika_signal(device, url)


    """    loginRes = requests.post(loginUrl, headers= headers, cookies=cookies, data= '{"username": "admin","password": "PASSWORD_HERE"}')
        print(loginRes.status_code)
        print(loginRes.text)
        try:
            print(loginRes.json())
        except:
            print('could not print json responce')
    else:
        response = requests.get(url)
        print(f'Reached unimplemented authentication method, Auth method was {auth}')"""




if __name__ == '__main__':
 main()