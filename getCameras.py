import requests
import logging
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from getRouterSignal import get_teltonika_signal

logging.basicConfig(level=logging.INFO)
from epconf import get_conf, get_device_auth, get_device_url, update_fa_device
conf = get_conf()
def get_data_from_fa(device_type = "camera"):
    url = f"http://facilityadmin/api/internal/generic-devices/v2/devices/?page=1&active=2&type={device_type}"
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
    data = get_data_from_fa(device_type="camera")
    facilities = conf.get_facilities_with_environment()
    devices = [i for i in data if i["type"]["id"] in (22, 30, 12, 28, 29, 1, 24, 2, 13, 16)]
    count_device = []
    citysync = []
    axis = []
    tattile = []

    for device in tqdm(devices):
        try:
            print("Device Name: " + device['type']['key'] and facilities[device['periods'][0]['facility_key']]['environment'].lower() in ('prod', 'ep'))
            count_device.append(device)
            if device['type']['id'] == 1:
               citysync.append(device)
            if device['type']['id'] in (22, 30, 12, 28, 29, 17):
               axis.append(device)
            if device['type']['id'] in (24, 2, 13, 16):
               tattile.append(device)
        except Exception as e:
            print(f'{device["identifier"]} had exception {e}')



    logging.info(f'Found {len(count_device)} active cameras in total')
    logging.info(f'Found {len(citysync)} CitySync cameras')
    logging.info(f'Found {len(axis)} Axis cameras')
    logging.info(f'Found {len(tattile)} Tattile cameras')


    #cameras = get_data_from_fa(device_type="camera")
    #logging.info(f'Found {len(cameras)} cameras, here is one of them: {cameras[0]}')
## print(switchRes.status_code)
    ##print(switchRes.text)




if __name__ == '__main__':
 main()