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

from luckybot.luckynet.protocols import irc
import gobject

class LuckyBotClient(irc.IRCClient, gobject.GObject):
	"""
		This class handles parsing incoming data
	"""
	
	__gsignals__ = {
		'irc-message': (gobject.SIGNAL_RUN_LAST, None, (irc.ServerMessage,)),
		'data-received': (gobject.SIGNAL_RUN_LAST, None, (str,)),
		'data-sent': (gobject.SIGNAL_RUN_LAST, None, (str,)),
		'closed': (gobject.SIGNAL_RUN_LAST, None, ())
	}
	
	def __init__(self, bot, nickname, password, invisible = True):
		"""
			Constructor, calls parent constructors
		"""
		
		gobject.GObject.__init__(self)
		irc.IRCClient.__init__(self, nickname, password, invisible)
		self.bot = bot
	
	def handle_write(self):
		if len(self.send_queue) != 0:
			item = self.send_queue[0]		
			item.sent(self.connection.send(item.read()))
			
			if item.is_complete():				
				del self.send_queue[0]
				string = str(item)
				del item
		
				self.emit('data-sent', string)
	
	def handle_close(self):
		self.emit('closed')
		
	
	def on_line_received(self, data):
		irc.IRCClient.on_line_received(self, data)
		self.emit('data-received', data)
	
	def check_message(self, message):
		"""
			This methods inspects a received irc message. It checks if it contains a bot
			command, and if so, parses the command name, and arguments
			
			Then it passes the message through our plugin manager, and eventually respons to ping
			or joins the channels when the time is right.
		
			@type message: luckybot.luckynet.protocols.irc.ServerMessage
			@param message: The IRC Message
		"""
		data = str(message)
		if data[0:4] == 'PING':
			# Reply to ping
			self.send('PONG :%s' % data[6:])
		
		if message == None:
			return
		
		if isinstance(message, irc.ChannelMessage):
			cmd_prefix = self.bot.settings.get('Bot', 'command_prefix')
			
			# A message sent in PM/Channel
			if message.message[0:len(cmd_prefix)] == cmd_prefix:
				space_pos = message.message.find(' ', len(cmd_prefix))
				if space_pos == -1:
					space_pos = len(message.message)
					
				command = message.message[len(cmd_prefix):space_pos]
				message.bot_command = command
				message.bot_args = message.message[space_pos+1:]
			
		self.emit('irc-message', message)
		irc.IRCClient.check_message(self, message)
	
	def on_command_001(self, message):
		"""
			Called when we succesfully authenticate with the IRC Server
			This means we can safely join
		"""
		
		channels = self.bot.settings.get('Server', 'channels').split(',')
		for channel in channels:
			self.join(channel)
	
