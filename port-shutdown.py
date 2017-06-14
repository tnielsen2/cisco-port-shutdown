import re	
import sys
import time
import datetime
from netmiko import ConnectHandler




import getpass



if len(sys.argv) == 4:
	hostfile = sys.argv[1]
	outfile = sys.argv[2]
	statsfile = sys.argv[3]
	
elif len(sys.argv) == 1:
	sys.exit("Usage: {} <input file> <output file> <stats file>".format(sys.argv[0]))	

elif len(sys.argv) < 4:
	print ("Not enough arguments")
	sys.exit()

elif len(sys.argv) > 4:
	print ("Too many arguments")
	sys.exit()


import getpass
username = input("Username: ")
password = getpass.getpass()

#Open a file for reading
input = open(hostfile, 'r+')

#Open a file for writing
output = open(outfile,'a')	
	
#Open a statistics file
stats = open(statsfile,'a')

#Open a file for errors
errors = open('script-errors.txt','a')	

#sys.stderr = errors	

#Set debug level
debug = False


#Declare some counters


totaldevices = 0
skippedswitches_ssh = 0
skippedswitches_days = 0
skippedswitches_noint = 0
skippedswitches_other = 0
totalinterfaces = 0
skippedinterfaces_psec = 0
skippedinterfaces_days = 0
modifiedinterfaces = 0




#Timestamp this when it starts
scriptstart = datetime.datetime.now().time()





def uglyshowrundict(session):
	###########SANDBOX################
		
	show_run_1 = re.sub("\n ","--->",session.send_command('show run'))
	
	show_run_2 = show_run_1.split("\n")
	
	show_run_3 = (grab_pattern(show_run_2,"^interface ([A-Z][a-z])[A-Za-z]+(\d.*?)(--->.*)"))

	show_run_4 = []

	for element in show_run_3:
		
		pass1 = (re.sub(r'^(..) (.*?) (--->)',r'\1\2tupplator',element))
		
		pass2 = (re.sub("--->","\n",pass1))
		
		show_run_4.append(pass2)

	d = dict(s.split('tupplator') for s in show_run_4)
	
	return (d)


	###########SANDBOX################




def ugliershowdtp(session):
	###########SANDBOX################
		
	show_dtp_1 = re.sub("DTP information for ","<split1><split2>",session.send_command('show dtp interface'))
	
	#print (repr(show_dtp_1))
	
	#DTP information for FastEthernet1/0/21
	
	show_dtp_2 = show_dtp_1.split("<split1>")
	
	pretuple = []
	
	for element in show_dtp_2:
	
		lookforstuff = grab_pattern("{}".format(repr(element)),"<split2>([A-Z][a-z])\w+(\d.*?):.*?(last link down on .*)")
		
		if lookforstuff is not None:
			
			pass1 = (re.sub(r'^(..) (.*?) (last link down on .*)',r'\1\2tupplator\3',lookforstuff))
			
			pretuple.append(pass1)
			
	d = dict(s.split('tupplator') for s in pretuple)
	
	return (d)
	
	###########SANDBOX################




#Test given object, return __class__ value of that object
def whatisthis(object):
	
	return (re.search("<class '(.*?)'>","{}".format(object.__class__)).group(1))



		
		


#Print STDOUT and to a file at the same time. 
def customPrint(object):
		
	if whatisthis(object) == 'str':
		
		print (object)
			
		print (object,file=output)

	elif whatisthis(object) == 'tuple':
		
		(string,debugtest) = object
			
		if debug == True and debugtest == True:
			
			print ("START:","*" * 58,"\n", string,"\n", "END:" , "*" * 60,"\n")
			
			print ("START:","*" * 58,"\n", string,"END:" , "*" * 60,"\n",file=output)

			
#Return 0 if string is None, otherwise return int(string)
def intsrsly(string):
	
	customPrint(("function 'intsrsly' invoked with:\n{}".format(string),debug))
		
	if string == None:
		return 0
	else:
		return int(string)	


			
#Given (string,regex) or (list,regex) will return a string of the match or a list of the matches
def grab_pattern(object,regex):
			
	if whatisthis(object) == "str":
		
		customPrint(("function 'grab_pattern' invoked with string:\n{}\nand pattern:\n{}".format(object,regex),debug))
			
		results = re.search(re.compile(regex),object)
			
		return (" ".join(results.groups())) if (results is not None) else None
		
	else:
		
		results = []
			
		customPrint(("function 'grab_pattern' invoked with list:\n{}\n\n-----> and pattern:\n{}\n".format('\n'.join(object),regex),debug))
			
		for result in object:
			
			hasmatch = re.search(re.compile(regex),result)

			if hasmatch is not None:
				
				results.append(" ".join(hasmatch.groups()))
					
		return results

		
		
		
