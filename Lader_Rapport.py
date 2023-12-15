from datetime import datetime

import requests

def Lader_Rapport():
    # Define the API endpoint for the charging stations status
    api_url = "http://facilityadmin/api/internal/v1/chargers/"

    headers = {
        'Authorization': 'Token <FA_TOKEN_HERE>' #'Token 49b34c1681dfc004df524f74d441b9ff2632c711'
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors

        charging_stations_data = response.json()
        available_chargers = []
        unknown_chargers = []
        unavailable_chargers = []
        zaptec = []
        evil = []
        defa = []
        easee = []
        schneider_electric_lbc = []
        # Loop through each charging station
        for station in charging_stations_data:

            station_name = station.get("shorthand_identifier")
            station_status = station.get("is_active")
            provider = station.get("provider")
            facility = station.get("facility")
            stop_time = None  # Default value in case "stop" key is not present or has a null value
            periods = station.get("periods")

            if periods:
                for period in periods:
                     # Check if "stop" key exists in the current period
                        start_time = period.get("start")
                        stop_time = period.get("stop")


                        if start_time and stop_time:  # Check if stop_time is not None
                            if isinstance(start_time, str) and isinstance(stop_time, str):
                                try:
                                    start_datetime = datetime.fromisoformat(start_time)
                                    start_dateonly = start_datetime.date()
                                    formatted_startdate = start_dateonly.strftime("%d.%m.%Y")

                                    stop_datetime = datetime.fromisoformat(stop_time)
                                    stop_dateonly = stop_datetime.date()
                                    formatted_stopdate = stop_dateonly.strftime("%d.%m.%Y")

                                    target_date = datetime.now()
                                    target_dateonly = target_date.date()
                                    formatted_targetdate = target_dateonly.strftime("%d.%m.%Y")

                                    if formatted_startdate > formatted_targetdate:
                                        unavailable_chargers.append(station_name)

                                    elif formatted_startdate <= formatted_targetdate and formatted_stopdate is None:
                                        available_chargers.append(station_name)

                                    elif formatted_startdate <= formatted_targetdate and formatted_stopdate and formatted_stopdate > formatted_targetdate:
                                        available_chargers.append(station_name)

                                    else:

                                        unavailable_chargers.append(station_name)

                                except ValueError:
                                    print(f"Invalid stop_time format: {stop_time}")
                            else:
                                print(f"stop_time is not a string: {stop_time}")
                        else:
                            unknown_chargers.append(station_name)

        print(f"We have gotten a total of {len(available_chargers)} available chargers")
        print(f"We have gotten a total of {len(unavailable_chargers)} unavailable chargers")
        print(f"We have gotten a total of {len(unknown_chargers)} unknown chargers")

    except requests.exceptions.HTTPError as e:
        print(f"Failed to get data. HTTP status code: {e.response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    Lader_Rapport()
