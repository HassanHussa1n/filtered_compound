import requests
import logging
import csv
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from getRouterSignal import get_teltonika_signal

logging.basicConfig(level=logging.INFO)
from epconf import get_conf, get_device_auth, get_device_url, update_fa_device
conf = get_conf()

#Forklaring
"""Denne koden brukes for å se over devices med manglende informasjon i Facility Admin, og sende det over til en CSV fil. Bytt navnet til filen i slutten av linje 182."""

def get_data_from_fa(): #La Stå
    url = f"http://facilityadmin/api/internal/generic-devices/v2/devices/?page=1"
    data = []
    while url is not None:
        try:
            headers = {
                'Authorization': 'Token <TOKEN_HERE>'
            }
            response = requests.get(url, headers=headers).json()
            data = data + response['results']
            url = response['next']
        except Exception as e:
            logging.warning(f'Could not get results from response, data was: {response}, url was: {url}, exception was {e}')
            raise

    return data





def getCameras(data):
    from tqdm import tqdm
    logging.info('hei')
    # data = get_data_from_fa()
    devices = [i for i in data if i["type"]["id"] in (20, 22, 30, 12, 28, 29, 17, 24, 2, 13, 16, 1)]
    count_hardware = []

    cameras = [i for i in data if i["type"]["id"] in (22, 30, 12, 28, 29, 17, 24, 2, 13, 16, 1)]


    print(f'Found {len(cameras)} norwegian cameras!')

    return cameras

def getTeltonikas(data):

    from tqdm import tqdm
    logging.info('hei')
    #data = get_data_from_fa()
    devices = [i for i in data if i["type"]["id"] in (20, 22, 30, 12, 28, 29, 17, 24, 2, 13, 16, 1)]
    count_hardware = []

    teltonikas = [i for i in data if i["type"]["id"] in (21, 27)]




    print(f'Found {len(teltonikas)} norwegian cameras!')

    return teltonikas

def getSoltechs(data):

    from tqdm import tqdm

    #data = get_data_from_fa()

    devices = [i for i in data if i["type"]["id"] in (20, 22, 30, 12, 28, 29, 17, 24, 2, 13, 16, 1)]
    count_hardware = []


    soltechs = [i for i in data if i["type"]["id"] == 20]


    print(f'Found {len(soltechs)} norwegian soltechs!')

    return soltechs


def write_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['DeviceID', 'MissingInfo']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            for key, value in item.items():
                writer.writerow({'DeviceID': key, 'MissingInfo': value})


if __name__ == '__main__':
    fetched_data = get_data_from_fa()
    facilities = conf.get_facilities_with_environment()
    soltechs = getSoltechs(fetched_data)
    teltonikas = getTeltonikas(fetched_data)
    cameras = getCameras(fetched_data)
    uten_periods = []
    uten_deviceauth = []
    uten_networkdevice = []
    uten_lane = []
    count_hardware = []
    for device in cameras:
        try:
            facility_env = facilities[device['periods'][0]['facility_key']]['environment'].lower()
            is_valid_environment = facility_env in ('prod', 'ep')
            if is_valid_environment and device['periods']:
                if not device['periods'][0]['end']:
                  count_hardware.append(device)

        except Exception as e:

            print(f"Gikk ikke med device: {device['identifier']}, fordi error er: {e}")

    for device in count_hardware:
        try:

                if not device['periods']:

                   uten_periods.append({device['identifier']: "Mangler hele periods i FA!"})

                if not device['periods'][0]['facility_key']:

                   uten_periods.append({device['identifier']: "Mangler facility i FA!"})


                if not device['periods'][0]['direction']:

                   uten_periods.append({device['identifier']: "Mangler direction i FA!"})

                if not device['deviceauth']:

                    uten_deviceauth.append({device['identifier']: "Mangler hele deviceauth i FA, RDC - avdeling?"})

                if not device['deviceauth']['username']:

                    uten_deviceauth.append({device['identifier']: "Mangler brukernavn i FA!"})

                if not device['deviceauth']['password']:

                    uten_deviceauth.append({device['identifier']: "Mangler password i FA!"})

                if not device['networkdevice']:

                    uten_networkdevice.append({device['identifier']: "Mangler hele networkdevice i FA!"})

                if not device['networkdevice']['ip_address']:

                    uten_networkdevice.append({device['identifier']: "Mangler IP-addresse i FA!"})

                if not device['networkdevice']['mac_address']:

                    uten_networkdevice.append({device['identifier']: "Mangler mac_addresse i FA!"})

                if not device['camerameta']:

                    uten_lane.append({device['identifier']: "Mangler hele camerameta i FA!"})

                if not device['camerameta']['lane_identifier']:

                    uten_lane.append({device['identifier']: "Mangler lane i FA!"})

                if not device['lane']['identifier']:

                    uten_lane.append({device['identifier']: "Mangler lane id (entry_with_exit for eks) i FA!"})




        except Exception as e:
            print(f'{device["identifier"]} has error : {e}')


    #print(f"Device har ikke periods: {uten_periods}\n")
    #print(f"Device har ikke deviceauth: {uten_deviceauth}\n")
    #print(f"Device har ikke networkdevice info: {uten_networkdevice}\n")
    #print(f"Device har ikke lane info: {uten_lane}\n")

    write_to_csv(uten_periods + uten_deviceauth + uten_networkdevice + uten_lane, 'devices_missing_info.csv')
