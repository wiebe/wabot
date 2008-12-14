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

import luckybot
import luckybot.bot
import time
import datetime
from luckybot.luckynet.protocols.irc import Format
from luckybot.bot.plugins import Plugin
from gettext import gettext as _

class BotInfo(Plugin):

	def initialize(self):
		self.register_command("info", self.show_info, help=_("Shows the bot credits"))
		self.register_command("plugins", self.list_plugins, help=_("List all enabled plugins"))
		self.register_command("plugin", self.show_plugin_info, help=_("Show info about a specified plugin"), args="plugin_name")

	def show_info(self, message, keywords):
		self.bot.client.send_pm(message.channel, Format.color('darkblue') + Format.bold() + _("LuckyBot, an extendable IRC bot written in python. Version %s" % (luckybot.__version__)))
		self.bot.client.send_pm(message.channel, Format.color('darkblue') + _("Created by Lucas van Dijk. http://www.return1.net"))

	def list_plugins(self, message, keywords):
		self.bot.client.send_pm(message.nick, "%s%s%s" % (Format.color('darkblue'), Format.bold(), _("Plugin List")))
		
		i = 1
		for plugin_file, plugin in self.bot.plugins.plugins.iteritems():
			self.bot.client.send_pm(message.nick, "%s#%d %s" % (Format.color('darkblue'), i, plugin.plugin_info['name']))
			#time.sleep(0.3)
			i += 1
		
		self.bot.client.send_pm(message.nick, _("Use !plugin plugin_name to view more info about a plugin").replace('!', self.bot.settings.get('Bot', 'command_prefix')))

	def show_plugin_info(self, message, keywords):
		# Check if plugin exists
		plugin_obj = None
		
		if self.bot.plugins.plugins.has_key(message.bot_args):
			plugin_obj = self.bot.plugins.plugins[message.bot_args]
		else:
			for plugin_dir, plugin in self.bot.plugins.plugins.iteritems():
				if self.plugin_info['name'] == message.bot_args:
					plugin_obj = plugin
					break
		
		if plugin_obj != None:
			self.bot.client.send_pm(message.nick, Format.color('darkblue') + Format.bold() + plugin_obj.plugin_info['name'])
			
			if plugin_obj.plugin_info.has_key('description'):
				self.bot.client.send_pm(message.nick, plugin_obj.plugin_info['description'])
			
			if plugin_obj.plugin_info.has_key('authors'):
				self.bot.client.send_pm(message.nick, Format.color('darkblue') + "%s %s" % (_("Created By: "), ', '.join(plugin_obj.plugin_info['authors'])))
			
			if hasattr(plugin_obj, 'commands') and len(plugin_obj.commands) > 0:
				self.bot.client.send_pm(message.nick, Format.bold() + _("Plugin commands:"))
				for command, tuple in plugin_obj.commands.iteritems():
					
					callback, data = tuple
					str = Format.color('darkred') + self.bot.settings.get('Bot', 'command_prefix') + command
					
					if data.has_key('args'):
						str += " %s%s%s" % (Format.color('orange'), data['args'], Format.normal())
					
					if data.has_key('help'):
						str += " - %s%s" % (Format.color('darkblue'), data['help'])
						
					self.bot.client.send_pm(message.nick, str)
		else:
			self.bot.client.send_notice(message.nick, _("The specified plugin does not exists"))
			
		
		
	
