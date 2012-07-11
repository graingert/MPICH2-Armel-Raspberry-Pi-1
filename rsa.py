import subprocess
import getpass
import fcntl
import struct
import socket
from subprocess import Popen  

def this_ip(ifname):
	soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(soc.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])
	
clear = Popen(["clear"])
waitclear = clear.wait()
this_user = getpass.getuser()

if this_user == "root":
	print "=====RSA Public-Private Key Python Setup Script v0.1 for RPi========"
	print "Starting script in ROOT mode. Ensure you also run for regular users."
	print "===================================================================="
else:
	print "=====================RSA Public-Private Key Python Setup Script v0.1 for RPi======================"
	print "Starting script under user \"" + this_user +  "\". If you want to setup RSA key access for ROOT, run script as ROOT."
	print "=================================================================================================="

key_directory = raw_input("Enter directory to store keys (Enter 'd' for default /home/" + this_user + "/.ssh/id_rsa): ")
print "Generating RSA key pair, please wait..."
if key_directory in ["d", "D"]:
	key_directory = "/home/" + this_user + "/.ssh/id_rsa"
key_gen = Popen(["ssh-keygen", "-t", "rsa"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output = key_gen.communicate(key_directory)
key_gen_wait = key_gen.wait()

number_done = False
number_error = False
while number_done == False:
	try:	
		if number_error == False:
			count = input("\nEnter number of Raspberry Pis to setup: ")
		else:
			count = input("Error: Not a number. Enter number of Raspberry Pis to setup: ")
		number_done = True
	except (SyntaxError, ValueError, NameError):
		number_error = True
		
done = False
x = 0
while done == False:
	username = raw_input("Enter in the username of Pi: ")
	ip_valid = False
	bad_ip = False
	while ip_valid == False:
			if bad_ip == True:
				ip = raw_input("Error: Invalid IPv4 address. Enter in IP of Pi: ")
			else:
				ip = raw_input("Enter in IP of Pi: ")
			try:
				socket.inet_aton(ip)
				if len(ip.split(".")) == 4:
					ip_valid = True
				else:
					bad_ip = True
			except socket.error:
				bad_ip = True
				
	print "You will now be prompted for the password of your Pi for the only time...\n"
	ssh_cat = Popen(["cat", key_directory + ".pub"], stdout=subprocess.PIPE)
	ssh_cat_wait = ssh_cat.wait()
	ssh_cat_pipe = Popen(["ssh", username + "@" + ip, "mkdir", ".ssh;cat", ">>", ".ssh/authorized_keys"], stdin=ssh_cat.stdout, stderr=subprocess.PIPE)
	ssh_cat_pipe_wait = ssh_cat_pipe.wait()
	
	if "ssh:" in ssh_cat_pipe.stderr.read():
		print "Error: Connection failed. Check correct username and IP address and try again."
	else:
		x += 1
		print "\nRSA key access successfully setup between " + this_user + "@" + this_ip("eth0") + " and " + username + "@" + ip
	if x == count:
		break
