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

from datetime import datetime, timedelta

class Manager(object):
	"""
		This class handles authenticating bot admins
	"""
	
	def __init__(self):
		"""
			Initializes the object
		"""
		
		self.logged_in = {}
	
	def check_logged_in(self, nick):
		"""
			Checks if a given nickname is logged in
			
			@type nick: string
			@param nick: The nickname you want to check
			
			@rtype: bool
			@return: True when logged in else false
		"""
		if nick.lower() in self.logged_in and self.logged_in[nick.lower()] + timedelta(minutes = 120) > datetime.now():
			self.update_session(nick.lower())
			return True
		else:
			return False
	
	def log_in(self, nick):
		"""
			Log a given nickname in
			
			@type nick: string
			@param nick: The nickname
		"""
		
		self.logged_in[nick.lower()] = datetime.now()
	
	def log_out(self, nick):
		"""
			Log a given nickname out
			
			@type nick: string
			@param nick: The nickname
			
			@rtype: bool
			@return: True on success else false
		"""
		
		if self.logged_in.has_key(nick.lower()):
			del self.logged_in[nick.lower()]
			
			return True
		else:
			return False
	
	def update_session(self, nick):
		"""
			Updates the session (last action of this user), so it will be logged
			out after his last activity
			
			@type nick: string
			@param nick: The nickname
			
			@rtype: bool
		"""
		
		if self.logged_in.has_key(nick.lower()):
			self.logged_in[nick.lower()] = datetime.now()
		else:
			return False
