import requests
import logging
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from getRouterSignal import get_teltonika_signal

logging.basicConfig(level=logging.INFO)
from epconf import get_conf, get_device_auth, get_device_url, update_fa_device
conf = get_conf()
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
    global switchRes
    from tqdm import tqdm
    logging.info('hei')
    #data = get_data_from_fa()
    devices = [i for i in data if i["type"]["id"] in (20, 22, 30, 12, 28, 29, 17, 24, 2, 13, 16, 1)]
    count_hardware = []

    cameras = [i for i in data if i["type"]["id"] in (22, 30, 12, 28, 29, 17, 24, 2, 13, 16, 1)]
    soltechs = [i for i in data if i["type"]["id"] == 20]



    print(f'Found {len(cameras)} norwegian cameras!')

    return cameras

def getSoltechs(data):
    global switchRes
    from tqdm import tqdm

    #data = get_data_from_fa()

    devices = [i for i in data if i["type"]["id"] in (20, 22, 30, 12, 28, 29, 17, 24, 2, 13, 16, 1)]
    count_hardware = []

    cameras = [i for i in data if i["type"]["id"] in (22, 30, 12, 28, 29, 17, 24, 2, 13, 16, 1)]
    soltechs = [i for i in data if i["type"]["id"] == 20]


    print(f'Found {len(soltechs)} norwegian soltechs!')

    return soltechs

def fetch_mac_and_ports(device):
    try:
        if device['type']['id'] == 20:
            username = device['deviceauth']['username']
            password = device['deviceauth']['password']
            deviceIP = device['networkdevice']['ip_address']
            deviceIPPort = device['networkdevice']['ip_port']

            switchUrl = f"http://{deviceIP}:{deviceIPPort}/config/dynamic_mac_table"
            auth = device['type']['communication_type']
            if auth == 'http_basic':
                switchRes = requests.get(switchUrl, auth=HTTPBasicAuth(username, password))
                #print(f"Her er responsen fra {device['identifier']} : {switchRes.status_code}")
                #print(f"Her er responsen fra {device['identifier']} : {switchRes.text}")
            elif auth == 'http_digest':
                switchRes = requests.get(switchUrl, auth=HTTPDigestAuth(username, password))
                #print(f"Her er responsen fra {device['identifier']} : {switchRes.status_code}")
                #print(f"Her er responsen fra {device['identifier']} : {switchRes.text}")
            elif auth is None:
                loginUrl = switchUrl + 'cgi-bin/login'
                data = (
                    '{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": [ "00000000000000000000000000000000", "session", "login",'
                    ' { "username": '
                    f'{username}'
                    ', "password": '
                    f'{password}'
                    '  } ] }')
                pass

            return parse_switch_response(switchRes)
    except Exception as e:
        logging.warning(f'Error fetching MAC and Ports for device {device["identifier"]}: {e}')
    return None


def parse_switch_response(response): #La Stå
  try:
    response_text = response.text
    lines = response_text.split('|')  # Split the response into lines based on the pipe character
    parsed_data = {}

    for line in lines:
        parts = line.split('/')  # Split each line into parts using '/'
        mac_address = parts[0]  # The first part is the MAC address
        ports = "/".join(parts[4:])  # The rest are ports

        parsed_data[mac_address] = "/".join(ports)  # Store MAC address and ports in a dictionary
  except Exception as e:
      logging.warning(f'Error parsing the request: {e}')
      return None


  return parsed_data

def decode_ports(ports_value):
    used_ports = []
    for i, port_status in enumerate(ports_value):
        if port_status == '1':
            used_ports.append(i + 1)  # Adding 1 to match port numbering (assuming 1-indexed)
    return used_ports

def find_port_number(data):
  # Check if the data contains only 0s and 1s
  if not all(bit in ['0', '1'] for bit in data):
    return "Invalid data format"

  # Check for the special cases where we should skip
  if data.count('1') != 1 or data.count('0') == len(data) or data.count('0') == 0:
    return "Skip"

  # Find the index of '1' in the data
  port_number = data.index('1') + 1
  return port_number


if __name__ == '__main__':
    fetched_data = get_data_from_fa()
    facilities = conf.get_facilities_with_environment()
    soltechs = getSoltechs(fetched_data)
    cameras = getCameras(fetched_data)
    uten_mac = []
    good_list = []
    check_up = []
    count_hardware = []
    for device in cameras:
        try:
            facility_env = facilities[device['periods'][0]['facility_key']]['environment'].lower()
            is_valid_environment = facility_env in ('prod', 'ep')
            if is_valid_environment:
                count_hardware.append(device)

        except Exception as e:

            print(f"Gikk ikke med device: {device['identifier']}, fordi error er: {e}")

    for device in count_hardware:
        try:

            if not device['networkdevice']:

               print(f'device har ikke networkdevice: {device["identifier"]}')
               continue

            if device['networkdevice']['mac_address']:
               good_list.append(device['networkdevice']['mac_address'])



            elif device['networkdevice']['mac_address'] == "Null" or not device['networkdevice']['mac_address']:

               if not device['periods'] and device['periods'][0]['start']:
                   print(f"Device har ikke periods: {device['identifier']}")
                   continue
               if not device['periods'][0]['end']:

                   uten_mac.append(device['identifier'])

            else:
                check_up.append(device['identifier'])



        except Exception as e:
            print(f'{device["identifier"]} has error : {e}')


    for device in good_list:

        if good_list:

           modified_list = [mac.replace(":", "").replace("-", "").lower() for mac in good_list]


    print(modified_list)
    #print(f"Device har ikke MAC addresse: {uten_mac}")
    #print(f"Device har MAC addresse: {good_list}")
    #print(f"Device trenger check-up: {check_up}")
    parsed_soltech_macs = []
    for device in soltechs:
        mac_ports = fetch_mac_and_ports(device)
        if mac_ports:
            print(f"\033[1mDevice ID: {device['identifier']} and its MAC table: \033[0m")
            for mac_address, ports in mac_ports.items():
                parsed_mac = mac_address.replace(":", "").replace("-", "")
                parsed_soltech_macs.append(parsed_mac)
                parsed_ports = ports.replace("/", "")
                port_number = find_port_number(parsed_ports)

                #print(f"Device ID: {device['identifier']} - MAC Address: {parsed_mac} - Ports: {port_number}")

# Måle opp mac address med identifier fra FA

    print(f"Camera Mac:   {len(modified_list)}")
    print(f"Soltech - Camera Mac:   {len(parsed_soltech_macs)}")

    matched_macs = set(parsed_soltech_macs) & set(modified_list)
    unmatched_macs = set(modified_list) - set(parsed_soltech_macs)


    print("Matched MAC addresses:")
    for mac in matched_macs:
        print(f"We have a match!")
        print(mac)

    print("\nUnmatched MAC addresses:")
    for mac in unmatched_macs:
        print(mac)