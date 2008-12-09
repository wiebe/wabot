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

from luckybot.luckynet.protocol import Protocol

class LineProtocol(Protocol):
	"""
		Simple protocol which reads lines
	"""
	
	received_buffer = ""
	
	def send(self, data):
		"""
			Sends the given data, and automaticly adds a newline to the 
			end
			
			@type data: string
			@param data: The data to send
		"""
		
		return Protocol.send(self, "%s\n" % data)
	
	def on_data(self, data):
		"""
			Called when it's time to read something from the socket
			So this function reads some data from the server and adds 
			it to the buffer
		"""
		self.received_buffer += data
		
		self.check_buffer()
	
	def check_buffer(self):
		"""
			This function checks if the buffer contains a new line
		"""
		
		pos = self.received_buffer.find("\n")
		
		if pos != -1:
			data = self.received_buffer[0:pos+1]
			
			if hasattr(self, 'on_line_received'):
				self.on_line_received(data)
			
			self.received_buffer = self.received_buffer[pos+1:]
			
			if self.received_buffer.find("\n") != -1:
				self.check_buffer()
		
		
