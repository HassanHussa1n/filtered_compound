import requests
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)



def get_data_from_fa(device_type):

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

    camera = get_data_from_fa(device_type="camera")

    facility = "4455"
    antall_kamera = []
    for facility_cameras in tqdm(camera):
        try:
            if facility_cameras['periods'][0]['facility'].startswith(facility):
               antall_kamera.append(facility_cameras)
        except Exception as e:
            logging.info(f"Sure you typed in the right facility name? {e}")
            print(f"Sure you typed in the right facility name? {e}")
    print(f"Facility {facility} has {len(antall_kamera)} cameras.")


if __name__ == '__main__':
    main()
