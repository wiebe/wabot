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
from gettext import gettext as _
from luckybot.bot.plugins import Plugin

class LastFMInfo(object):
	"""
		This class can be used to get Last.FM profile data
	"""
	
	def __init__(self, username):
		"""
			Initializes the class
			
			@type username: string
			@param username: The username of the profile you want to get data from
		"""
		
		self.username = username
	
	def _get_xml(self, url):
		"""
			Gets an Element object for the given URL
			
			@type url: string
			@param url: The url to fetch data from
			
			@rtype: elementtree.Element
			@return: An Element object
		"""
		
		data = urllib.urlopen(url)
		
		try:
			tree = ElementTree.ElementTree(file=data)
		finally:
			data.close()

		if not tree or tree == None:
			raise Exception, 'Could not parse XML'

		return tree.getroot()
	
	def now_playing(self):
		"""
			Gets the current listening track of this user
			
			@rtype: string
			@return: A string containing the artist an title, or False when there're no tracks
		"""
		elem = self._get_xml('http://ws.audioscrobbler.com/1.0/user/%s/recenttracks.xml' % self.username)
			
		track = elem.find('track')
			
		if not track or track == None:
			return False
				
		title = track.find('artist').text + " - " + track.find('name').text
		del elem
		
		return title;
	
	def get_top_tracks(self):
		tree = self._get_xml('http://ws.audioscrobbler.com/1.0/user/%s/toptracks.xml' % self.username)
		
		tracks = tree.findall('track')
		
		to_return = []
		i = 0
		while i < 5:
			to_return.append(tracks[i].find('artist').text + " - " + tracks[i].find('name').text + " (" + Format.color('red') + _("Playcount:") + " " + tracks[i].find('playcount').text + Format.normal() + ")")
			
			i += 1
		
		return to_return
	
	def get_top_artists(self):
		tree = self._get_xml('http://ws.audioscrobbler.com/1.0/user/%s/topartists.xml' % self.username)
		
		artists = tree.findall('artist')
		
		to_return = []
		i = 0
		while i < 5:
			to_return.append(artists[i].find('name').text + " (" + Format.color('red') + _("Playcount:") + " " + artists[i].find('playcount').text + Format.normal() + ")")
			
			i += 1
		
		return to_return
	
	def get_weekly_tracks(self):
		tree = self._get_xml('http://ws.audioscrobbler.com/1.0/user/%s/weeklytrackchart.xml' % self.username)
		
		tracks = tree.findall('track')
		
		to_return = []
		i = 0
		while i < 5:
			to_return.append(tracks[i].find('artist').text + " - " + tracks[i].find('name').text + " (" + Format.color('red') + _("Playcount:") + " " + tracks[i].find('playcount').text + Format.normal() + ")")
			
			i += 1
		
		return to_return
		
class LastFMPlugin(Plugin):
	def initialize(self):
		self.register_command('lastfm', self.on_lastfm, help=_("Get some last.fm data. The optional 'data' argument can contain the following values: tracks, artists, weekly, which will get the top overall tracks, top overall artists or the weekly top tracks"), args="nick [data]")	
	
	def on_lastfm(self, message, keywords):
		# Check which mode
		args = message.bot_args.split(' ')
		
		if len(args) > 1:
			if args[1] == 'tracks':
				self.send_top_tracks(args[0], message)
			elif args[1] == 'artists':
				self.send_top_artists(args[0], message)
			elif args[1] == 'weekly':
				self.send_weekly_top(args[0], message)
			else:
				self.bot.client.send_notice(message.nick, _("Invalid argument, use 'tracks', 'artists' or 'weekly'"))
		elif len(args) == 1:
			self.send_now_playing(args[0], message)
		else:
			self.bot.client.send_notice(message.nick, _("No username specified"))

	def send_now_playing(self, user, message):
		lastfm = LastFMInfo(user)
		try:
			title = lastfm.now_playing()
		except:
			import traceback
			traceback.print_exc()
			self.bot.client.send_pm(message.channel, _("Could not load data, probably the user doesn't exists"))
		else:
			if title == False:
				self.bot.client.send_pm(message.channel, _("No track currently playing"))
			else:
				self.bot.client.send_pm(message.channel, Format.color('darkblue') + Format.bold() + _('[%s] Last.FM Now Playing:%s %s') % (user, Format.bold(), title))
		
		del lastfm

	def send_top_tracks(self, user, message):
		lastfm = LastFMInfo(user)
		
		try:
			tracks = lastfm.get_top_tracks()
		except:
			import traceback
			traceback.print_exc()
			self.bot.client.send_pm(message.channel, _("Could not load data, probably the user doesn't exists"))
		else:
			if len(tracks) == 0:
				self.bot.client.send_pm(message.channel, _("No top tracks available"))
			else:
				self.bot.client.send_pm(message.channel, Format.color('darkblue') + Format.bold() + _("Top tracks from %s") % user)
				
				i = 1
				for track in tracks:
					self.bot.client.send_pm(message.channel, Format.bold() + str(i) + ". " + Format.bold() + track)
					i += 1
					
	def send_top_artists(self, user, message):
		lastfm = LastFMInfo(user)
		
		try:
			artists = lastfm.get_top_artists()
		except:
			import traceback
			traceback.print_exc()
			self.bot.client.send_pm(message.channel, _("Could not load data, probably the user doesn't exists"))
		else:
			if len(artists) == 0:
				self.bot.client.send_pm(message.channel, _("No top artists available"))
			else:
				self.bot.client.send_pm(message.channel, Format.color('darkblue') + Format.bold() + _("Top artists from %s") % user)
				
				i = 1
				for artist in artists:
					self.bot.client.send_pm(message.channel, Format.bold() + str(i) + ". " + Format.bold() + artist)
					i += 1

	def send_weekly_top(self, user, message):
		lastfm = LastFMInfo(user)
		
		try:
			tracks = lastfm.get_weekly_tracks()
		except:
			import traceback
			traceback.print_exc()
			self.bot.client.send_pm(message.channel, _("Could not load data, probably the user doesn't exists"))
		else:
			if len(tracks) == 0:
				self.bot.client.send_pm(message.channel, _("No top tracks available"))
			else:
				self.bot.client.send_pm(message.channel, Format.color('darkblue') + Format.bold() + _("Weekly top tracks from %s") % user)
				
				i = 1
				for track in tracks:
					self.bot.client.send_pm(message.channel, Format.bold() + str(i) + ". " + Format.bold() + track)
					i += 1
	
