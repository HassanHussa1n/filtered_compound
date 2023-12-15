import os
import time
import csv
from tqdm import tqdm
import requests
from requests.auth import HTTPBasicAuth
import sys, getopt
import threading
from epconf import get_conf
from epcommon.log import get_logger
import http
conf = get_conf()
log = get_logger('log')


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

    return norwegian_tattiles

def tattile_f01750_f01752(device: dict, remote: bool, _username=None, _password=None, address=None):
  default_password = False
  if _username is not None:
    username = _username
  elif device['deviceauth'] is not None and device['deviceauth'].get('username', None) is not None:
    username = device['deviceauth']['username']
  else:
    log.warning(
      "no username was provided and no username was found in facilityadmin, fix this, attempting default username")
    username = 'superuser'

  if _password is not None:
    password = _password
  elif device['deviceauth'] is not None and device['deviceauth'].get('password', None) is not None:
    password = device['deviceauth']['password']
  else:
    log.warning(
      "no password was provided and no password was found in facilityadmin, fix this, attempting default password")
    password = 'superuser'
    default_password = True

  identifier = device['identifier']
  auth = HTTPBasicAuth(username=username, password=password)
  if address is not None:
    _url = f'http://{address}'
  elif remote:
    port = str(device["networkdevice"].get("ip_port","80")) if device["networkdevice"].get("ip_port","80") is not None else "80"
    _url = f'http://{device["networkdevice"]["ip_address"]}:{port}'
    print(_url)
    print(port)
  else:
    _url = 'http://192.168.0.21'

  try:
    response = requests.head(_url)
    #response.raise_for_status()
    log.info(f'{identifier} established connection to {_url} checking authentication')
    api = '/cgi-bin/CGI_PlateConf.cgi?VegaType=Access&EnableSkewCorrection=1&Apply=Apply'
    reqrestarting(_url, auth,api=api, extra_auth=None)


  except:
    log.warning(
      f'{identifier} could not establish connection to {_url}')
    raise

def reqrestarting(_url, auth, api, extra_auth=None):
    api = '/cgi-bin/CGI_PlateConf.cgi?VegaType=Access&EnableSkewCorrection=1&Apply=Apply'
    attempt = 0
    max_attempts = 10
    output = 0
    response = requests.get(_url + api, auth=auth)
    if response.status_code != 200:
        print(response)
            # raise Exception('Error authenticationg password change...')
    log.info('started restart')
    time.sleep(10)
    while output != 200 and attempt <= max_attempts:
            try:
                response = requests.get(f'{_url}/cgi-bin/CGI_DeviceInfo.cgi', auth=auth, timeout=3)
                output = response.status_code
                time.sleep(2)
                if output != 200:
                    response = requests.get(f'{_url}/cgi-bin/CGI_DeviceInfo.cgi', auth=extra_auth, timeout=3)
                    response.raise_for_status()
                    if response.status_code == 200:
                        break
            except Exception as e:
                print(e)
                time.sleep(2)
    log.info('finished restart')


def process_device(device):
    try:
        tattile_f01750_f01752(device=device, remote=True)
    except Exception as e:
        log.error(f"Feil ved prosessering av device: {device['identifier']}: {e}")




    if __name__ == '__main__':
        devices = get_tattile_devices()
        threads = []

        for device in tqdm(devices):
            thread = threading.Thread(target=process_device, args=(device,))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()