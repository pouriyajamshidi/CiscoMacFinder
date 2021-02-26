# Cisco MAC Address Finder

This cross-platform Python script helps you find a MAC address on your Cisco switches or any other vendor that has a similar MAC table format as Cisco.

Use the included ```YAML``` file to [define](#usage) different data centers, floors, etc. so that the program stops looking inside other data centers or floors upon finding a MAC address. **There is no limit on the number of sites or devices that you define, everything will be handled dynamically**.

For your convenience, it [takes](#run-it-like) a MAC address in any notation (```Linux```, ```Windows```, ```Cisco```) and automatically converts it to Cisco format.

## Requirements

```Netmiko``` and ```PyYAML``` are required to run this script. You can install them using below command.

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

For example:

```python
python3 CiscoMacFinder.py 8041.a473.453b

OR

python3 CiscoMacFinder.py 80:41:a4:73:45:3b

OR

python3 CiscoMacFinder.py 80-41-a4-73-45-3b

```

## Tested on

IOS and IOS-XE.

## Contributing

Pull requests are welcome.

## License

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

