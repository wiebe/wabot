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

import luckybot.views.base
import luckybot.luckynet.connection as connection
import socket
import gobject

class ConsoleView(luckybot.views.base.BaseView):
	"""
		This view displays all in and out coming data in console
	"""
	
	def __init__(self):
		self.loop= gobject.MainLoop()
	
	def get_connection(self):
		return connection.GlibConnection(socket.AF_INET, socket.SOCK_STREAM)
	
	def data_in(self, data):
		print "<<< ", data.strip()
	
	def data_out(self, data):
		print ">>> ", data.strip()
	
	def data_other(self, data):
		print "<o> ", data
	
	def error(self, data):
		print "ERROR: ", data
	
	def on_close(self):
		self.data_other("Connection closed")
		self.loop.quit()
	
	def start(self):
		self.bot.plugins.load_plugins(luckybot.path.get_base_path('plugins'))
		self.bot.plugins.load_plugins(luckybot.path.get_personal_file('plugins'))
		
		self.bot.connect_to_server()
		self.loop.run()
		
