from requests.auth import HTTPDigestAuth, HTTPBasicAuth
import requests
import os
from epcommon.conf.conf import Conf

os.environ['EP_FA_URL'] = 'http://facilityadmin/api'
os.environ['EP_FA_TOKEN'] = '<TOKEN_HERE>'
conf = Conf()

if __name__ != '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
else:
    try:
        from __main__ import logging
    except Exception as e:
        print(e)
        import logging
        logging.basicConfig(level=logging.INFO)

def get_conf():
    return conf

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

def get_device_auth(device):
    auth_type = device['type']['communication_type']
    auth = None
    if not device['deviceauth']:
        logging.warning(f'Device with identifier {device["identifier"]} did not have auth, using default')
        #Check if Tattile
        if device['type']['id'] in (2, 13, 16):
            username = 'superuser'
            password = 'PASSWORD_HERE'
        #Check if Axis
        elif device['type']['id'] in (12, 30, 29, 28, 17):
            username = 'root'
            password = 'PASSWORD_HERE'
        #Check if Teltonika
        elif device['type']['id'] in (21, 27):
            username = 'admin'
            password = 'PASSWORD_HERE'
    else:
        username = device['deviceauth']['username']
        password = device['deviceauth']['password']
    if auth_type == 'http_basic':
        auth = HTTPBasicAuth(username, password)
    elif auth_type == 'http_digest':
        auth = HTTPDigestAuth(username, password)
    elif auth is None:
        #TODO! teltonika needs its own communication type thats called 'ubus'
        auth = ('{ "jsonrpc": "2.0", "id": 1, "method": "call", '
                '"params": [ "00000000000000000000000000000000", "session", '
                '"login", { "username": "{}", "password": "{}"  } ] }'.format(username, password))
    return auth

def get_device_url(device):
    deviceIP = device['networkdevice']['ip_address']
    url = f'http://{deviceIP}'
    deviceIPPort = device['networkdevice']['ip_port']
    if deviceIP.startswith('10.80'):
        url = url + f':{str(deviceIPPort)}'
    return url

def update_fa_device(device:dict, body:dict):
    url = f"http://facilityadmin/api/internal/generic-devices/v3/devices/{device['id']}/"
    header = {'Authorization': 'Token ' + os.getenv('EP_FA_TOKEN')}
    if not body.get('id', None):
        body['id'] = device['id']
    try:
        response = requests.put(url, headers=header, json=body )
        response.raise_for_status()
    except Exception as e:
        logging.critical(f"{device['identifier']} Could not update in FA, exception was {e}")
        raise #todo remove?

def create_fa_device(device):
    #TODO this needs to be propperly made :'D
    url = 'http://facilityadmin/api/internal/generic-devices/v3/devices/'
    headers = conf.get_facilityadmin_authorized_header_dict()
    try:
        response = requests.post(url, headers=headers, json=device)
        response.raise_for_status()
        logging.info(response.content)
    except Exception as e:
        """
        try:
            #HACKY :D could perhaps forloop or check for active switches, but oh well
            device['identifier'] = str(int(device['identifier'])+3)
            response = requests.post(url, headers=headers, json=device)
            response.raise_for_status()
            logging.info(response.content)
        except Exception as e:"""
        logging.critical(f'Could not create new device in FA cause of {e}, data we sent was {device}')

