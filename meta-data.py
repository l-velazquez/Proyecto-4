###############################################################################
#
# Filename: meta-data.py
# Author: Jose R. Ortiz and ... (hopefully some students contribution)
# Student Contributor: Luis Fernando Javier Velazquez Sosa
# Description:
# 	MySQL support library for the DFS project. Database info for the 
#       metadata server.
#
# Please modify globals with appropiate info.

from mds_db import *
from Packet import *
import sys
import socketserver# changed to python 3.8 module

def usage():
	print ("""Usage: python %s <port, default=8000>""" % sys.argv[0] )
	sys.exit(0)


class MetadataTCPHandler(socketserver.BaseRequestHandler):

	def handle_reg(self, db, p):
		"""Register a new client to the DFS  ACK if successfully REGISTERED
			NAK if problem, DUP if the IP and port already registered
		"""
		try:
			if db.AddDataNode(p.getAddr(),p.getPort()) != 0:# Fill condition:
				self.request.sendall("ACK") 
			else:
				self.request.sendall("DUP")
		except:
			self.request.sendall("NAK")

	def handle_list(self, db):
		"""Get the file list from the database and send list to client"""
		try:
			dbfiles = db.GetFiles()
			packet = Packet()
			packet.BuildListResponse(dbfiles)
			self.request.sendall(packet.getEncodedPacket)

		except:
			self.request.sendall("NAK")	

	def handle_put(self, db, p):
		"""Insert new file into the database and send data nodes to save
		   the file.
		"""
	       
		# Fill code
		fileInfo = p.getFileInfo()

		if db.InsertFile(fileInfo[0], fileInfo[1]):
			dataNodes = db.GetDataNodes()
			p.BuildPutResponse(dataNodes)
			self.request.sendall(p.getEncodedPacket)
		else:
			self.request.sendall("DUP")
	
	def handle_get(self, db, p):
		"""Check if file is in database and return list of
			server nodes that contain the file.
		"""

		# Fill code to get the file name from packet and then 
		# get the fsize and array of metadata server
		fileName = p.getFileName()
		fileSize,MetadataList = db.GetFileInode(fileName)

		if fileSize:
			# Fill code
			p.BuildGetResponse(MetadataList,fileSize)
			self.request.sendall(p.getEncodedPacket)
		else:
			self.request.sendall("NFOUND")

	def handle_blocks(self, db, p):
		"""Add the data blocks to the file inode"""

		# Fill code to get file name and blocks from
		# packet
		fileName = p.getFileName()
		blocks = p.getDataBlocks()
		db.AddBlockToInode(fileName,blocks)
		# Fill code to add blocks to file inode

		
	def handle(self):

		# Establish a connection with the local database
		db = mds_db("dfs.db")
		db.Connect()

		# Define a packet object to decode packet messages
		p = Packet()

		# Receive a msg from the list, data-node, or copy clients
		msg = self.request.recv(1024)
		print (msg, type(msg))
		
		# Decode the packet received
		p.DecodePacket(msg)
	

		# Extract the command part of the received packet
		cmd = p.getCommand()

		# Invoke the proper action 
		if   cmd == "reg":
			# Registration client
			self.handle_reg(db, p)

		elif cmd == "list":
			# Client asking for a list of files
			self.handle_reg(db)
		
		elif cmd == "put":
			# Client asking for servers to put data
			self.handle_reg(db, p)
		
		elif cmd == "get":
			# Client asking for servers to get data
			self.handle_reg(db,p)

		elif cmd == "dblks":
			# Client sending data blocks for file
			 self.handle_reg(db,p)

		db.Close()

if __name__ == "__main__":
	HOST, PORT = "", 8000

	if len(sys.argv) > 1:
		try:
			PORT = int(sys.argv[1])
		except:
			usage()

	server = socketserver.TCPServer((HOST, PORT), MetadataTCPHandler)

	# Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
	server.serve_forever()
