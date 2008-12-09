#
# LuckyBot4, a python IRC bot
# (c) Copyright 2008 by Lucas van Dijk
# http://www.return1.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA
#
# $Id$
#

from luckybot.luckynet.connection import *

class OutgoingPacket(object):
	"""
		This class represents data to be asyncrhously sent
		
		This class is used to track how many of the packet is sent, so we
		can track if we need to sent more of this packet
	"""
	
	def __init__(self, data):
		self.data = data
		self.length = len(data)
		self._sent = 0
	
	def read(self, length = 2048):
		if length != None:
			return self.data[self._sent:][0:length]
		
		return self.data[self._sent:]
	
	def sent(self, bytes):
		self._sent += bytes
		
	def is_complete(self):
		return self._sent >= self.length
	
	def __str__(self):
		return self.data

class BaseProtocol(object):
	"""
		Base (abstract) class for all protocols
	"""
	
	def __init__(self):
		"""
			Constructor, does nothing at the moment
		"""
		
		pass
	
	def set_connection(self, connection):
		"""
			Sets the connection object
			
			@type connection: luckybot.luckynet.connection.Connection
			@param connection: The connection object
		"""
		
		self.connection = connection
	
	def handle_write(self):
		"""
			Called when we can safely send something to the socket
		"""
		
		pass
	
	def handle_read(self):
		"""
			Called when the socket is available for reading
		"""
		pass
	
	def handle_connect(self):
		"""
			Called when a connection is made
		"""
		pass
	
	def handle_close(self):
		"""
			Called when the connection is closed
		"""
		pass
	
	def readable(self):
		"""
			Check if it's allowed to read
		"""
		
		return True
	
	def writeable(self):
		"""
			Check if we have something to write
		"""
		
		return True

class Protocol(BaseProtocol):
	"""
		Base class for a protocol
	"""
	
	send_queue = []
	
	def send(self, data):
		"""
			Adds the given data to the buffer,
			and it will be sent when the time is right
		"""
		
		self.send_queue.append(OutgoingPacket(data))
		
		self.connection.has_buffer()
	
	def handle_write(self):
		"""
			Called when we safely can send something to the socket
			
			This function sends the buffer (partially), and then updates
			our local buffer variable, depending on how many bytes we
			actually have sent
		"""
		
		if len(self.send_queue) != 0:
			item = self.send_queue[0]		
			item.sent(self.connection.send(item.read()))
			
			if item.is_complete():				
				del self.send_queue[0]
				del item
	
	def handle_read(self):
		"""
			Called when there's data available
			
			This function then reads data from the socket, and calls an
			event handler if it exists
		"""
		data = self.connection.recv(2048)
		
		if hasattr(self, 'on_data'):
			self.on_data(data)
	
	def writeable(self):
		return len(self.send_queue) != 0
	
