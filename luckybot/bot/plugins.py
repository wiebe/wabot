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

import sys
import os
import re 
import luckybot.path as path
from luckybot.language import Language
from ConfigParser import SafeConfigParser

REGEXP_RAW = 1
REGEXP_MESSAGE = 2

class PluginException(Exception):
	pass

class Plugin(object):
	"""
		This class represents a (loaded) plugin
	"""
	
	_instance = None
	
	def __init__(self, manager, plugins_dir, dirname):
		self.plugins_dir = plugins_dir
		self.dirname = dirname
		self.manager = manager
		self.bot = manager.bot
		
		self.lang = Language(self.bot.settings.get('Bot', 'language'))
		
	def load(self):	
		"""
			(Re)Loads the module instance of this plugin
		"""
		
		if hasattr(self, 'commands'):
			del self.commands
			
		if hasattr(self, 'regexps'):
			del self.regexps
			
		if hasattr(self, 'message_handler'):
			del self.message_handler
			
		self.commands = {}		
		self.regexps = []
		self.message_handler = None

		oldpath = sys.path
		
		try:
			if self.dirname in sys.modules:
				del sys.modules[self.dirname]
				
			sys.path.insert(0, self.plugins_dir)
			self._instance = __import__(self.dirname)
		
			if not self._instance or self._instance == None:
				raise PluginException, 'Could not load plugin', self.dirname
		finally:
			sys.path = oldpath
		
		# read plugin meta data
		self.plugin_info = self._read_metadata()
		self.plugin_info['dirname'] = self.dirname
		
		self._load_language()
		
		self._instance.plugin = self

		if hasattr(self._instance, 'initialize'):
			self._instance.initialize()
	
	def _load_language(self):
		"""
			Checks if the plugin has a language file, and reads it, 
			if there's one
		"""
		
		if os.path.exists(os.path.join(self.plugins_dir, self.dirname, 'language.ini')):
			self.lang.read_language(os.path.join(self.plugins_dir, self.dirname, 'language.ini'))
		
	def unload(self):
		"""
			Unloads the plugin
		"""
		
		if hasattr(self._instance, 'destroy'):
			self._instance.destroy()		
		
		del self.commands
		del self.regexps
		del self.message_handler
		del self.plugin_info
		
		del self._instance
		
	
	def _read_metadata(self):
		"""
			Reads some info about the plugin in the plugininfo file
		
			@rtype: dict
			@return: Dictionary containing all keys and values
		"""
		
		if not os.path.exists(os.path.join(self.plugins_dir, self.dirname, 'plugininfo')):
			raise PluginException, 'Plugin does not have a plugininfo file', self.dirname
		
		f = open(os.path.join(self.plugins_dir, self.dirname, 'plugininfo'))
		infodict = {}
		for line in f:
			try:
				key, val = line.split("=",1)
				infodict[key.strip().lower()] = eval(val)
			except ValueError:
				pass # this happens on blank lines
		return infodict
	
	def register_command(self, name, callback, **keywords):
		"""
			Register a new bot command
			
			@type name: string
			@param name: The name of the command
			
			@type callback: function
			@param callback: The function to call when the command is used
			
			@type keywords: dictionary
			@param keywords: List of extra data you want to give with. Special keywords are:
				help: A short string explaining the command
				args: List of arguments
		"""
		
		if name in self.commands:
			return
		
		self.commands[name] = (callback, keywords)
		self.manager.register_command(name, self.dirname)
	
	def register_regexp(self, regexp, type, callback, userdata = None):
		"""
			Register a new regular expression to match against the incoming data or user message
			
			@type regexp: string
			@param regexp: The regular expression I{object} which will be used for matching
			
			@type type: int
			@param type: Where to match against: The Data (REGEXP_RAW) our the user message (REGEXP_MESSAGE)
			
			@type callback: function
			@param callback: The function to call when the regexp matches
			
			@param userdata: Any object you want to give with the callback
		"""
		
		self.regexps.append((regexp, type, callback, userdata))
		self.manager.register_regexp(self.dirname)
	
	def register_message_handler(self, callback):
		"""
			Registers a 'message handler', the given function will be called on EACH server and/or channel
			message, allowing the plugin to check for JOIN/PART/QUIT and other events.
			
			@type callback: function
			@param callback: The function to call when we receive a server/channel message
		"""
		
		self.message_handler = callback
		self.manager.register_message_handler(self.dirname)
	
	def call(self, name, message):
		"""
			Call the the command callback
			
			@type name: string
			@param name: The command name
			
			@rtype: bool
			@return: True when the command exists, else false
		"""
		
		if name in self.commands:
			callback, keywords = self.commands[name]
			
			callback(message, keywords)
			return True
		else:
			return False
		

