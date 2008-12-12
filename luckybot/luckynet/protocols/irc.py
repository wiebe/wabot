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

from luckybot.luckynet.protocols.simple import LineProtocol
import gobject
import re

class Parser(object):
	"""
		Represents incoming data from an IRC server
	"""
	
	@classmethod
	def parse(self, data):
		"""
			Parses received data from the IRC server to an object containing all
			sorts of data.
			
			@type data: string
			@param data: The data to parse
			
			@rtype: ServerMessage|ChannelMessage
			@return: A ServerMessage or ChannelMessage object containing all data
		"""
		
		if len(data) == 0:
			return None
		
		if data[0] == ':':
			# Get all message parts
			regexp = re.compile(r'\:(.*?) ([a-z0-9]+) (.*?)\r?\n', re.I)
			match = regexp.match(data)
			
			message_from = match.group(1)
			command = match.group(2)
			params = match.group(3).strip()
			
			return_obj = None
			
			# Check from who this message came
			if message_from.find("@") != -1:
				# Message came from a user
				# Retreive nick etc
				regexp2 = re.compile(r'(.*?)!(.*?)@(.*?)$')
				match2 = regexp2.match(message_from)
				
				# Get the channel
				regexp = re.compile(r'#([^ ]+)')
				
				match = regexp.match(params)
				if match:
					channel = '#%s' % match.group(1)
				else:
					channel = match2.group(1)
				
				return_obj = ChannelMessage(data, message_from, command, params, match2.group(1), match2.group(2), match2.group(3), params[params.find(':')+1:], channel)
			else:
				return_obj = ServerMessage(data, message_from, command, params)
			
			return return_obj
		else:
			return None

class ServerMessage(gobject.GObject):
	"""
		This is the base class for a message received from the IRC server
	"""
	
	sender = ""
	command = ""
	params = ""
	raw = ""
	
	def __init__(self, raw, sender, command, params):
		gobject.GObject.__init__(self)
		
		self.raw = raw
		self.sender = sender
		self.command = command
		self.params = params
	
	def __str__(self):
		return self.raw

class ChannelMessage(ServerMessage):
	"""
		This class represents a message said in a channel/Private conversation
	"""
	
	nick = ""
	realname = ""
	hostname = ""
	channel = ""
	message = "" 
	
	def __init__(self, raw, sender, command, params, nick, realname, hostname, message, channel):
		ServerMessage.__init__(self, raw, sender, command, params)
		
		self.nick = nick
		self.realname = realname
		self.hostname = hostname
		self.message = message
		self.channel = channel

gobject.type_register(ServerMessage)
gobject.type_register(ChannelMessage)

class Format(object):
	"""
		This class can be used to format messages sent to the IRC server
	"""
	
	black = 1
	darkblue = 2
	green = 3
	red = 4
	darkred = 5
	purple = 6
	orange = 7
	yellow = 8
	lightgreen = 9
	aqua = 10
	lightblue = 11
	blue = 12
	violet = 13
	grey = 14
	lightgrey = 15
	white = 16
	
	@classmethod
	def color(self, color):
		"""
			Add a color to a message
			
			@type color: string
			@param color: The color textual name (NOT the number)
		
			@rtype: string
			@return: The string for the color
		"""
		try:
			code = getattr(self, color)
		except:
			code = 1
		
		return "\x03%02.f" % (code)
	
	@classmethod
	def normal(self):
		"""
			Reset to the default color
			
			@rtype: string
			@return: The string which resets the color
		"""
		return "\x0F"
	
	@classmethod
	def bold(self):
		"""
			Make the text bold
		"""
		return "\x02"
	
	@classmethod
	def reverse(self):
		"""
			Make the text italic (doet not work for all clients)
		""" 
		return "\x16"
	
	@classmethod
	def underline(self):
		"""
			Underline the text
		"""
		return "\x1F"
	
	@classmethod
	def remove(self, string):
		"""
			Remove all format in the given string
			
			@type string: str
			@param string: The string where to remove format from
			
			@rtype: str
			@return: The string without format
		"""
		
		regexp = re.compile('(?:(?:\x03[0-9]+)|(?:\x0F|\x02|\x16|\x1F))', re.I)
		
		return regexp.sub('', string)

class IRCClient(LineProtocol):
	"""
		Class representing the IRC Protocol
	"""
	
	nickname = ""
	invisible = True
	
	def __init__(self, nickname, password, invisible = True):
		"""
			Sets some vars
		"""
		
		self.nickname = nickname
		self.password = password
		self.invisible = invisible
		
	def handle_connect(self):
		"""
			Called when the client is connected
			
			This function authenticates the bot with the IRC 
			server
		"""
		
		self.send('USER %s %d * :%s' % (self.nickname, 1 if self.invisible else 0, self.nickname))
		
		self.set_nick(self.nickname)
		
		if self.password:
			self.send_pm('nickserv', 'identify %s' % self.password)
	
	def on_line_received(self, data):
		"""
			Called when a line arrives from the socket
			This function parses the data
			
			@type data: string
			@param data: The received data
		"""
		
		if data[0:4] == 'PING':
			# Reply to ping
			self.send('PONG :%s' % data[6:])
		
		message = Parser.parse(data)
		
		self.check_message(message)
	
	def check_message(self, message):
		"""
			Checks the given message object and calls a correspondending
			method
		"""
		
		if isinstance(message, ChannelMessage):
			if hasattr(self, 'on_message'):
				self.on_message(message)
		else:
			if hasattr(self, 'on_command_%s' % message.command):
				func = getattr(self, 'on_command_%s' % message.command)
				func(message)
			
			if hasattr(self, 'on_command'):
				self.on_command(message)
	
	def send_pm(self, nick, message):
		"""
			Sends a message to a channel or nickname
			
			@type nick: string
			@param nick: The channel or nickname to send a message
			
			@type message: string
			@param message: The message to send
		"""
		
		return self.send("PRIVMSG %s :%s" % (nick, message))
	
	def send_notice(self, nick, message):
		"""
			Sends a notice to a given channel/nickname
			
			@type nick: string
			@param nick: The channel or nickname to send a notice
			
			@type message: string
			@param message: The message to send
		"""
		
		return self.send("NOTICE %s :%s" % (nick, message))
	
	def send_action(self, dest, message):
		"""
			Sends an 'action' message to a given destination
			Like you use the /me command on a normal IRC client
			
			@type dest: string
			@param dest: The nickname or channel you want to send to
			
			@type message: string
			@param message: The message
		"""
		
		self.send_pm(dest, "\001ACTION %s\001" % message)
	
	def join(self, channel):
		"""
			Joins a given channel
			
			@type channel: string
			@param channel: The channel to join
		"""
		
		if not channel.startswith('#'):
			channel = '#%s' % (channel)
		
		self.send("JOIN %s" % channel)
	
	def part(self, channel):
		"""
			Leaves a given channel
			
			@type channel: string
			@param channel: The channel to leave
		"""
		
		if not channel.startswith('#'):
			channel = '#%s' % channel
		
		self.send("PART %s" % channel)

	def set_nick(self, nickname):
		"""
			Changes the nickname
			
			@type nickname: string
			@param nickname: The new nickname
		"""
		
		self.send("NICK %s" % nickname)
		
