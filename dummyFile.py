import os
import time
import csv
from tqdm import tqdm
import requests
from requests.auth import HTTPBasicAuth
import sys, getopt
import threading

from EnableSkewCorrection_Tattile import log
from epconf import get_conf, conf
from epcommon.log import get_logger

# ... (the rest of your code)
def get_tattile_devices():
    facilities = conf.get_facilities_with_environment()
    log.info(f'got {len(facilities)} facilities')
    devices = conf.get_active_devices()
    log.info(f'got {len(devices)} devices')
    t_devices = [d for d in devices if d['type']['id'] in (2, 13, 16)]
    log.info(f'got {len(t_devices)} tattile devices')

    norwegian_tattiles = []
    tattile_f01750 = []
    tattile_f01752 = []
    tattile_f02200 = []
    in_front = []
    in_rear = []
    out_front = []
    out_rear = []
    for device in tqdm(t_devices):
        if not device['periods']:
            log.warning(f'got device with no periods, device identifier was {device["identifier"]}')
            continue
        if not facilities.get(device['periods'][0]['facility_key'], None):
            log.warning(f'facility that aint in facilities??, device identifier was {device["identifier"]}, facility was {device["periods"][0]["facility_key"]}')
            continue
        if facilities[device['periods'][0]['facility_key']]['environment'].lower() in ('prod', 'ep'):
            norwegian_tattiles.append(device)


            if not device['type']['model_number']:
                log.warning(f'Device does not have a normal Type or Model Number')
                continue
            if device['type']['model_number'] == 'Tattile Vega Basic F01750':
                tattile_f01750.append(device)
            if device['type']['model_number'] == 'Tattile Vega Basic F01752':
                tattile_f01752.append(device)
            if device['type']['model_number'] == 'Tattile Vega Basic F02200':
                tattile_f02200.append(device)

    for device in tqdm(tattile_f01752):
        if not device['periods'] or not device['periods'][0]:
            log.warning(f'Got device with no periods, device identifier was {device["identifier"]}')
            continue

        if ('direction' in device['periods'][0] and device['periods'][0]['direction'] == 'in_front') or (
                'description' in device and device['description'] == 'IF'):
            in_front.append(device)
        if ('direction' in device['periods'][0] and device['periods'][0]['direction'] == 'in_rear') or (
                'description' in device and device['description'] == 'IR'):
            in_rear.append(device)
        if ('direction' in device['periods'][0] and device['periods'][0]['direction'] == 'out_front') or (
                'description' in device and device['description'] == 'OF'):
            out_front.append(device)
        if ('direction' in device['periods'][0] and device['periods'][0]['direction'] == 'out_rear') or (
                'description' in device and device['description'] == 'OR'):
            out_rear.append(device)

    log.info(f'got {len(in_front)} tattile devices')
    log.info(f'got {len(in_rear)} tattile devices')
    log.info(f'got {len(out_front)} tattile devices')
    log.info(f'got {len(out_rear)} tattile devices')

    return in_rear, out_rear



if __name__ == '__main__':

    devices = get_tattile_devices()


