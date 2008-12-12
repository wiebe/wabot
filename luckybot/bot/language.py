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

from ConfigParser import SafeConfigParser

class Language:
	def __init__(self, language, defaults = {}):
		self.language = language.lower()
		self.parser = SafeConfigParser(defaults)
	
	def read_language(self, path):
		"""
			Reads the language of an ini file
		"""
		
		self.parser.read(path)
	
	def add_defaults(self, defaults):
		for key, value in defaults.iteritems():
			self.parser.set('english', key, value)
	
	def get(self, key, vars = {}):
		"""
			Gets the value of a specified language entry
		"""
		if self.parser.has_section(self.language):
			if self.parser.has_option(self.language, key):
				if len(vars) != 0:
					return self.parser.get(self.language, key, False, vars)
				else:
					return self.parser.get(self.language, key, True)
		elif self.parser.has_section('english'):
			if self.parser.has_option('english', key):
				if len(vars) != 0:
					return self.parser.get('english', key, False, vars)
				else:
					return self.parser.get('english', key, True)
		
		return False
			
	
		
			
		
