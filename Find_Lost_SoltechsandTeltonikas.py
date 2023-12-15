import requests
import logging
from epconf import get_conf, create_fa_device
from threading import Thread
from requests.auth import HTTPBasicAuth

logging.basicConfig(level=logging.INFO)

conf = get_conf()
active_devices = conf.get_active_devices()
def get_lost_devices():
    active_ips = {device['networkdevice']['ip_address'] for device in active_devices if
                  device['networkdevice'] and device['networkdevice']['ip_address'] and device['type']['id'] in (20, 21, 27)}

    logging.info(f'Got {len(active_ips)} active IP addresses')

    #t_devices = [d for d in active_devices if d['type']['id'] in (20, 21, 27)]
    #logging.info(f'Got {len(t_devices)} soltech switches')


    subnet = '10.80.56'
    ip_range = range(256)
    tasks = []
    auth = {
        'username': 'admin',
        'password': 'PASSWORD_HERE'
    }
    for i in ip_range:
        ip_address = f'{subnet}.{i}'

        if ip_address in active_ips:
            logging.debug(f'Skipping {ip_address}, already in use.')
            continue


        # Teltonika always have 10000 as the port on 10.80
        """
        teltonika_url = f'http://{ip_address}:10000/ubus'
        

        task = Thread(target=check_teltonika, args=[teltonika_url, auth])
        task.start()
        tasks.append(task)
        """

        #check_teltonika(teltonika_url, auth)

        # Soltech URLs:
        task = Thread(target=check_soltech, args=[ip_address, "10010", auth])
        task2 = Thread(target=check_soltech, args=[ip_address, "10011", auth])
        task.start()
        task2.start()
        tasks.append(task)
        tasks.append(task2)
        #check_soltech(soltech_url_1, auth)
        #check_soltech(soltech_url_2, auth)

    for task in tasks:
        task.join()

def check_teltonika(url, auth):


    try:
        response = requests.post(url, auth=(auth['username'], auth['password']))
        response.raise_for_status()
        response_data = response.json()



    except Exception as e:
        logging.error(f'Could not reach {url}. Exception: {e}')


def check_soltech(ip_address, port, auth):
    url = f'http://{ip_address}:{port}/stat/sys'
    try:
        response = requests.get(url, auth=HTTPBasicAuth(auth['username'], auth['password']))
        response.raise_for_status()
        if "SFC8000HP" in response.text:
            #print(response.text)
            facilities = [d["periods"][0]["facility"] for
                          d in active_devices if d['networkdevice'] and d["periods"] and d['networkdevice']["ip_address"]==ip_address]
            if not all(facility == facilities[0] for facility in facilities):
                logging.warning(f'{ip_address} had multiple facilities, picking first anyways :D facilities was {facilities}')
            if len(facilities)==0:
                logging.critical(f'{ip_address} does not have any facilities ??')
                return
            #print(facilities[0])
            try:
                empty_device = {
                    "type": {"id": 20},
                    "networkdevice": {
                        "ip_address": ip_address,
                        "ip_port": int(port),
                        "mac_address": response.text.split("/")[0],
                        "switch_port": None,
                        "patch_port": None,
                        "local_ip_address": None,
                        "local_port": None
                    },
                    "periods": [
                        {
                            "facility": facilities[0]
                        }
                    ],
                    "deviceauth": {"username":"admin","password":"PASSWORD_HERE"},
                    "identifier": f"{facilities[0]}{port[-3:]}",
                    "shorthand_identifier": None,
                    "description": "Soltech",
                    "comment": "Automatically Created"
                }
            except Exception as e:
                logging.warning(f'could not create empty device to send to FA, error was {e}')
            create_fa_device(empty_device)


    except requests.exceptions.ConnectionError:
        logging.debug(f'Could not reach {url} cause of no connection, skipping')
    except Exception as e:
        logging.error(f'Could not reach {url}. Exception: {e}')


if __name__ == '__main__':
    get_lost_devices()
