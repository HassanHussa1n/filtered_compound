import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth

def main():
    identifier = "1090013"
    url = f"http://facilityadmin/api/internal/generic-devices/v2/devices/?search={identifier}"

    headers = {
        'Authorization': 'Token <FA_TOKEN_HERE>'
    }

    respons = requests.get(url=url, headers=headers)

    #legger data fra FA inn i variabler
    username = respons.json()[0]['deviceauth']['username']
    password = respons.json()[0]['deviceauth']['password']
    deviceIP = respons.json()[0]['networkdevice']['ip_address']
    deviceIPPort = respons.json()[0]['networkdevice']['ip_port']

    switchUrl = f"http://{deviceIP}:{deviceIPPort}/"
    auth = respons.json()[0]['type']['communication_type']

    if auth == 'http_basic':
        switchRes = requests.get(switchUrl, auth=HTTPBasicAuth(username, password))
    elif auth == 'http_digest':
        switchRes = requests.get(switchUrl, auth=HTTPDigestAuth(username, password))
    elif auth is None:
        loginUrl = switchUrl + 'cgi-bin/login'
        data = ('{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": [ "00000000000000000000000000000000", "session", "login",'
' { "username": '
                f'{username}'
                ', "password": '
                f'{password}'
                '  } ] }')




        



        loginRes = requests.post(loginUrl, headers= headers, cookies=cookies, data= '{"username": "{username}","password": "{password}"}'.format(username = username, password = password))
        print(loginRes.status_code)
        print(loginRes.text)
        try:
            print(loginRes.json())
        except:
            print('could not print json responce')
    else:
        switchRes = requests.get(switchUrl)
        print(f'Reached unimplemented authentication method, Auth method was {auth}')


    print(switchRes.status_code)



if __name__ == '__main__':
 main()