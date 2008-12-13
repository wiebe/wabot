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
	from xml.etree import ElementTree
except ImportError:
	try:
		from elementtree import ElementTree
	except ImportError:
		raise
		
import urllib2 as urllib
from luckybot.luckynet.protocols.irc import Format
from luckybot.bot.plugins import Plugin

def get_xml(url):
	data = urllib.urlopen(url)
	contents = data.read()
	
	contents = contents.replace('&', '&amp;')
	tree = ElementTree.fromstring(contents)
	
	return tree

class BaseRadio(object):	
	@classmethod
	def get_radio(self, name):
		classes = self.__subclasses__()
		for subclass in classes:
			if subclass.__name__.lower() == ('radio_%s' % name).lower():
				return subclass()

		return False
		
	def now_playing(self):
		raise NotImplementedError
	
	def get_stream_url(self):
		raise NotImplementedError

class Radio_538(BaseRadio):	
	def now_playing(self):
		root = get_xml('http://stream.radio538.nl/538play/nowplaying.xml')
				
		artist = root.find('now').find('artist').text
		
		if not artist or len(artist) == 0:
			artist = root.find('previous').find('artist').text
			title = root.find('previous').find('title').text
			previous = True
		else:
			title = root.find('now').find('title').text
			previous = False
		
		return (artist.lower().title(), title.lower().title())
	
	def get_stream_url(self):
		return 'http://82.201.100.9:8000/radio538.m3u'

class Radio_SlamFM(BaseRadio):	
	def now_playing(self):
		root = get_xml('http://www.slamfm.nl/slamfm/nowonair/Onair.XML')
				
		artist = root.find('Current').find('artistName').text
		title = root.find('Current').find('titleName').text
		
		return (artist, title)
	
	def get_stream_url(self):
		return 'http://nl.sitestat.com/slamfm/slam/s?slam.luister.itunes_winamp&ns_type=clickin'

class Radio_3fm(BaseRadio):
	def now_playing(self):
		root = get_xml('http://www.3fm.nl/page/xml_daletfeed')
		
		artist = root.find('artist').text
		title = root.find('title').text
		
		artist = artist or ""
		title = title or ""
		
		return (artist.lower().title(), title.lower().title())
	
	def get_stream_url(self):
		return 'http://cgi.omroep.nl/cgi-bin/shoutcastlive.pls?radio3live'

class RadioPlugin(Plugin):

def initialize():
	plugin.register_command('radio', get_radio_np, help="Geeft wat er nu speelt op een bepaalde radio", args="radio_name")
	plugin.register_command('radiolist', show_radio_list, help="Geeft een lijst van beschikbare radio stations")

def get_radio_np(message, keywords):
	radio = BaseRadio.get_radio(message.bot_args)
	
	if not radio == False:
		np = radio.now_playing()
		plugin.bot.client.send_pm(message.channel, Format.color('darkblue') + Format.bold() + ("[%s]" % message.bot_args.lower().title()) + " " + Format.normal() + Format.bold() + ("%s - %s" % np))
	else:
		plugin.bot.client.send_pm(message.channel, "Radio bestaat niet")
		
def show_radio_list(message, keywords):
	classes = BaseRadio.__subclasses__()
	
	plugin.bot.client.send_pm(message.nick, Format.color('darkblue') + Format.bold() + "Beschikbare radio stations")
	for subclass in classes:
		plugin.bot.client.send_pm(message.nick, subclass.__name__.lower().replace('radio_', '').title())
	
	plugin.bot.client.send_pm(message.nick, Format.bold() + "Typ %sradio [naam] om te kijken welk liedje er nu draait" % (plugin.bot.settings.get('Bot', 'command_prefix')))
	
		
	
	
