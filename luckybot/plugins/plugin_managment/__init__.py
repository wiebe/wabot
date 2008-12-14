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

from gettext import gettext as _
from luckybot.luckynet.protocols.irc import Format
from luckybot.bot.plugins import Plugin

class PluginManagment(Plugin):
	def initialize(self):
		self.register_command('load', self.load_plugin, help=_("Load a currently unloaded plugin"), args="plugin")
		self.register_command('unload', self.unload_plugin, help=_("Unloads a given plugin"), args="plugin")
		self.register_command('reload', self.reload_plugins, help=_("Reloads all bot plugins, or the specified plugin"), args="[plugin]")

	def load_plugin(self, message, keywords):
		if not self.bot.auth.check_logged_in(message.nick):
			self.bot.client.send_notice(message.nick, _("You do not have enough rights to use this command"))
			return
		
		if len(message.bot_args) == 0:
			return
		
		for dir in self.manager.dirs:
			success = False
			
			if self.manager.load_plugin(dir, message.bot_args):
				success = True
				break
		
		if not success:
			self.bot.client.send_pm(message.channel, Format.color('red') + Format.bold() + _("Could not load the plugin"))
		else:
			self.bot.client.send_pm(message.channel, Format.color('green') + _("Plugin succesfully loaded"))

	def unload_plugin(self, message, keywords):
		if not self.bot.auth.check_logged_in(message.nick):
			self.bot.client.send_notice(message.nick, _("You do not have enough rights to use this command"))
			return
			
		if len(message.bot_args) == 0:
			return
		
		if not self.manager.unload_plugin(message.bot_args):
			self.bot.client.send_pm(message.channel, Format.color('red') + Format.bold() + _("Could not unload the plugin"))
		else:
			self.bot.client.send_pm(message.channel, Format.color('green') + _("Plugin succesfully unloaded"))
		
	def reload_plugins(self, message, keywords):
		if not self.bot.auth.check_logged_in(message.nick):
			self.bot.client.send_notice(message.nick, _("You do not have enough rights to use this command"))
			return
		
		self.bot.client.send_pm(message.channel, Format.color('orange') + _("Reloading.."))
		if len(message.bot_args) != 0:
			success = self.manager.reload_plugin(message.bot_args)
		else:
			success = self.manager.reload_plugins()
		
		if not success:
			self.bot.client.send_pm(message.channel, Format.color('red') + Format.bold() + _("Could not reload the plugin(s)"))
		else:
			self.bot.client.send_pm(message.channel, Format.color('green') + _("Plugin(s) succesfully reloaded"))
