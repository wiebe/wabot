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

from luckybot.luckynet.protocols.irc import Format
from pysqlite2 import dbapi2 as sqlite
import math
import re

class RssException(Exception):
	pass

class RssFeed(object):
	"""
		Reads RSS feeds
	"""
	
	def __init__(self, url):
		self.url = url
	
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
	
	def parse(self, max = 5):
		xml = self._get_xml(self.url)
		self.title = xml.find('channel').find('title').text
		
		self.items = []
		
		items = xml.find('channel').findall('item')
		
		i = 0
		while i < math.min(max, len(items)):
			item = {
				'title': items[i].find('title').text,
				'description': items[i].find('description').text,
				'link': items[i].find('link').text
			}
			
			self.items.append(item)
			i += 1
	
	def __iter__(self):
		return iter(self.items)
		
class RssPlugin(object):
	"""
		Class which handles the plugin commands etc
	"""
	
	def __init__(self):
		# Setup database connection
		self.connection = sqlite.connect(os.path.join(plugin.plugins_dir, plugin.dirname, 'rss.db'))
	
	def _validate_url(self, url):
		regexp = re.compile('^(ftp|https?):\/\/([^:]+:[^@]*@)?([a-zA-Z0-9][-_a-zA-Z0-9]*\.)*([a-zA-Z0-9][-_a-zA-Z0-9]*){1}(:[0-9]+)?\/?(((\/|\[|\]|-|~|_|\.|:|[a-zA-Z0-9]|%[0-9a-fA-F]{2})*)\?((\/|\[|\]|-|~|_|\.|,|:|=||\{|\}|[a-zA-Z0-9]|%[0-9a-fA-F]{2})*\&?)*)?(#([-_.a-zA-Z0-9]|%[a-fA-F0-9]{2})*)?$')
		return regexp.match(url) != False
		
	def read_url(self, message, keywords):
		# Check URL
		if not self._valudate_url(message.bot_args):
			raise RssException, plugin.lang('invalid_url')
		
		rss = RssFeed(message.bot_args)
		rss.parse(5)
		
		plugin.bot.connection.send_pm(message.channel, Format.color('darkblue') + Format.bold() + rss.title)
		for item in rss:
			send = "[ %s%s%s ] - %s" % (Format.color('red'), item['link'], Format.normal(), item['title'])
			plugin.bot.connection.send_pm(message.channel, send)
	
	def __del__(self):
		self.connection.close()
		
			
		

def initialize():
	#plugin.register_command('rss', display_feed, help=_("Display the last entries of a given feed name or URL"), args="name|url")
	#plugin.register_command('addfeed', add_feed, help=_("Add a feed"), args="name url")
	pass
	
