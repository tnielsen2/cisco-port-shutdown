# Cisco-Port-Shutdown

This script was written to solve the problem of open ports being left administratively up after a device is disconnected. If you do not have 802.1X for your wired endpoints, this is a (less) effective way to control users plugging in devices to attempt to gain access. The script will leave the port in an up state, but will put a dummy mac address on the port and enable port security. err-disable port recovery for security violations will also be enabled on the switch to generate traps (if logging is set up correctly). When a port violation occurs, a syslog/snmp trap is generated to the syslog/snmp server configured on the device. This gives the network administrator visibility to see who is connecting to a disabled port. 

This python script used to disable physical access ports of Cisco IOS/IOS-XE devices with an downtime of 60 days or greater. If device has an utpime of less than 60 days, port evaluation is skipped. The script will ask for credentials and then use the netmiko ssh connect handler to connect to devices specified in hosts file.

If your environment can alert based upon syslog traps, you will be notified if a device connects to a disabled port via err-disable security violation. 




Written in Python 3.5

# Libraries

re

sys

time

datetime

netmiko (fork of paramiko)

getpass

# Syntax

port-shutdown.py #hosts #output #summary

#hosts = text file with IP addresses, one per line to connect to and run port evaluation against

#output = output text file with all logged activity

#summary = output text file will sumnmary of all actions performed


