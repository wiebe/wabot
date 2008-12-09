#
# Luckyluckybot4, a python IRC luckybot
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
import re
from gettext import gettext as _

def initialize():	
	plugin.register_command('login', do_login, help=_("Login with specified password"), args="password")
	plugin.register_command('logout', logout, help=_("Logout"))
	plugin.register_command('checklogin', check_login, help=_("Check if you're logged in"))
	plugin.register_message_handler(on_message)

def do_login(message, keywords):
	password = base64.b64encode(message.bot_args)
	
	users = plugin.bot.settings.options('Admins')
	
	for nick in users:
		if message.nick.lower() == nick.lower() and password == plugin.bot.settings.get('Admins', nick):
			# Valid username/password
			if plugin.bot.auth.check_logged_in(message.nick):
				plugin.bot.client.send_notice(message.nick, _("You're already logged in"))
				return
			else:
				plugin.bot.auth.log_in(message.nick)
				plugin.bot.client.send_notice(message.nick, _("You've been succesfully logged in"))
				return
	
	plugin.bot.client.send_notice(message.nick, _("The password you entered is not correct"))

def check_login(message, keywords):
	if plugin.bot.auth.check_logged_in(message.nick):
		plugin.bot.client.send_notice(message.nick, _("You're logged in"))
	else:
		plugin.bot.client.send_notice(message.nick, _("You're not logged in"))

def logout(message, keywords):
	plugin.bot.auth.log_out(nick)

def on_message(message):
	if hasattr(message, 'command'):
		if message.command == 'NICK':
			print "Nickchange"
			if plugin.bot.auth.check_logged_in(message.nick):
				plugin.bot.auth.log_out(message.nick)
				plugin.bot.auth.log_in(message.message)
		
		if message.command == 'QUIT':
			if plugin.bot.auth.check_logged_in(message.nick):
				plugin.bot.auth.log_out(message.nick)
	
	