class Manager(object):
	"""
		This class handles everything related to plugins.
		Registering of bot commands, regexp hooking, 
		calling and loading plugins.
	"""
	
	def __init__(self, bot):
		self.bot = bot
		self.commands = {}
		self.regexps = []
		self.message_handlers = []
		self.plugins = {}
		self.dirs = []
	
	def register_command(self, name, plugin_name):
		"""
			Register command with the plugin manager
			
			@type name: string
			@param name: The command name
			
			@type plugin_name: string
			@param plugin_name: The plugin directory name
		"""
		
		if not name in self.commands:
			self.commands[name] = []
		
		try:
			self.commands[name].index(plugin_name)
		except Exception, e:
			self.commands[name].append(plugin_name)
	
	def register_regexp(self, plugin_name):
		"""
			Register a new regular expression to match against the incoming data or user message
			
			@type plugin_name: string
			@param plugin_name: The directory name of the plugin
		"""
		
		try:
			self.regexps.index(plugin_name)
		except:
			self.regexps.append(plugin_name)
			
	def register_message_handler(self, plugin_name):
		"""
			Registers a 'message handler', the given function will be called on EACH server and/or channel
			message, allowing the plugin to check for JOIN/PART/QUIT and other events.
			
			@type plugin_name: string
			@param plugin_name: The directory name of the plugin
		"""
		
		try:
			self.message_handler.index(plugin_name)
		except:
			self.message_handlers.append(plugin_name)
	
	def check_data(self, message):
		"""
			Checks incoming data for matching regexps or commands
			
			@type message: sockets.protocols.irc.ServerMessage
			@param message: A server or channel message object, containing all data
		"""
		
		if self.regexps:
			for plugin in self.regexps:
				if plugin in self.plugins:
					for tuple in self.plugins[plugin].regexps:
						regexp, type, callback, userdata = tuple
				
						if type == REGEXP_RAW:
							match = regexp.match(message.raw)
						else:
							match = regexp.match(message.message)
						
						if match:
							callback(message, match, userdata) 
		
		if self.message_handlers:
			for plugin_name in self.message_handlers:
				if self.plugins.has_key(plugin_name):
					self.plugins[plugin_name].message_handler(message)
		
		if hasattr(message, 'bot_command'):			
			if message.bot_command in self.commands:
				for plugin_name in self.commands[message.bot_command]:
					self.plugins[plugin_name].call(message.bot_command, message)
						
					
	
	def load_plugins(self, dir):
		"""
			Loads plugins in a specified directory
			
			@type dir: string
			@param dir: The directory to read
		"""

		if not os.path.isdir(dir):
			return
		
		# Get enabled plugins
		plugins = self.bot.settings.items('Disabled')
		disabled = []
		for tuple in plugins:
			plugin, disable = tuple
			if disable:
				disabled.append(plugin)
		
		for file in os.listdir(dir):				
			if file[0] == '_' or file[0] == '.' or not os.path.isdir(os.path.join(dir, file)):
				continue
			
			self.load_plugin(dir, file)
		
		self.dirs.append(dir)
	
	def load_plugin(self, dir, name):
		"""
			loads a given plugin in a specified Direcotory
			
			@type dir: string
			@param dir: The directory where the plugin dir lies in
			
			@type name: string
			@param name: The name of the plugin directory
			
			@rtype: bool
			@return: True on success else false
		"""
		
		if not os.path.isdir(os.path.join(dir, name)):
			return False
		
		try:
			plugin = Plugin(self, dir, name)
			plugin.load()
		except Exception, e:
			import traceback
			traceback.print_exc()
			self.bot.view.error('Could not load plugin %s' % name)
			return False
		
		self.plugins[name] = plugin	
		return True	
	
	def unload_plugins(self):
		"""
			Unloads all loaded plugins
		"""
		
		for name, plugin in self.plugins.iteritems():
			self.unload_plugin(name)
	
	def unload_plugin(self, name):
		"""
			Unloads the specified plugin
			
			@type name: string
			@param name: The plugin name (directory name)
			
			@rtype: bool
			@return: True on success, else false
		"""
		
		if not name in self.plugins:
			got_plugin = False
			for plugin in self.plugin:
				if name == plugin.plugin_info['name']:
					name = plugin.dirname
					got_plugin = True
					break
			
			if got_plugin == False:	
				name = False
		
		if name == False:
			return False
		
		# Remove registered commands/regexps/handlers
		try:
			self.regexps.remove(name)
			self.message_handlers.remove(name)
		except:
			pass
		
		for command, plugin_list in self.commands.iteritems():
			try:
				plugin_list.remove(name)
			except:
				pass
		
		self.plugins[name].unload()
		del self.plugins[name]
		
		return True
	
	def reload_plugins(self):
		"""
			Reloads all loaded plugins
			
			@rtype: bool
			@return: True on success else false
		"""
		
		success = True
		
		if self.plugins:
			for name, plugin in self.plugins.iteritems():
				if not self.reload_plugin(name) and succes == True:
					success = False
		
		return success
		
	def reload_plugin(self, name):
		"""
			Reloads a given plugin
			
			@rtype: bool
			@return: True on success else false
		"""
		
		succes = False
		
		if name in self.plugins:
			plugins_dir = self.plugins[name].plugins_dir
			if self.unload_plugin(name) and self.load_plugin(plugins_dir, name):
				succes = True
		
		return succes
	
	def __del__(self):
		self.unload_plugins()	
		
