#First, get cameras from the facility that has "EP" environment - V
#Then, we get a request that delivers us the subscription key the camera uses.
#Lastly, import this data to a CSV file.

import xml.etree.ElementTree as ET
import os
import time
import csv
from tqdm import tqdm
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import sys, getopt
import threading

from epcommon import log
from epconf import get_conf, conf
from epcommon.log import get_logger

conf = get_conf()
log = get_logger('log')


#Forklaring
"""Denne koden brukes for å få en oversikt over EasyPay Subscription Keys for Axis - Kamera."""

def write_to_csv(data):
  header = ['Identifier', 'Key', 'Is JSON Active?']
  with open('Vaxtor_Subscriptions_Overview.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    for row in data:
      writer.writerow(row)
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

  output_data = []
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
        cameraUrl = f"http://{deviceIP}:80/local/Vaxreader/alpr.cgi"
      else:
        cameraUrl = f"http://{deviceIP}:{deviceIPPort}/local/Vaxreader/alpr.cgi"
      try:

          response = requests.get(cameraUrl, auth=HTTPDigestAuth(device_username, device_password), timeout=15)

          log.info(f'Identifier: {device["identifier"]} + Status code: {response.status_code}')

      except Exception as e:

        log.warning(f"Not able to connect to device: {device['identifier']}")

      xml_data = response.text
      authorization_key, is_json_active = get_authorization_key(xml_data)

      if authorization_key is not None:
        log.info(f"Identifier: {device['identifier']} has authorization key: {authorization_key}, with the JSON Active status being: {is_json_active}")
        output_data.append([device['identifier'], authorization_key, is_json_active])

      else:
        log.warning(f"No authorization key found for device: {device['identifier']}")

  write_to_csv(output_data)


def get_authorization_key(xml_data):
  try:
    root = ET.fromstring(xml_data)
    json_element = root.find(".//json")
    if json_element is not None:
      authorization_key = json_element.get("authorization")
      json_active = json_element.get("active")
      return authorization_key, json_active
    else:
      log.warning("JSON element not found in XML.")
      return None, False
  except ET.ParseError as e:
    log.error(f"Error parsing XML data: {e}")
    return None, False


if __name__ == '__main__':
    get_ep_devices()