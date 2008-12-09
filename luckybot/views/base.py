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

class BaseView(object):
	"""
		The 'view' of the bot, subclasses should display the data 
		on the screen
	"""
		
	def get_connection(self):
		raise NotImplementedError
	
	def data_in(self, data):
		pass
	
	def data_out(self, data):
		pass
	
	def data_other(self, data):
		pass
		
	def error(self, data):
		pass
	
	def start(self):
		pass
	
	def on_close(self):
		pass
	
	def set_bot(self, bot):
		self.bot = bot
		self.start()
	
