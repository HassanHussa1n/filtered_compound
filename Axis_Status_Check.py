#First, get cameras from all facilities
#Then, we get a request that delivers us the plates from Vaxtor.
#Print the info: Offline, Bad Request, Check-Up.

import xml.etree.ElementTree as ET
import os
import time
import csv
from tqdm import tqdm
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import sys, getopt
import threading
from concurrent.futures import ThreadPoolExecutor

from epcommon import log
from epconf import get_conf, conf
from epcommon.log import get_logger

conf = get_conf()
log = get_logger('log')

#Forklaring
"""Denne koden brukes for å sjekke en status over Axis - Kamera, den gir ut to lister som output. Ene listen gir deg en oversikt over kamera som burde sjekkes opp pga lav leserate, og den andre viser offline eller unreachable kamera."""

def get_ep_devices():
  facilities = conf.get_facilities_with_environment()
  log.info(f'got {len(facilities)} facilities')
  devices = conf.get_active_devices()
  log.info(f'got {len(devices)} devices')
  t_devices = [d for d in devices if d['type']['id'] in (22, 30, 12, 28, 29, 17)]
  log.info(f'got {len(t_devices)} axis devices')

  norwegian_cameras = []

  for device in tqdm(t_devices):
    if not device['periods']:
      log.warning(f'got device with no periods, device identifier was {device["identifier"]}')
      continue
    if not facilities.get(device['periods'][0]['facility_key'], None):
      log.warning(
        f'facility that aint in facilities??, device identifier was {device["identifier"]}, facility was {device["periods"][0]["facility_key"]}')
      continue
    if facilities[device['periods'][0]['facility_key']]['environment'].lower() in ('prod', 'ep'):
      norwegian_cameras.append(device)

  log.info(f"Got {len(norwegian_cameras)} Norwegian Cameras")

  check_up_cameras = []

  offline_cameras = []
  for device in tqdm(norwegian_cameras):





      if 'networkdevice' not in device or not isinstance(device['networkdevice'], dict):
        log.warning(f"Network device information missing or invalid for device: {device['identifier']}")
        continue

      deviceIP = device['networkdevice']['ip_address']
      if deviceIP is None:
        log.warning(f"IP address not found for device: {device['identifier']}")
        continue

      deviceIPPort = device['networkdevice']['ip_port']
      if deviceIPPort is None:
        log.warning(f"IP port not found for device: {device['identifier']}")
        continue


      if not device['deviceauth']:
        log.info(f"This device doesnt have device authentication details: {device['identifier']}")
        continue
      device_username = device['deviceauth']['username']
      device_password = device['deviceauth']['password']
      if deviceIP.startswith("10.59"):
        cameraUrl = f"http://{deviceIP}:80/local/Vaxreader/plates.cgi?page=0"
      else:
        cameraUrl = f"http://{deviceIP}:{deviceIPPort}/local/Vaxreader/plates.cgi"
      try:

          response = requests.get(cameraUrl, auth=HTTPDigestAuth(device_username, device_password), timeout=30)

          log.info(f'Identifier: {device["identifier"]} + Status code: {response.status_code}')

          xml_data = response.text






          root = ET.fromstring(xml_data)
          resultset = root.find("resultset")
          if resultset is not None:

            results_value = resultset.get("results")

            if results_value is not None:
              results_int = int(results_value)
              if results_int < 5:
                 check_up_cameras.append({device['identifier'] : cameraUrl})
                 log.info(f"Vi har et kamera som ikke har plates: {device['identifier']}")

            else:
              log.warning("Results not found in XML.")
              check_up_cameras.append({device['identifier'] : cameraUrl})

          elif resultset is None:

            log.warning(f"Resultset not found in XML: {device['identifier']}")

          else:
            log.info(f'The device: {device["identifier"]} has read more than 5 plates')

      except ET.ParseError as parse_err:
        log.error(f"Error parsing XML data: {parse_err}")
        check_up_cameras.append({device['identifier'] + " + " + device['periods'][0]['facility_name'] : cameraUrl})

      except Exception as e:

        log.warning(f"Not able to connect to device: {device['identifier']} with error: {e}")
        offline_cameras.append({device['identifier'] + " + " + device['periods'][0]['facility_name'] : cameraUrl})






  log.info(f"These identifiers have read no plates: {check_up_cameras}")
  log.info(f"These identifiers are offline or unreachable: {offline_cameras}")








if __name__ == '__main__':
    get_ep_devices()