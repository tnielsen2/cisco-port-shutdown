# Cisco-Port-Shutdown
Python Script used to shutdown physical access ports of Cisco IOS/IOS-XE devices with an downtime of 60 days or greater. If device has an utpime of less than 60 days, skip port evaluation. Script will ask for credentials and then use the netmiko ssh connect handler to connect to devices specified in hosts file.


Written in Python 3.5

# Libraries

re

sys

time

datetime

netmiko (fork of paramiko)

# Syntax

port-shutdown.py #hosts #output #summary

#hosts = text file with IP addresses, one per line to connect to and run port evaluation against

#output = output text file with all logged activity

#summary = output text file will sumnmary of all actions performed


