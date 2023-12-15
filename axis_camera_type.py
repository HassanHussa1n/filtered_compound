import requests
import os
from tqdm import tqdm
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import logging
logging.basicConfig(level=logging.INFO)


from epconf import get_conf, get_device_auth, get_device_url, update_fa_device
conf = get_conf()



#Forklaring
"""Denne koden brukes for å sjekke hvor mange forskjellige typer Axis - Kamera vi har."""

def get_axis_devices():
    facilities = conf.get_facilities_with_environment()
    logging.info(f'got {len(facilities)} facilities')
    devices = conf.get_active_devices()
    logging.info(f'got {len(devices)} devices')
    t_devices = [d for d in devices if d['type']['id'] in (30, 12, 28, 29, 17)]
    logging.info(f'got {len(t_devices)} axis devices')

    norwegian_axises = []
    axis_q1455 = []
    axis_q1785 = []
    axis_q3536 = []
    axis_q1700 = []
    axis_q3536_lve = []
    for device in tqdm(t_devices):
        if not device['periods']:
            logging.warning(f'got device with no periods, device identifier was {device["identifier"]}')
            continue
        if not facilities.get(device['periods'][0]['facility_key'], None):
            logging.warning(f'facility that aint in facilities??, device identifier was {device["identifier"]}, facility was {device["periods"][0]["facility_key"]}')
            continue
        if facilities[device['periods'][0]['facility_key']]['environment'].lower() in ('prod', 'ep'):
            norwegian_axises.append(device)

            if not device['type']['model_number']:
                logging.warning(f'Device does not have a normal Type or Model Number')
                continue
            if device['type']['id'] == 30:
                axis_q1455.append(device)
            if device['type']['id'] == 12:
                axis_q1785.append(device)
            if device['type']['id'] == 28:
                axis_q3536.append(device)
            if device['type']['id'] == 29:
                axis_q1700.append(device)
            if device['type']['id'] == 17:
                axis_q3536_lve.append(device)



    logging.info(f'got {len(norwegian_axises)} norwegian axises')
    logging.info(f'first device in list: {norwegian_axises[0]}')
    logging.info(f'Antall Q1455 - kameraer er: {len(axis_q1455)}')
    logging.info(f'Antall Q1785 - kameraer er: {len(axis_q1785)}')
    logging.info(f'Antall Q3536 - kameraer er: {len(axis_q3536)}')
    logging.info(f'Antall Q1700 - kameraer er: {len(axis_q1700)}')
    logging.info(f'Antall Q3536-lve - kameraer er: {len(axis_q3536_lve)}')

    axis_device_type_ids = {"axis_q1455": 30,
                               "axis_q1785": 12,
                               "axis_q3536": 28,
                               "axis_q1700": 29,
                               "axis_q3536_lve": 17}











if __name__ == '__main__':
    get_axis_devices()
