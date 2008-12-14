#
# LuckyBot4, a python IRC luckybot
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

import base64
from gettext import gettext as _
from luckybot.bot.plugins import Plugin

class AuthenticationPlugin(Plugin):
	def initialize(self):	
		self.register_command('login', self.do_login, help=_("Login with specified password"), args="password")
		self.register_command('logout', self.logout, help=_("Logout"))
		self.register_command('checklogin', self.check_login, help=_("Check if you're logged in"))
		self.register_message_handler(self.on_message)

	def do_login(self, message, keywords):
		password = base64.b64encode(message.bot_args)
		
		users = self.bot.settings.options('Admins')
		
		for nick in users:
			if message.nick.lower() == nick.lower() and password == self.bot.settings.get('Admins', nick):
				# Valid username/password
				if self.bot.auth.check_logged_in(message.nick):
					self.bot.client.send_notice(message.nick, _("You're already logged in"))
					return
				else:
					self.bot.auth.log_in(message.nick)
					self.bot.client.send_notice(message.nick, _("You've been succesfully logged in"))
					return
		
		self.bot.client.send_notice(message.nick, _("The password you entered is not correct"))

	def check_login(self, message, keywords):
		if self.bot.auth.check_logged_in(message.nick):
			self.bot.client.send_notice(message.nick, _("You're logged in"))
		else:
			self.bot.client.send_notice(message.nick, _("You're not logged in"))

	def logout(self, message, keywords):
		self.bot.auth.log_out(nick)

	def on_message(self, message):
		if hasattr(message, 'command'):
			if message.command == 'NICK':
				print "Nickchange"
				if self.bot.auth.check_logged_in(message.nick):
					self.bot.auth.log_out(message.nick)
					self.bot.auth.log_in(message.message)
			
			if message.command == 'QUIT':
				if self.bot.auth.check_logged_in(message.nick):
					self.bot.auth.log_out(message.nick)
	
	
