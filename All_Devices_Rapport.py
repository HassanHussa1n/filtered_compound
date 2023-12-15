import csv

from dateutil import parser
from datetime import datetime

import pytz
import requests
import os
from tqdm import tqdm
from tabulate import tabulate
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import logging
logging.basicConfig(level=logging.INFO)
import pytz
from epconf import get_conf, get_device_auth, get_device_url, update_fa_device
conf = get_conf()




#Forklaring
"""Denne koden brukes som regel til å produsere en csv fil som inneholder info angående nye devices vi har fått inn siden en viss dato. Bytt datoen om det trengs på linje 92, og kjør koden."""


def get_all_devices(dt, output_csv_filename):
    facilities = conf.get_facilities_with_environment()
    logging.info(f'got {len(facilities)} facilities')
    devices = conf.get_active_devices()
    logging.info(f'got {len(devices)} devices')
    t_devices = [d for d in devices if d['type']['id'] in (21, 5, 14, 30, 12, 28, 29, 17)] #Juster hvis nødvendig

    device_rapport_data = [

    ]


    timezone = pytz.timezone('Europe/Oslo')
    last_run_date = timezone.localize(dt)
    current_date = datetime.now()                           # Dagens dato




    for device in tqdm(t_devices):

            try:
                if not device['periods']:
                    logging.warning(
                        f'Got device with no periods, device identifier was {device["identifier"]}, Name = {device["type"]["model_number"]}')
                elif 'created_at' in device['periods'][0]:
                    date_string = device['periods'][0]['created_at']
                    date_obj = datetime.fromisoformat(date_string)
                    parsed_date = parser.isoparse(date_string)
                    opprettet = parsed_date.strftime("%Y-%m-%d")


                    if date_obj > last_run_date and device['identifier'] and device['type']['model_number']:
                        device_rapport_data.append(
                            [device['identifier'],
                             device['type']['model_number'],
                             device['periods'][0]['facility'],
                             device['periods'][0]['facility_name'], opprettet])

                else:
                    logging.warning(f'Rar data struktur for device: {device}')
            except IndexError as e:

                logging.error(f'Error processing device: {e}')
                continue

    headers = ["Device Id:", "Device Name:", "Avdelingsnummer:", "Avdelingsnavn:", "Opprettet:"]

    with open(output_csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)


        csv_writer.writerow(headers)


        for row in device_rapport_data:
            csv_writer.writerow(row)






if __name__ == '__main__':

   try:

    dt = datetime(2023, 11, 20) # Endre datoen
    output_csv_filename = 'Device_Rapport_271123_test.csv'
    get_all_devices(dt, output_csv_filename)
    fil_plassering = os.path.basename(f'/root/{output_csv_filename}')
    logging.info(f"Prosessen er fullført, sjekk filen: {fil_plassering}")

   except Exception as e:
    logging.info(f"Det var noe feil med data, Sjekk: {e}")