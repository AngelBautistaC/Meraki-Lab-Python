# API Python module @ https://github.com/meraki/dashboard-api-python/blob/master/meraki.py


#Ejercicio previo: hacer unclaim de APs de alguna network...

##### DO NOT MODIFY #####
import meraki
import random
import sys
import login

API_KEY = login.api_key
dashboard = meraki.DashboardAPI(API_KEY)


orgs = dashboard.organizations.getOrganizations()



nombre_organizacion='Cisco_Peru'
org_names = [org['name'] for org in orgs]
index = org_names.index(nombre_organizacion)
my_org = orgs[index]['id']
##### DO NOT MODIFY #####
print(my_org)


# 1. Create a network

#########################
##### START EDITING #####
my_name = 'Borrador'
my_tags = ['Tag1', 'Tag2', 'Tag3']
my_time = 'America/Lima'
###### END EDITING ######
#########################

# Get the current list of networks
current_networks = dashboard.organizations.getOrganizationNetworks(my_org)

# Get the current networks' names
network_names = [network['name'] for network in current_networks]

# Was my_name changed from default 'First Last'?
if my_name == 'First Last':
    sys.exit('Part 1: please edit your name\n')
# Have tags been added?
elif my_tags == '':
    sys.exit(('Part 1: please add some tags\n'))
# Does the network already exist?
elif my_name in network_names:
    my_netid = current_networks[network_names.index(my_name)]['id']
    print('Part 1: the network {0} already exists with ID {1}\n'.format(my_name, my_netid))
# Add the new network
else:
    # Call to create a newtork
    my_network = dashboard.organizations.createOrganizationNetwork(
    my_org, my_name, ["appliance", "wireless"],
    tags=my_tags, 
    timeZone=my_time, 
    )

    my_netid = my_network['id']
    print('Part 1: created network {0} with network ID {1}\n'.format(my_name, my_netid))






# 2. Return the inventory for an organization

#########################
##### START EDITING #####
# Hace una llamada para retornar el inventario de la organización. Investigar los argumentos que toma

inventory = dashboard.organizations.getOrganizationInventoryDevices(organizationId=my_org)

###### END EDITING ######
#########################

# Filtrar y mostrar solo los dispositivos sin utilizar...
unused = [device for device in inventory if device['networkId'] is None]
print('Ejercicio 2: found total of {0} unused devices in inventory\n'.format(len(unused)))





# 3. Claim a device into a network

# Check if network already contains devices

network_devices = dashboard.networks.getNetworkDevices(my_netid)



if len(network_devices) == 0:
    # Buscar un AP dentro de dispositivos sin utilizar.
    for my_ap in unused:
        if my_ap['model'].startswith(('CW', 'MR')):
            print(f"Ejercicio 3: Se encontró un AP {my_ap['model']} sin utilizar, con serial number: {my_ap['serial']}\n")

    # #########################
    # ##### START EDITING #####
    my_serial = "ABCD-EFGH-IJKL"
   
    # ###### END EDITING ######
    # #########################

    # Claim the device into the network
    try:
        dashboard.networks.claimNetworkDevices(my_netid, serials=[my_serial])
    except meraki.APIError as e:
        sys.exit(f"[ERROR] Claim failed: {e}")

    # Confirm device is now part of the network
    network_devices_after = dashboard.networks.getNetworkDevices(my_netid)
    if not any(dev['serial'] == my_serial for dev in network_devices_after):
        sys.exit('Part 3: AP no hizo claim correctamente\n')
    else:
        print(f'Part 3: Se añadió el AP {my_serial} en la network: {my_name} \n')

else:
    my_ap = network_devices[0]
    my_serial = my_ap['serial']
    print(f'Part 3: AP {my_serial} ya se encuentra en la network: {my_name}\n')


# # 4. Update the attributes of a device

# #########################
# ##### START EDITING #####
# my_address = 'Cisco Peru'
# ###### END EDITING ######
# #########################

# # Check if address changed from default
# if my_address == '500 Terry A. Francois Blvd, San Francisco, CA 94158' or my_address == '':
#     sys.exit('Part 4: change your address to your favorite vacation spot (not 500TF)!\n')

# #########################
# ##### START EDITING #####
# # Call to update the attributes of a device
# # Only change this one line below
# meraki.updatedevice(my_key, move='true')
# ###### END EDITING ######
# #########################

# # Check if all attributes were updated and marked moved
# device_detail = meraki.getdevicedetail(my_key, my_netid, my_serial)
# try:
#     device_tags = device_detail['tags'].strip()
# except:
#     sys.exit('Part 4: no tags were applied to the device\n')
# if device_detail['name'] != my_name:
#     sys.exit('Part 4: the name of the device was not changed\n')
# elif set(device_tags.split()) != set(my_tags):
#     sys.exit('Part 4: the tags of the device were not changed\n')
# elif device_detail['address'] != my_address:
#     sys.exit('Part 4: the address of the device was not changed\n')
# elif device_detail['lat'] == 37.4180951010362 and device_detail['lng'] == -122.098531723022:
#     sys.exit('Part 4: the marker for the address was not moved\n')
# else:
#     print('Part 4: updated address of AP {0} to {1}\n'.format(my_serial, my_address))



# # 5. Update the attributes of an SSID

# #########################
# ##### START EDITING #####
# my_ssid_name = ''
# my_ssid_psk = ''
# ###### END EDITING ######
# #########################

# # Check if defaults have been changed
# if my_ssid_name == '' or my_ssid_psk == '':
#     sys.exit('Part 5: please edit your SSID name and PSK\n')

# #########################
# ##### START EDITING #####
# # Call to update the attributes of an SSID
# # Only add one line here to call the function

# ###### END EDITING ######
# #########################

# # Check if SSID was updated correctly
# ssids = meraki.getssids(my_key, my_netid)
# if ssids[0]['name'] != my_ssid_name:
#     sys.exit('Part 5: SSID in the first slot not successfully updated\n')
# elif my_ssid_name not in [ssid['name'] for ssid in ssids]:
#     sys.exit('Part 5: SSID not successfully updated\n')
# elif ssids[0]['psk'] != my_ssid_psk:
#     sys.exit('Part 5: SSID not successfully updated\n')
# elif ssids[0]['enabled'] != True:
#     sys.exit('Part 5: SSID not enabled\n')
# else:
#     print('Part 5: updated the network {0} with SSID {1} in the first slot\n'.format(my_name, my_ssid_name))

# print('You have successfully completed the Dashboard API Python lab. Congratulations!!\n')



# # BONUS. Update the attributes of an SSID

# #########################
# ##### START EDITING #####
# # Call to update the attributes of all other SSIDs
# # Edit the two lines and only two lines here
# for x in range(0):
#     # Remove pass, and fill in the blank by calling a function
#     pass
# ###### END EDITING ######
# #########################

# # Check if all other SSIDs were updated correctly
# ssids = meraki.getssids(my_key, my_netid)
# for name in [ssid['name'] for ssid in ssids]:
#     if 'Unconfigured' in name:
#         sys.exit('Bonus: not all SSIDs updated yet\n')
#     else:
#         pass
# print('You have completed the bonus question. Awesome!!\n')
