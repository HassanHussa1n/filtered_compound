import requests
import os
from tqdm import tqdm
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import logging
logging.basicConfig(level=logging.INFO)


from epconf import get_conf, get_device_auth, get_device_url, update_fa_device
conf = get_conf()







def get_tattile_devices():
    facilities = conf.get_facilities_with_environment()
    logging.info(f'got {len(facilities)} facilities')
    devices = conf.get_active_devices()
    logging.info(f'got {len(devices)} devices')
    t_devices = [d for d in devices if d['type']['id'] == 20] #Juster hvis nødvendig
    logging.info(f'got {len(t_devices)} soltech switches')

    soltech_ikke_i_fa = []

    for device in tqdm(t_devices):
        if not device['periods']:
            logging.warning(f'got device with no periods, device identifier was {device["identifier"]}')
            soltech_ikke_i_fa.append(device)
        print(f'The soltech switch: {device["identifier"]}, belongs to {device["periods"][0]["facility_name"]}')

if __name__ == '__main__':
    get_tattile_devices()