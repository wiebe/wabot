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

import gobject
import os
import luckybot
from luckybot.luckynet.protocols import irc
from luckybot.bot.client import LuckyBotClient
import luckybot.bot.plugins as plugins
import luckybot.bot.auth as auth
import luckybot.path as path
from ConfigParser import SafeConfigParser

class LuckyBot(object):
	"""
		This is the main bot class, where every thing is controlled from
	"""
	
	def __init__(self, options, args):
		"""
			Initializes the bot, reads settings, and setups auth/plugin manager
		"""
		
		self.view = None
		
		# Load settings
		self.settings = SafeConfigParser()
		if os.path.exists(path.get_personal_file('settings.ini')):
			self.settings.read([path.get_personal_file('settings.ini')])
		else:
			self.settings.read(path.get_base_path('data', 'settings.ini'))
			
		self.plugins = plugins.Manager(self)
		self.auth = auth.Manager()
		
		self.joined = False
		self._buffer = ""
		self.options = options
		self.args = args
		self.client = None
	
	def set_view(self, view):
		"""
			This sets the view for the bot
			
			@type view: views.base.BaseView
			@param view: The view for the bot, which displays all info on the screen
		"""
		self.view = view
		self.view.set_bot(self)		
	
	def connect_to_server(self, host = None, port = None):
		"""
			Opens the connection to a specified IRC Server
			
			If called without paramaters, the hostname and port is read 
			from the settings file.
			
			@type host: string
			@param host: The server name
			
			@type port: int
			@param port: The port to connect on
		"""
		
		if hasattr(self, 'client') and self.client != None:
			del self.client
			
		if host == None:
			host = self.settings.get('Server', 'hostname')
		
		if port == None:
			port = self.settings.getint('Server', 'port')
				
		connection = self.view.get_connection()
		protocol = LuckyBotClient(self, self.settings.get('Bot', 'nickname'), self.settings.getboolean('Bot', 'invisible'))
		protocol.connect('irc-message', self.on_message)
		protocol.connect('data-sent', self.on_data_sent)
		protocol.connect('data-received', self.on_data_received)
		protocol.connect('closed', self.on_client_close)
		
		connection.set_protocol(protocol)
		connection.open((host, port))
		connection.setblocking(0)
		
		self.client = protocol
	
	def on_message(self, protocol, message):
		self.plugins.check_data(message)
	
	def on_data_received(self, protocol, data):
		self.view.data_in(data)
			
	def on_data_sent(self, protocol, data):
		"""
			Called when data is sent, sends the data to our view
		"""
		
		self.view.data_out(data)
	
	def on_client_close(self, protocol):
		"""
			Called when the socket is closed
		"""
		if hasattr(self, 'client'):
			del self.client
			
		self.view.on_close()
		
		print "Closed protocol"
		
		
		
