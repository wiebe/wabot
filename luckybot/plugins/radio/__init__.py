#
# Radio plugin
# (c) Copyright 2008 by Wiebe Verweij
# http://wiebelt.nl
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
import xml.etree.cElementTree as ElementTree
import urllib2 as urllib
import string
from string import Template
from luckybot.bot.plugins import Plugin
from luckybot.luckynet.protocols.irc import Format

#		
# RadioPlugin
#
class RadioPlugin(Plugin):
	
	def initialize(self):
		# Register commands
		self.register_command('3fm', self.on_3fm, help=_('Laat zien welk nummer er nu op 3FM word gedraaid.'))
		self.register_command('538', self.on_538, help=_('Laat zien welk nummer er nu op Radio 538 word gedraaid.'))
		self.register_command('caz', self.on_caz, help=_('Laat zien welk nummer er nu op Caz word gedraaid.'))
		self.register_command('qmusic', self.on_qmusic, help=_('Laat zien welk nummer er nu op Qmusic word gedraaid.'))
		self.register_command('slamfm', self.on_slamfm, help=_('Laat zien welk nummer er nu op SlamFM word gedraaid.'))
		
		# Load model and view
		self.model = Model()
		self.view = View()
		
	
	def on_3fm(self, message, keywords):
		# Get data
		data = self.model.get_3fm()
		
		# Format
		msg = self.view.format_3fm(data['artist'], data['title'], data['program'])
		
		# Send the message
		self.bot.client.send_pm(message.channel, msg)
		
	def on_538(self, message, keywords):
		# Get data
		data = self.model.get_538()
		
		# Format
		msg = self.view.format_538(data['artist'], data['title'], data['program'], data['dj'])
		
		# Send the message
		self.bot.client.send_pm(message.channel, msg)
		
	def on_caz(self, message, keywords):
		pass
		
	def on_qmusic(self, message, keywords):
		pass
		
	def on_slamfm(self, message, keywords):
		pass
		

#
# Model
#
class Model(object):

	def get_xml(self, url):
		data = urllib.urlopen(url, 15)
		contents = data.read()	
		contents = contents.replace('&', '&amp;')		
		tree = ElementTree.fromstring(contents)
		
		return tree
		
	def get_3fm(self):
		# Music feed
		m_feed = self.get_xml('http://www.3fm.nl/page/xml_daletfeed')
		
		# Program feed
		p_feed = self.get_xml('http://www.3fm.nl/page/xml_onairfeed')
		
		# Get music data
		artist = m_feed.find('artist').text
		title = m_feed.find('title').text
		
		# Get program data
		program = p_feed.find('program').text
		link = p_feed.find('programlink').text
		
		return {'artist': artist, 'title': title, 'program': program, 'link': link}
		
	def get_538(self):
		# Music feed
		m_feed = self.get_xml('http://stream.radio538.nl/538play/nowplaying.xml')
		
		# Program feed
		p_feed = self.get_xml('http://stream.radio538.nl/xml/onair_538.xml')
		
		# Get music data
		artist = m_feed.find('artist').text
		title = m_feed.find('title').text
		
		# Get program data
		program = p_feed.find('showname').text
		dj = p_feed.find('djname').text
		
		return {'artist': artist, 'title': title, 'program': program, 'dj': dj}
		
	def get_caz(self):
		pass
		
	def get_qmusic(self):
		pass
		
	def get_slamfm(self):
		pass

#
# View
#
class View(object):

	def format_3fm(self, artist, title, program):
		# None naar Onbekend :)
		if artist == None:
			artist = 'Onbekend'
		
		if title == None:
			title = 'Onbekend'
			
		if program == None: 
			program = 'Onbekend'
			
		# Capitalize
		artist = string.capwords(artist)
		title = string.capwords(title)
		
		# Make the message
		msg = Template('[$c 3FM $n| Now playing:$c $artist $n-$c $title $n | Program:$c $program $n]')
		msg = msg.substitute(c = Format.color('red'), n = Format.normal(), artist = artist, title = title, program = program)		
		
		return msg
		
	def format_538(self, artist, title, program, dj):
		msg = Template('[$c 538 $n| Now playing:$c $artist $n-$c $title $n | Program:$c $program $n | DJ:$c $dj $n]')
		msg = msg.substitute(c = Format.color('red'), n = Format.normal(), artist = artist, title = title, program = program, dj = dj)
		pass
		
	def format_caz(self, artist, title, program):
		pass
		
	def format_qmusic(self, artist, title, program):
		pass
		
	def format_slamfm(self, artist, title, program):
		pass