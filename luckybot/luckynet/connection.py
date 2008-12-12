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

import socket
import gobject
			
class GlibConnection:
	"""
		This class represents a connection
		using gobject IOChannel to integrate with the main glib loop
	"""
	
	def __init__(self, family, type, protocol = None):
		"""
			Constructor initializes some vars
		"""
		
		self._family = family
		self._type = type
		
		if protocol != None:
			self.set_protocol(protocol)
		
		self._buffer = []
		self._io_condition = 0
		self._watch_id = 0
		
	def set_protocol(self, protocol):
		self.protocol = protocol
		self.protocol.set_connection(self)
	
	def open(self, addr):
		"""
			Opens and creates a new socket object plus an IOChannel
			object, connecting to the given address
			
			@type addr: tuple
			@param addr: A tuple containing the address and port
		"""
		
		try:
			self._socket = socket.socket(self._family, self._type)
			self._socket.connect(addr)
				
			self._addr = addr
		except socket.error, e:
			if e[0] in [EINPROGRESS, EALREADY, EWOULDBLOCK]:
				return
			else:
				raise socket.error, e
				
		self.connected = True
		
		self.iochannel = gobject.IOChannel(self._socket.fileno())
		self.iochannel.set_encoding(None)
		self.iochannel.set_buffered(False)
		self.iochannel.set_flags(self.iochannel.get_flags() | gobject.IO_FLAG_NONBLOCK)
		
		self._set_watch(gobject.IO_IN | gobject.IO_PRI | gobject.IO_ERR | gobject.IO_HUP)
		self.handle_connect_event()
	
	def close(self):
		"""
			Closes the socket
		"""
		
		self.iochannel.close()
		
		try:
			self._socket.close()
			del self._socket
			self._fileno = -1
			self.connected = False
			
			self.handle_close_event()
		except socket.error, e:
			if e[0] in [ECONNRESET, ENOTCONN]:
				self.handle_close_event()
			else:
				raise socket.error, e
	
	def recv(self, length):
		"""
			Reads data from the socket
			
			@type length: int
			@param length: Number of bytes to read
		"""
		
		data = self.iochannel.read(length)
		
		if data == "":
			self.handle_close_event()
			return ''
		
		return data
	
	def send(self, data):
		"""
			Writes data to the socket
			
			@type data: string
			@param data: The data to send
		"""
		
		return self.iochannel.write(data)
	
	def readable(self):
		"""
			Called before select, to check if this socket is readable
			Default is to check the protocol object, but can be changed if necessary
			by subclasses
		"""
		
		return self.protocol.readable()
	
	def writeable(self):
		"""
			Called before select to check if this socket needs to write something
			this makes sure no unnecessary called will be made
		"""
		
		return self.connected and self.protocol.writeable()
		
	def has_buffer(self):
		"""
			Add IO_OUT watch
		"""
		self._add_condition(gobject.IO_OUT)
	
	def _remove_watch(self):
		"""
			Remove the IOChannel event handler
		"""
		
		gobject.source_remove(self._watch_id)
		self._watch_id = 0
		self._io_condition = 0
		
	def _set_watch(self, condition):
		"""
			Set the IOChannel event handler with a given condition
			
			@type condition: int
			@param condition: The conditions
		"""
			
		if self._watch_id != 0:
			self._remove_watch()
		
		self._io_condition = condition
		self._watch_id = self.iochannel.add_watch(condition, self._io_handler)
	
	def _add_condition(self, condition):
		"""
			Add an additional condition to the current handler
			
			@type condition: int
			@param condition: The condition to add
		"""
		
		if self._io_condition & condition == condition:
			return
		
		self._io_condition |= condition
		self._set_watch(self._io_condition)
	
	def _remove_condition(self, condition):
		if self._io_condition & condition == 0:
			return
			
		self._io_condition ^= condition
		self._set_watch(self._io_condition)
	
	def _io_handler(self, channel, condition):
		"""
			Our IO handler, this function will be called when we can perform 
			i/o operations without blocking the GUI
			
			@type channel: gobject.IOChannel
			@param channel: The channel we're on
			
			@type condition: int
			@param condition: The condition(s) which apply for this call
		"""
		
		if (condition & (gobject.IO_IN | gobject.IO_PRI)) != 0:
			self.handle_read_event()
		
		if (condition & (gobject.IO_ERR | gobject.IO_HUP)) != 0:
			self.handle_close_event()
			
		if (condition & gobject.IO_OUT) != 0:
			self.handle_write_event()
			
			if not self.writeable():
				self._remove_condition(gobject.IO_OUT)
		
		return True
	
	def handle_read_event(self):
		"""
			This checks if the current instance has an event handler
			for a read event and calls it if it exists
		"""
		
		if not self.connected:
			self.connected = True
			self.handle_connect_event()
		
		if hasattr(self.protocol, 'handle_read'):
			self.protocol.handle_read()
	
	def handle_write_event(self):
		"""
			This checks if the current instance has an event handler
			for a write/out event and calls it if it exists
		"""
		
		if not self.connected:
			self.connected = True
			self.handle_connect_event()
		
		if hasattr(self.protocol, 'handle_write'):
			self.protocol.handle_write()
	
	def handle_connect_event(self):
		"""
			This checks if the current instance has an event handler
			for a connect event and calls it if it exists
		"""
		
		if hasattr(self.protocol, 'handle_connect'):
			self.protocol.handle_connect()		
	
	def handle_close_event(self):
		"""
			This checks if the current instance has an event handler
			for a close event and calls it if it exists
		"""
		
		try:
			if self.connected:
				self.iochannel.close()
		except:
			pass
		
		self.connected = False
		
		if hasattr(self.protocol, 'handle_close'):
			self.protocol.handle_close()
	
	def handle_error(self, type, value, traceback):
		"""
			Called when an error occurs
		"""
		
		if hasattr(self.protocol, 'handle_error'):
			self.protocol.handle_error(type, value, traceback)
		else:
			print 'Socket Error'
			
			print 'Type:', type
			print 'Value:', value
			print 'Traceback:'
			print traceback
	
	@property
	def addr(self):
		"""
			Returns the address
		"""
		
		return self._addr
			
	def fileno(self):
		"""
			Returns the socket fileno. We cache it so we can we can
			retreive it	even when it's closed.
		"""
		
		if self._fileno == -1:
			self._fileno = self._socket.fileno()
		
		return self._fileno
	
	def __getattr__(self, name):
		"""
			Redirect calls to our socket object
		
			@type name: string
			@param name: Attribute name
		"""
		
		if hasattr(self._socket, name):
			return getattr(self._socket, name)
		else:
			raise AttributeError, 'Undefined attribute %s' % name
		
