#Ejercicio previo: hacer unclaim de APs de alguna network...

##### No Modificar #####
import meraki
import random
import sys
import login

API_KEY = login.api_key
dashboard = meraki.DashboardAPI(API_KEY)
orgs = dashboard.organizations.getOrganizations()

##### No Modificar #####


#########################
##### EDITAR #####
nombre_organizacion='Cisco_Peru'
##### EDITAR #####
#########################

org_names = [org['name'] for org in orgs]
index = org_names.index(nombre_organizacion)
my_org = orgs[index]['id']

print("La organizacion '{0}' tiene un ID: {1}",nombre_organizacion,my_org)


# 1. Crear una Network

#########################
##### EDITAR #####
my_name = 'Draft'
my_tags = ['Tag1', 'Tag2', 'Tag3']
my_time = 'America/Lima'
##### EDITAR #####
#########################

# Obtener listado de networks y sus nombres
current_networks = dashboard.organizations.getOrganizationNetworks(my_org)
network_names = [network['name'] for network in current_networks]

# Proceso de validación
if my_name == 'Draft':
    sys.exit('⚠️ Parte 1: Editar el nombre de la red...\n')
elif my_tags == '':
    sys.exit(('⚠️ Parte 1: Agregar algunos tags...s\n'))
elif my_name in network_names:
    my_netid = current_networks[network_names.index(my_name)]['id']
    print('✅ Parte 1: La network {0} ya existe, con un ID: {1}\n'.format(my_name, my_netid))
# Añadir la network
else:
    # Call to create a newtork
    my_network = dashboard.organizations.createOrganizationNetwork(
    my_org, my_name, ["appliance", "wireless"],
    tags=my_tags, 
    timeZone=my_time, 
    )

    my_netid = my_network['id']
    print('✅ Parte 1: Creada la network {0} con network ID {1}\n'.format(my_name, my_netid))






# 2. Retornar el inventario de la organización

#########################
##### EDITAR #####
# Hace una llamada para retornar el inventario de la organización. 
try:
    inventory = dashboard.organizations.getOrganizationInventoryDevices()
except Exception as e:
    sys.exit(f"❌ Parte 2: Error en el request: {e}")

##### EDITAR #####
#########################


# Filtrar y mostrar solo los dispositivos sin utilizar...
unused = [device for device in inventory if device['networkId'] is None]
print('✅ Parte 2: Se encontró un total de {0} dispositivos no utilizados en networks\n'.format(len(unused)))



# 3. Realizar el claim de un dispositivo en la Network

# Ver si la red ya tiene un dispositivo
network_devices = dashboard.networks.getNetworkDevices(my_netid)
if len(network_devices) == 0:
    # Buscar un AP dentro de dispositivos sin utilizar.
    for my_ap in unused:
        if my_ap['model'].startswith(('CW', 'MR')):
            print(f"Parte 3: Se encontró un AP {my_ap['model']} sin utilizar, con serial number: {my_ap['serial']}\n")

    # #########################
    # ##### EDITAR #####
    my_serial = "ABCD-EFGH-IJKL"
    # ###### EDITAR ######
    # #########################

    # Hacer Claim al device en la Network
    try:
        dashboard.networks.claimNetworkDevices(my_netid, serials=[my_serial])
    except meraki.APIError as e:
        sys.exit(f"❌ Parte 3: Error en el claim: {e}")

    # Confirmar que el device está en la Network
    network_devices_after = dashboard.networks.getNetworkDevices(my_netid)
    if not any(dev['serial'] == my_serial for dev in network_devices_after):
        sys.exit('❌ Parte 3: AP no hizo claim correctamente\n')
    else:
        print(f'✅ Parte 3: Se añadió el AP {my_serial} en la network: {my_name} \n')

else:
    my_ap = network_devices[0]
    my_serial = my_ap['serial']
    print(f'✅ Parte 3: AP {my_serial} ya se encuentra en la network: {my_name}\n')


# 4. Actualizar los atributos de un dispositivo

# #########################
# ##### EDITAR #####
my_address = 'Edificio Real Uno, Piso 13, Victor Andres Belaunde 147, Vía Principal 123, San Isidro 15073'
# ###### EDITAR ######
# #########################

# Validar
if my_address == 'Edificio Real Uno, Piso 13, Victor Andres Belaunde 147, Vía Principal 123, San Isidro 15073' or my_address == '':
    sys.exit('❌ Parte 4: Address no ha sido modificado\n')

else:
    # #########################
    # ##### EDITAR #####
    # Hacer un update de los atributos del AP - Agregar parámetros necesarios
    try:
        dashboard.devices.updateDevice(moveMapMarker=True)
    except Exception as e:
        sys.exit(f"❌ Parte 4: Error: {e}")
    # ###### EDITAR ######
    # #########################


    # === Verificación de cambios aplicados ===
    try:
        device_detail = dashboard.devices.getDevice(my_serial)
    except Exception as e:
        sys.exit(f"Parte 4: No se pudo obtener detalles del dispositivo: {e}\n")

    # Validar tags
    device_tags = device_detail.get('tags', [])

    if device_detail.get('name') != my_name:
        sys.exit('❌ Parte 4: el nombre del dispositivo no fue actualizado\n')
    elif set(device_tags) != set(my_tags):
        sys.exit('❌ Parte 4: los tags del dispositivo no fueron actualizados\n')
    elif device_detail.get('address') != my_address:
        sys.exit('❌ Parte 4: la dirección del dispositivo no fue actualizada\n')
    else:
        print(f"✅ Parte 4: Se actualizó el AP {my_serial} con dirección: {my_address}\n")



# === 5. Actualizar los atributos de un SSID ===
my_ssid_name = ''
my_ssid_psk = ''

# Validación inicial
if my_ssid_name.strip() == '' or my_ssid_psk.strip() == '':
    sys.exit('❌ Parte 5: Editar nombre SSID y PSK...\n')

# === Actualizar SSID en la posición 0 ===
try:
    dashboard.wireless.updateNetworkWirelessSsid(
        encryptionMode="wpa",
        wpaEncryptionMode= "WPA2 only",
        enabled=True,
        authMode='psk'
    )
except Exception as e:
    sys.exit(f"❌ Part 5: Error al actualizar el SSID: {e}\n")

# === Verificación de que se aplicaron los cambios ===
try:
    ssids = dashboard.wireless.getNetworkWirelessSsids(my_netid)
except Exception as e:
    sys.exit(f"❌ Part 5: Error al obtener los SSIDs: {e}\n")

ssid_0 = ssids[0] if len(ssids) > 0 else {}

if ssid_0.get('name') != my_ssid_name:
    sys.exit('❌ Parte 5: El nombre del SSID en el primer slot no fue actualizado correctamente\n')
elif my_ssid_name not in [ssid.get('name') for ssid in ssids]:
    sys.exit('❌ Parte 5: SSID no fue encontrado en la lista de SSIDs\n')
elif ssid_0.get('psk') != my_ssid_psk:
    sys.exit('❌ Parte 5: PSK del SSID no fue actualizado\n')
elif not ssid_0.get('enabled', False):
    sys.exit('❌ Parte 5: SSID no fue habilitado\n')
else:
    print(f"✅ Parte 5: Se actualizó la red {my_name} con el SSID '{my_ssid_name}' en la posición 0\n")

print('🎉 Has completado exitosamente el laboratorio de la API de Meraki en Python. ¡Felicitaciones!\n')



