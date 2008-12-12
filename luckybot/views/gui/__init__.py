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

try:
	import pygtk
	pygtk.require('2.4')
except:
	pass

try:
	import gtk
	import gobject
	import gtk.glade
except:
	raise

import luckybot.views.base
import os
import socket
import luckybot.path
from luckybot.luckynet.connection import GlibConnection
from gettext import gettext as _

gtk.gdk.threads_init()

class GUIView(luckybot.views.base.BaseView, gobject.GObject): 
	"""
		This class represents the main LuckyBot window
	"""
	
	def __init__(self):
		"""
			Loads and shows the window
		"""
		
		gobject.GObject.__init__(self)
		
		self.xml = gtk.glade.XML(luckybot.path.get_base_path('data', 'glade', 'mainwindow.glade'), 'mainWindow', 'luckybot')
		self.window = self.xml.get_widget('mainWindow')
		
		self.window.set_title(_("Lucky Bot"))
		
		self.xml.signal_autoconnect(self)
		self.window.show()
		self.window.connect('destroy', self.on_quit)
		
		self.connected = False
		
	def set_defaults(self):
		"""
			Reads settings, and sets some textboxes to the current
			settings
		"""
		
		self.xml.get_widget('txtServer').set_text(self.bot.settings.get('Server', 'hostname'))
		self.xml.get_widget('txtPort').set_text(self.bot.settings.get('Server', 'port'))
		self.xml.get_widget('txtChannel').set_text(self.bot.settings.get('Server', 'channels'))
	
	def get_connection(self):
		"""
			Returns the type of connection used for this view
			
			@rtype: GlibConnection
		"""
		
		return GlibConnection(socket.AF_INET, socket.SOCK_STREAM)	
	
	def on_close(self):
		self.connected = False
		self.toggle_connect_button()
		self.data_other("Connection closed")
		
	def toggle_connect_button(self):
		"""
			This function changes the 'connect' menu item and 'connect' button 
			to 'disconnect' when they click it and reverse
		"""
		
		if self.connected:
			for child in self.xml.get_widget('menuConnect').get_children():
				if isinstance(child, gtk.AccelLabel):
					child.set_text(_('Disconnect'))
		
			self.xml.get_widget('menuConnect').set_image(gtk.image_new_from_stock(gtk.STOCK_DISCONNECT, gtk.ICON_SIZE_MENU))
			self.xml.get_widget('btnConnect').set_label(_('Disconnect'))
		else:
			for child in self.xml.get_widget('menuConnect').get_children():
				if isinstance(child, gtk.AccelLabel):
					child.set_text(_('Connect'))
					
			self.xml.get_widget('menuConnect').set_image(gtk.image_new_from_stock(gtk.STOCK_CONNECT, gtk.ICON_SIZE_MENU))
			self.xml.get_widget('btnConnect').set_label(_('Connect'))
		
	
	def send_command(self, widget = None, event = None):
		"""
			Sends the command given in the textbox
		"""
		
		text = self.xml.get_widget('txtCommand').get_text()
		
		if len(text) == 0:
			return
		
		self.bot.client.send(text)
		self.xml.get_widget('txtCommand').set_text('')
	
	def do_connect(self, widget = None, event = None):
		"""
			Connects to the given server
		"""
		if self.connected:
			self.bot.client.connection.close()
			self.connected = False
			self.toggle_connect_button()
		else:			
			server = self.xml.get_widget('txtServer').get_text()
			port = int(self.xml.get_widget('txtPort').get_text())
			channel = self.xml.get_widget('txtChannel').get_text()
			
			if len(server) == 0 or len(channel) == None:
				return
			
			self.bot.connect_to_server(server, port)
			
			self.bot.settings.set('Server', 'channels', channel)
			
			self.connected = True		
			self.toggle_connect_button()
	
	def on_quit(self, widget = None, event = None):
		"""
			Quits the bot and window
		"""
		self.window.hide()
		gtk.main_quit()
		
		if hasattr(self.bot, 'client') and self.bot.client != None:
			try:
				self.bot.client.connection.close()
			except:
				pass
			
	
	def data_in(self, data):
		"""
			Adds incoming data to the textview
			
			@type data: string
			@param data: The data to add
		"""
		
		textview = self.xml.get_widget('txtLog')
		buffer = textview.get_buffer()
		
		buffer.insert(buffer.get_end_iter(), "<<< %s" % data)
		textview.scroll_to_mark(buffer.get_insert(), 0)
	
	def data_out(self, data):
		"""
			Adds outgoing data to the textview
			
			@type data: string
			@param data: The data to add
		"""
		
		textview = self.xml.get_widget('txtLog')
		buffer = textview.get_buffer()
		
		buffer.insert(buffer.get_end_iter(), ">>> %s" % data)
		textview.scroll_to_mark(buffer.get_insert(), 0)
	
	def data_other(self, data):
		"""
			Adds other data to the textview
			
			@type data: string
			@param data: The data to add
		"""
		
		textview = self.xml.get_widget('txtLog')
		buffer = textview.get_buffer()
		
		buffer.insert(buffer.get_end_iter(), "<o> %s" % data)
		textview.scroll_to_mark(buffer.get_insert(), 0)
	
	def error(self, data):
		"""
			Called when an error occurs
			
			@type data: string
			@param data: The data to add
		"""
		
		dialog = gtk.MessageDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, data)
		dialog.run()
		dialog.hide()
		
	def start(self):
		"""
			Starts the view
		"""		
		
		self.bot.plugins.load_plugins(luckybot.path.get_base_path('plugins'))
		self.bot.plugins.load_plugins(luckybot.path.get_personal_file('plugins'))
		
		# Set Defaults
		self.set_defaults()
		
		gtk.main()
	
	
		
