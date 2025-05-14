#!/usr/bin/python3

import csv
import datetime
import meraki
import sys
import requests

def get_network_name(network_id, networks):
    return next((network['name'] for network in networks if network['id'] == network_id), 'Unknown Network')

if __name__ == '__main__':
    # Import API key and org ID from login.py
    try:
        import login
        API_KEY, ORG_ID = login.api_key, login.org_id
    except ImportError:
        API_KEY = input('Enter your Dashboard API key: ')
        ORG_ID = input('Enter your organization ID: ')

    dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)

    try:
        org = dashboard.organizations.getOrganization(ORG_ID)
        org_name = org['name']
    except meraki.APIError:
        sys.exit('Incorrect API key or org ID, as no valid data returned')

    networks = dashboard.organizations.getOrganizationNetworks(ORG_ID)
    inventory = dashboard.organizations.getOrganizationInventoryDevices(ORG_ID)

    appliances = [device for device in inventory if device['model'][:2] in ('MX', 'Z1', 'Z3', 'vM') and device['networkId']]
    appliance_serials = [device['serial'] for device in appliances]

    # Obtener todos los estados de uplinks con una sola llamada
    try:
        uplink_statuses = dashboard.appliance.getOrganizationApplianceUplinkStatuses(
            ORG_ID, serials=appliance_serials, total_pages='all'
        )
        uplink_by_serial = {entry['serial']: entry for entry in uplink_statuses}
    except meraki.APIError as e:
        print(f"[ERROR] Could not fetch uplink statuses: {e}")
        uplink_by_serial = {}

    today = datetime.date.today()
    csv_filename = f"{org_name} appliances -{today}.csv"

    with open(csv_filename, 'w', encoding='utf-8', newline='') as csv_file:
        fieldnames = [
            'Network', 'Device', 'Serial', 'MAC', 'Model',
            'WAN1 Status', 'WAN1 IP', 'WAN1 Gateway', 'WAN1 Public IP', 'WAN1 DNS', 'WAN1 Static',
            'WAN2 Status', 'WAN2 IP', 'WAN2 Gateway', 'WAN2 Public IP', 'WAN2 DNS', 'WAN2 Static',
            'Cellular Status', 'Cellular IP', 'Cellular Provider', 'Cellular Public IP', 'Cellular Model', 'Cellular Connection',
            'Performance'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, restval='')
        writer.writeheader()

        for appliance in appliances:
            network_id = appliance['networkId']
            serial = appliance['serial']
            network_name = get_network_name(network_id, networks)
            print(f"Looking into network {network_name}")

            # Obtener nombre del dispositivo (fallback manual vía requests)
            try:
                url = f"https://api.meraki.com/api/v1/networks/{network_id}/devices/{serial}"
                headers = {
                    "X-Cisco-Meraki-API-Key": API_KEY,
                    "Content-Type": "application/json"
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    device_details = response.json()
                    device_name = device_details.get('name', serial)
                else:
                    print(f"[ERROR] Could not retrieve device {serial} (status {response.status_code})")
                    device_name = serial
            except Exception as e:
                print(f"[ERROR] Exception while retrieving device details: {e}")
                device_name = serial

            # Obtener performance score
            try:
                perf = dashboard.appliance.getDeviceAppliancePerformance(serial)
                perfscore = perf.get('perfScore')
            except meraki.APIError as e:
                print(f"[WARN] No performance data for {serial}: {e}")
                perfscore = None

            # Obtener uplinks desde el dict agrupado
            uplinks_info = {'WAN1': {}, 'WAN2': {}, 'Cellular': {}}
            uplink_entry = uplink_by_serial.get(serial)

            if uplink_entry:
                for uplink in uplink_entry.get('uplinks', []):
                    iface = uplink['interface'].replace(' ', '').upper()
                    uplinks_info[iface] = {
                        'status': uplink.get('status'),
                        'ip': uplink.get('ip'),
                        'gateway': uplink.get('gateway'),
                        'publicIp': uplink.get('publicIp'),
                        'dns': uplink.get('primaryDns'),
                        'usingStaticIp': uplink.get('ipAssignedBy') == 'static'
                    }

            row = {
                'Network': network_name,
                'Device': device_name,
                'Serial': serial,
                'MAC': appliance['mac'],
                'Model': appliance['model'],

                'WAN1 Status': uplinks_info['WAN1'].get('status'),
                'WAN1 IP': uplinks_info['WAN1'].get('ip'),
                'WAN1 Gateway': uplinks_info['WAN1'].get('gateway'),
                'WAN1 Public IP': uplinks_info['WAN1'].get('publicIp'),
                'WAN1 DNS': uplinks_info['WAN1'].get('dns'),
                'WAN1 Static': uplinks_info['WAN1'].get('usingStaticIp'),

                'WAN2 Status': uplinks_info['WAN2'].get('status'),
                'WAN2 IP': uplinks_info['WAN2'].get('ip'),
                'WAN2 Gateway': uplinks_info['WAN2'].get('gateway'),
                'WAN2 Public IP': uplinks_info['WAN2'].get('publicIp'),
                'WAN2 DNS': uplinks_info['WAN2'].get('dns'),
                'WAN2 Static': uplinks_info['WAN2'].get('usingStaticIp'),

                'Cellular Status': uplinks_info['Cellular'].get('status'),
                'Cellular IP': uplinks_info['Cellular'].get('ip'),
                'Cellular Provider': uplinks_info['Cellular'].get('provider'),
                'Cellular Public IP': uplinks_info['Cellular'].get('publicIp'),
                'Cellular Model': uplinks_info['Cellular'].get('model'),
                'Cellular Connection': uplinks_info['Cellular'].get('connectionType'),

                'Performance': perfscore
            }

            writer.writerow(row)

    print(f"\n✅ CSV export complete: {csv_filename}")


    # === Output CSV for all other devices using new API ===
    try:
        statuses = dashboard.organizations.getOrganizationDevicesStatuses(
            ORG_ID,
            total_pages='all'
        )
    except meraki.APIError as e:
        print(f"[ERROR] Could not fetch device statuses: {e}")
        statuses = []

    # Filtrar solo dispositivos que NO sean appliance (MX, Z1, Z3, vMX)
    other_devices_status = [
        dev for dev in statuses
        if dev.get('productType') != 'appliance' and dev.get('networkId') is not None
    ]

    csv_filename2 = f"{org_name} other devices -{today}.csv"
    with open(csv_filename2, 'w', encoding='utf-8', newline='') as csv_file2:
        fieldnames2 = [
            'Network', 'Device', 'Serial', 'MAC', 'Model',
            'Status', 'IP', 'Gateway', 'Public IP', 'DNS', 'VLAN', 'Static'
        ]
        writer2 = csv.DictWriter(csv_file2, fieldnames=fieldnames2, restval='')
        writer2.writeheader()

        for dev in other_devices_status:
            network_id = dev.get('networkId')
            serial = dev.get('serial')
            network_name = get_network_name(network_id, networks)

            row = {
                'Network': network_name,
                'Device': dev.get('name', serial),
                'Serial': serial,
                'MAC': dev.get('mac'),
                'Model': dev.get('model'),
                'Status': dev.get('status'),
                'IP': dev.get('lanIp'),
                'Gateway': dev.get('gateway'),
                'Public IP': dev.get('publicIp'),
                'DNS': dev.get('primaryDns'),
                'VLAN': '',  # No disponible en este endpoint
                'Static': dev.get('ipType') == 'static'
            }

            writer2.writerow(row)

    print(f"\n✅ CSV export complete: {csv_filename2}")