#datetime pattern and associated regex for "show clock" output
tuple_clock = ("%H:%M:%S %b %d %Y","[\.\*]?(\d\d:\d\d:\d\d).*?(\w+ \d+ \d+)")

#datetime pattern and associated regex for "show interface dtp" output
tuple_dtp = ("%b %d %Y, %H:%M:%S","(\w+ \d+ \d+, \d+:\d+:\d+)")
	
#Convert given timestamp into unix epoch time and work out days since Jan 1, 1970
def getunixdays(string,tuple):
		
	format,regex = tuple
		
	formatted = grab_pattern(string,regex)
	
	if formatted is not '0' and formatted is not None:
	
		return int(int(time.mktime(datetime.datetime.strptime(formatted,format).timetuple())) / 86400)
			
	else:
			
		return None
	
			
			
			

#Given the line of show version which includes uptime, calculate in days
def howmanydays(uptime):

	device_days_up = (
		
		(intsrsly(grab_pattern(uptime,"(\d+) year")) * 365) +
		
		(intsrsly(grab_pattern(uptime,"(\d+) week")) * 7) +
		
		(intsrsly(grab_pattern(uptime,"(\d+) day")) * 1)
		
		) 
		
	return(device_days_up)


	
def test_device(session,ipaddress):

	global skippedswitches_other
	
	global skippedswitches_days
	
	customPrint ("{}:  Beginning device test".format(ipaddress))
	
	show_version = session.send_command('show version | include uptime')
		
	try:
		
		uptime = grab_pattern(show_version,"uptime is (.*)$")
		device_days_up = intsrsly(howmanydays(uptime))
	
	except:
		
		skippedswitches_other += 1
	
		return (False,"{}:   Cannot determine device uptime".format(ipaddress),"","")	

	if device_days_up < 60:
		
		
		skippedswitches_days += 1
	
		return(False,"{}:   Device up only {} days.  Skipping.".format(ipaddress,device_days_up),"","")
		
	customPrint("{}:   Device has been up {} days.".format(ipaddress,device_days_up))
	
	try:
	
		show_clock = session.send_command('show clock')
		device_unixdays = getunixdays(show_clock,tuple_clock)
		
		if device_unixdays is None:
			return(False,"{}:   Cannot determine device's current time".format(ipaddress),"","")
	
	except:
	
		return(False,"{}:   Cannot determine device's current time".format(ipaddress),"","")
	
	return (True,"no reason",device_days_up,device_unixdays)
	
	
def get_initial_list(session):
	
	show_int_status = (session.send_command('show int status')).splitlines()
		
	outputlines = grab_pattern(show_int_status,"^([FG].*?)\s.*?notconnect\s+\d.*?BaseT")
	
	if outputlines is not None:
	
		return (outputlines)
			
	else:
			
		return None
			
def portsec_test(inputlist,session,ipaddress):

	global skippedinterfaces_psec
	global totalinterfaces
			
	customPrint ("{}:   starting port-security test".format(ipaddress))
		
	#if session.send_command('show run | inc switchport port-security') == "":
	#
	#	customPrint ("{}:   'port-security' does not appear in config".format(ipaddress))
	#	customPrint ("{}:   Skipping port-security check".format(ipaddress))
	#
	#	return (inputlist)
	
	outputlist = []
	d = uglyshowrundict(session)

	for interface in inputlist:
	
		
		totalinterfaces += 1
	
		try:
		
			#show_run_int = session.send_command('show run interface {}'.format(interface))
			show_run_int = 	d[interface]
			#print (show_run_int)
		
			#print (repr(show_run_int))
		
			test1 = grab_pattern(show_run_int,"(switchport port-security)\n")
		
			test2 = grab_pattern(show_run_int,"(switchport port-security mac)")
		
			if test1 is not None and test2 is not None:
		
				customPrint("{}:   {} port-sec already applied".format(ipaddress,interface))
				
				skippedinterfaces_psec += 1
			
			else:
				
				outputlist.append(interface)
		
		except:
		
			outputlist.append(interface)
			
	return (outputlist)			
			
def daysdown_test(inputlist,device_days_up,device_unixdays,session,ipaddress):

	global skippedinterfaces_days
	
	customPrint ("{}:   starting interface criteria test".format(ipaddress))
		
	outputlist = []
	
	dtp_dict = ugliershowdtp(session)
	
	for interface in inputlist:
		
		#show_dtp_int = session.send_command('show dtp interface {} | inc last link down'.format(interface))
		
		
		
		#last_link_down = grab_pattern(show_dtp_int,"last link down on (.*)")
		
		
		try:
		
			last_link_down = dtp_dict[interface]
			
			int_days_down = device_unixdays - intsrsly(getunixdays(last_link_down,tuple_dtp))
			
			if (int_days_down > device_days_up): 
					
				outputlist.append(interface)
				customPrint ("{}:    {} unreliable dtp. Adding".format(ipaddress,interface))
			
			elif (int_days_down >= 60):
					
				outputlist.append(interface)
				customPrint ("{}:    {} down {} days. Adding".format(ipaddress,interface,int_days_down))
					
			else:
				
				
				skippedinterfaces_days += 1
				customPrint ("{}:    {} down {} days. Skipping".format(ipaddress,interface,int_days_down))			
		
		except:
		
			customPrint ("{}:    {} down {} days (switch age). Adding".format(ipaddress,interface,device_days_up))
				
			outputlist.append(interface)	
				
	return (outputlist)
			

	
	
