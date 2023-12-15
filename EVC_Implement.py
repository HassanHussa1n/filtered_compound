import csv


def csv_generator():

    chargestation_id = input(f"Skriv inn navnet på ladestasjonen: ") #Eksempel 1231- eller LAM31-EntityPro-  | Ikke skriv et tall bak!

    #Handle input
    while True:
        try:
            amount = int(input("Skriv inn antall ladere: "))  # Antall ladere gitt av prosjektleder
            break
        except ValueError:
            print("Antall ladere må være et heltall. Prøv igjen.")

    chargestation_template_ids = ['apcoa-onboarding-1-phase_apcoa', 'apcoa-onboarding-3-phase_apcoa',
                                  'apcoa-onboarding-3-phase-dual_apcoa_apcoa',
                                  'apcoa-onboarding-ac-1-phase-v2_apcoa', 'apcoa-onboarding-apcoauk_apcoa',
                                  'ctek-dual-charger_apcoa', '	de-alfen-eve-single-pro-line_apcoa',
                                  'hunderfossen-ac-pro_apcoa']
    chargestation_template_id = input(f"Skriv inn Chargestation Template id or Enter for list of ids: ")  #Eksempel: apcoa-onboarding-1-phase_apcoa / apcoa-onboarding-3-phase_apcoa
    while chargestation_template_id not in chargestation_template_ids:
        print(f'Accepted template ids are the following: {chargestation_template_ids}')
        chargestation_template_id = input(f"Skriv inn Chargestation Template id: ")
    tariff_code = input(f"Skriv inn tariff kode, Enter for Default (A0-NOK): ") or "A0-NOK"

    charger_type = input(
        "Type environment (Public/Restricted) Enter for Public:") or "Public"
    while charger_type.lower() not in ("public", "restricted"):
        print('charger_type only supports input of "Public" or "Restricted".')
        charger_type = input("Type environment (Public/Restricted):")
    charger_type_capitalized = charger_type.capitalize()

    location_name = input(f"Skriv inn avdelingsnavnet: ") #TODO Stor forbokstav på hvert ord!!!!
    location_name_capitalized = location_name.capitalize()
    street = input(f"Skriv inn adresse på avdeling: ") #TODO Stor forbokstav på hvert ord!!!!!
    street_capitalized = street.capitalize()
    zipcode = input(f"Skriv inn postnummeret: ") #TODO Kun tall
    city = input(f"Skriv inn hvilken by: ") #Skriv byen med stor forbokstav
    city_capitalized = city.capitalize()
    country_code3 = input(f"Skriv inn landskoden eller trykk enter for NOR: ") or "NOR" #Eksempel: NOR/SVE osv

    if charger_type.lower() == "public":
       is_public = "TRUE"
       is_restricted = "FALSE"
    elif charger_type.lower() == "restricted":
       is_public = "FALSE"
       is_restricted = "TRUE"




    with (open('ladere_sno_phus.csv', 'w', newline='') as csvfile):
        fieldnames = [ 'ChargeStationID', 'ChargeStationTemplateID', 'TariffCode','ReimbursementTariffCode','ChargeStationName','Floor','ChargeStationDirections','DeployState','InstallationDate','ContactlessType','ContactlessTerminalSerialNumber',
                       'ContactlessTerminalAuthAmount','ChargeStationAuthList','TapToStop','ChargerType', 'MaintenanceInfo','Remarks','LocationName','HouseNumber','Street','ZipCode','City','CountryCode3','Addressline2','Facilities',
                       'Latitude','Longitude','TimeZone', 'IsPublic','IsRestricted','LocationDirections','AuthList','EnergyMixProfileId' 'LocationType', 'PaymentProvider', 'WalletId']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()




        for i in range(1, amount + 1):
            current_chargestation_id = f"{chargestation_id}{i}"
            writer.writerow({

        'ChargeStationID' : current_chargestation_id,
        'ChargeStationTemplateID' : chargestation_template_id,
        'TariffCode' : tariff_code,
        'ChargerType' : charger_type_capitalized,
        'LocationName' : location_name_capitalized,
        'Street' : street_capitalized,
        'ZipCode' : zipcode,
        'City' : city_capitalized,
        'CountryCode3' : country_code3,
        'IsPublic' : is_public,
        'IsRestricted' : is_restricted,
            })

        print(csvfile)


if __name__ == '__main__':
    csv_generator()

    #TODO DOBBELTSJEKK OM CSV FILEN ER HELT RIKTIG, OG ÅPNE DEN I EXCEL -> DATA -> "FRA TEKST/CSV"!!!!