import requests
import logging
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from getRouterSignal import get_teltonika_signal

logging.basicConfig(level=logging.INFO)
from epconf import get_conf, get_device_auth, get_device_url, update_fa_device
conf = get_conf()
def get_data_from_fa():
    url = f"http://facilityadmin/api/internal/generic-devices/v2/devices/?page=1"
    data = []
    while url is not None:
        try:
            headers = {
                'Authorization': 'Token <FA_TOKEN_HERE>'
            }
            response = requests.get(url, headers=headers).json()
            data = data + response['results']
            url = response['next']
        except Exception as e:
            logging.warning(f'Could not get results from response, data was: {response}, url was: {url}, exception was {e}')
            raise

    return data



def main():
    from tqdm import tqdm
    logging.info('halo')
    data = get_data_from_fa()
    facilities = conf.get_facilities_with_environment()
    devices = [i for i in data if i["type"]["id"] in (14, 20, 21, 27)]
    count_hardware = []
    moxa = []
    soltech = []
    teltonika = []

    for device in tqdm(devices):
        try:
            print("Device Name: " + device['type']['key'] and facilities[device['periods'][0]['facility_key']]['environment'].lower() in ('prod', 'ep'))
            count_hardware.append(device)
            if device['type']['id'] == 14:
               moxa.append(device)
            if device['type']['id'] == 20:
               soltech.append(device)
            if device['type']['id'] in (21, 27):
               teltonika.append(device)
        except Exception as e:
            print(f'{device["identifier"]} had exception {e}')



    logging.info(f'Found {len(count_hardware)} active hardware-devices in total')
    logging.info(f'Found {len(moxa)} Moxa relays')
    logging.info(f'Found {len(soltech)} Soltech switches')
    logging.info(f'Found {len(teltonika)} Teltonika routers')



    #cameras = get_data_from_fa(device_type="camera")
    #logging.info(f'Found {len(cameras)} cameras, here is one of them: {cameras[0]}')
    ## print(switchRes.status_code)
    ##print(switchRes.text)




if __name__ == '__main__':
 main()