def build_change_list(session,ipaddress):

	global skippedswitches_noint

	(result,reason,device_days_up,device_unixdays) = test_device(session,ipaddress)
	
	if result is False:
		
		return (reason)
			
	intlist_phase1 = get_initial_list(session)
	
	if intlist_phase1 is None:
	
		skippedswitches_noint += 1
		
		return ("{}: No interfaces found.  Exiting".format(ipaddress))

	intlist_phase2 = portsec_test(intlist_phase1,session,ipaddress)
	
	if intlist_phase2 is None:
	
		
		skippedswitches_noint += 1
		
		return ("{}: All identified interfaces already have port-security".format(ipaddress))	

	intlist_phase3 = daysdown_test(intlist_phase2,device_days_up,device_unixdays,session,ipaddress)
	
	if intlist_phase3 == []:
	
		skippedswitches_noint += 1
		
		return ("{}: No interfaces met criteria".format(ipaddress))	
		
	return (intlist_phase3)


def apply_change(inputlist,session,ipaddress):

	global modifiedinterfaces
	
	customPrint ("{}: Applying the following changes:".format(ipaddress))
	
	incrementingmac = 1
	
	
	
	all_the_commands = [""]
	all_the_commands.append ("errdisable recovery cause psecure-violation")
	all_the_commands.append ("errdisable recovery interval 30")	
	for interface in inputlist:
		all_the_commands.append ("interface {}".format(interface))
		all_the_commands.append ("switchport mode access")	
		all_the_commands.append ("switchport port-security")
		all_the_commands.append ("switchport port-security mac 000a.000b.{:04x}".format(incrementingmac))
		incrementingmac = incrementingmac + 1
		modifiedinterfaces += 1

	try:

		customPrint (session.send_config_set(all_the_commands))

	except:
	
		return ("{}: Unable to apply configuration".format(ipaddress))

	customPrint ("")
	customPrint (session.send_command_expect('show archive config differences'))
	customPrint (session.send_command_expect('write memory'))

			
def netmiko_session(ipaddress,deviceSSH):

	global skippedswitches_ssh

	try:
		
		session = ConnectHandler(**deviceSSH)
			
	except:

		
		skippedswitches_ssh += 1
		
		return ("{}: Unable to connect (SSHException)".format(ipaddress))

	interfaceList = build_change_list(session,ipaddress)
	
	if whatisthis(interfaceList) == 'str':
		
		return (interfaceList)
			
	else:
		
		apply_change(interfaceList,session,ipaddress)
	
		return ("{}: Successful Exit".format(ipaddress))
	


			
deviceList = []

for line in input:

	deviceIP = grab_pattern(line,"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
		
	if deviceIP is not None:
		
		deviceList.append(deviceIP)

if deviceList == []:
			
	customPrint("Empty list, exiting\n\n")
		
	sys.exit()			


		
for ipaddress in deviceList:

	totaldevices += 1
	
	customPrint ("{}: Trying to connect".format(ipaddress))
	
	deviceSSH = {
		'device_type': 'cisco_ios',
		'ip': '{}'.format(ipaddress),
		'username': '{}'.format(username),
		'password': '{}'.format(password),
		'port' : 22, 
		'verbose': True,
	} 

	customPrint (netmiko_session(ipaddress,deviceSSH))
	customPrint ("\n")


#Timestamp this when it ends
scriptend = datetime.datetime.now().time()




print ("Script Started: {}".format(scriptstart),file=stats)
print ("{} Total switches".format(totaldevices),file=stats)
print ("{} switches skipped due to SSH error".format(skippedswitches_ssh),file=stats)
print ("{} switches skipped due to uptime less than 60 days".format(skippedswitches_days),file=stats)
print ("{} switches skipped with no eligibile interfaces".format(skippedswitches_noint),file=stats)
#print ("{} switches skipped for other reasons".format(skippedswitches_other),file=stats)
print ("{} total interfaces".format(totalinterfaces),file=stats)
print ("{} interfaces with port security already applied".format(skippedinterfaces_psec),file=stats)
print ("{} interfaces down less than 60 days".format(skippedinterfaces_days),file=stats)
print ("{} interfaces modified".format(modifiedinterfaces),file=stats)
print ("Script Finished: {}".format(scriptend,file=stats),file=stats)
		
sys.exit("Clean Exit")




	

