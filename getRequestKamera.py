import requests
from requests.auth import HTTPDigestAuth

def main():
    identifier = "4455104"
    url = f"http://facilityadmin/api/internal/generic-devices/v2/devices/?search={identifier}"

    headers = {
        'Authorization': 'Token <FA_TOKEN_HERE>'
    }

    respons = requests.get(url=url, headers=headers)


    password = respons.json()[0]['deviceauth']['username']
    username = respons.json()[0]['deviceauth']['password']
    deviceIP = respons.json()[0]['networkdevice']['ip_address']
    deviceIPPort = respons.json()[0]['networkdevice']['ip_port']

    camera_dir = respons.json()[0]['description']
    camera_dir2 = respons.json()[0]['periods'][0]['direction']
    cameraUrl = f"http://{deviceIP}:{deviceIPPort}"

  #  cameraRes = requests.get(cameraUrl,auth=HTTPDigestAuth(username, password))

  #  print(cameraRes.status_code)
   # print(cameraRes.text)
    print(camera_dir)
    print(camera_dir2)


if __name__ == '__main__':
 main()
