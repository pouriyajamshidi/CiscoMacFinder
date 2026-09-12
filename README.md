# Cisco MAC Address Finder

This cross-platform Python script helps you find a MAC address on your Cisco switches or any other vendor that has a similar MAC table format as Cisco.

Use the included ```YAML``` file to [define](#usage) different data centers, floors, etc. so that the program stops looking inside other data centers or floors upon finding a MAC address. **There is no limit on the number of sites or devices that you define, everything will be handled dynamically**.

Switches within a site are queried in parallel, so a site of fifty devices takes about as long as its slowest switch.

For your convenience, it [takes](#run-it-like) a MAC address in any notation (```Linux```, ```Windows```, ```Cisco```) and automatically converts it to Cisco format.

## Requirements

Python 3.13 or newer, plus ```Netmiko``` and ```PyYAML```. You can install the latter two using below command.

```bash
pip3 install -r requirements.txt
```

## Usage

For starters, you need to populate the ```YAML``` file with your switch names, their corresponding IP addresses and ports like below example:

```yaml
France-DC:
  - name: FR-SW-TOR-R1-Rack1
    mgmt_ip: 172.16.16.1
    port: 22
  - name: FR-SW-TOR-R2-Rack2
    mgmt_ip: 172.16.16.2
    port: 22
Germany-DC:
  - name: DE-SW-TOR-R1-Rack1
    mgmt_ip: 172.18.18.1
    port: 222
  - name: DE-SW-TOR-R2-Rack2
    mgmt_ip: 172.18.18.2
    port: 222

```

```port``` is optional and defaults to ```22```.

Make the script executable:

```bash
chmod +x CiscoMacFinder.py
```

### Run it like

```python
./CiscoMacFinder.py <MAC Address>
```

For example:

```python
./CiscoMacFinder.py 8041.a473.453b

OR

./CiscoMacFinder.py 80:41:a4:73:45:3b

OR

./CiscoMacFinder.py 80-41-a4-73-45-3b
```

OR

```python
python3 CiscoMacFinder.py <MAC Address>
```

### Options

```text
-s, --switches   path to the YAML file (default: switches.yml)
-u, --username   login username (default: the CISCO_USERNAME environment variable)
-w, --workers    switches polled in parallel (default: 10)
```

You are prompted for the username and password unless they are supplied through ```--username``` and the ```CISCO_USERNAME``` / ```CISCO_PASSWORD``` environment variables:

```bash
./CiscoMacFinder.py 8041.a473.453b --switches ~/lab/switches.yml --workers 25
```

Lower ```--workers``` if your TACACS or RADIUS server rate-limits simultaneous authentications.

### Exit codes

```text
0   MAC address found
1   MAC address not found
2   invalid MAC address, or the YAML file is missing or malformed
```

## Tested on

IOS and IOS-XE.

## Contributing

Pull requests are welcome.

## License

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
