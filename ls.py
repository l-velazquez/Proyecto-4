###############################################################################
#
# Filename: ls.py
# Author: Jose R. Ortiz and Luis Fernando Javier Velázquez Sosa
#
# Description:
# 	List client for the DFS
#



import socket
import sys
from Packet import *

def usage():
	print ("""Usage: python %s <server>:<port, default=8000>""" % sys.argv[0])
	sys.exit(0)

def client(ip, port):

	# Contacts the metadata server and ask for list of files.
	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sock.connect((ip,port))

	package = Packet()
	package.BuildListPacket()
	sock.sendall(package.getEncodedPacket())

	receive = sock.recv(1024)

	package.DecodePacket(receive)
	file_arr = package.getFileArray()

	for i in file_arr:
		print (i[0],i[1],"bytes")

if __name__ == "__main__":

	if len(sys.argv) < 2:
		usage()

	ip = None
	port = None 
	server = sys.argv[1].split(":")
	if len(server) == 1:
		ip = server[0]
		port = 8000
	elif len(server) == 2:
		ip = server[0]
		port = int(server[1])

	if not ip:
		usage()

	client(ip, port)
