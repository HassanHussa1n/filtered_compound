import requests
import os
from tqdm import tqdm
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import logging
logging.basicConfig(level=logging.INFO)

from epconf import get_conf, get_device_auth, get_device_url, update_fa_device
conf = get_conf()


#Sjekke alle 10.80 adresser, og sende request til alle 10010 og 10011 porter, for å se om de svarer og hvis de svarer så kan vi sette dem inn i FA.
#Sjekke om begge typer teltonikas er i FA, og hvis de ikke er, legge dem inn i FA.
# hente alle 10.80 adresser, hente devices, legg til ip i liste hvis den allerede ikke ligger i liste starts with og (append)




def get_lost_devices():
    #facilities = conf.get_facilities_with_environment()
    #logging.info(f'got {len(facilities)} facilities')
    devices = conf.get_active_devices()
    logging.info(f'got {len(devices)} devices')
    t_devices = [d for d in devices if d['type']['id'] in (20, 21, 27)]
    logging.info(f'got {len(t_devices)} soltech switches')

    ips_with_1080 = []
    for device in tqdm(t_devices):
        if device['networkdevice']['ip_address'] is None:
         logging.info(f'Device does not have an IP: {device["identifier"]}')
         continue

        if (device['networkdevice']['ip_address'].startswith('10.80') 
                and device['networkdevice']['ip_address'] not in ips_with_1080):
         ips_with_1080.append(device['networkdevice']['ip_address'])


    logging.info(f'got {len(ips_with_1080)} 10.80 IP ranges')
         # logging.warning(f'Could not get signal for device {teltonika["identifier"]}, exception was {e}')
    data = []
    for ip_address in tqdm(ips_with_1080):
        #Teltonikas always have 10000 as port on 10.80
        teltonika_url = f'http://{ip_address}:10000/ubus'
        #Soltech urls:
        soltech_url_1 = f'http://{ip_address}:10010'
        soltech_url_2 = f'http://{ip_address}:10011'




        check_teltonika(teltonika_url)

        data = get_device_auth(device)





def check_teltonika(url):

    data = '{{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": [ "00000000000000000000000000000000", "session", "login", { "username": "{admin}", "password": "{PASSWORD_HERE}"  } ] }}'

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        response = response.json()

    except Exception as e:
        print(f'could not reach {url} exception was {e}')



    logging.info(f"{url}  got ubus session id {response['result'][1]['ubus_rpc_session']}")
    ubus_rpc_session = response['result'][1]['ubus_rpc_session']

    data = ('{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": ['
            f'"{ubus_rpc_session}"'
            ', "file", "exec", { "command":"mnf_info", "params": ["--name"] } ] }')

    try:
        response = requests.post(url, data=data).json()
        response.raise_for_status()
    except Exception as e:
        logging.warning(f'Got exception while posting command to teltonika with {url} exception was {e}, command was {data}')

    logging.debug(response)

    stdout = response['result'][1]['stdout']

    logging.info(f"{url} got result: {stdout}")


def check_soltech():

    return




if __name__ == '__main__':
    get_lost_devices()