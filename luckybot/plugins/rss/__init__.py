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

from luckybot.bot.plugins import Plugin
from luckybot.luckynet.protocols.irc import Format
from pysqlite2 import dbapi2 as sqlite
import re
import os
import urllib2 as urllib

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
		while i < min(max, len(items)):
			item = {
				'title': items[i].find('title').text,
				'description': items[i].find('description').text,
				'link': items[i].find('link').text
			}
			
			self.items.append(item)
			i += 1
	
	def __iter__(self):
		return iter(self.items)
		
class RssPlugin(Plugin):
	"""
		Class which handles the plugin commands etc
	"""
	
	def initialize(self):
		# Register commands
		self.register_command('rss', self.read_feed, help="Display the last entries of a given feed name or URL", args="name|url")
		self.register_command('addfeed', self.add_feed, help="Add a feed", args="name url")
		self.register_command('reviewfeed', self.review_feeds, help="View unreviewed feeds or review a feed", args="(id yes|no)")
		
		# Setup database connection
		self.connection = sqlite.connect(os.path.join(self.plugins_dir, self.dirname, 'rss.db'))
		
		cursor = self.connection.cursor()
		
		sql = """
		CREATE TABLE IF NOT EXISTS feeds (
			id integer NOT NULL PRIMARY KEY,
			name varchar(50),
			url varchar(255),
			moderated integer(1) default 0
		);
		"""
		
		cursor.execute(sql)
		self.connection.commit()
		cursor.close()
	
	def _validate_url(self, url):
		regexp = re.compile('([\w]+?://[\w\#$%&~/.\-;:=,?@\[\]+]*)$')
		return regexp.match(url) != None
		
	def read_feed(self, message, keywords):	
		try:	
			url = Format.remove(message.bot_args)
			
			# Check URL
			if not self._validate_url(url):
				url = self.get_url(url)
				if url == None:
					raise RssException, self.lang.get('not_found')
			
			rss = RssFeed(url)
			rss.parse(5)
			
			self.bot.client.send_pm(message.channel, Format.color('darkblue') + Format.bold() + rss.title)
			for item in rss:
				send = "[ %s%s%s ] - %s" % (Format.color('red'), item['link'], Format.normal(), item['title'])
				self.bot.client.send_pm(message.channel, send)
		except RssException, error:
			self.bot.client.send_pm(message.channel, error)
	
	def get_url(self, name):
		cursor = self.connection.cursor()
		cursor.execute('SELECT url FROM feeds WHERE name = ? AND moderated = 1 LIMIT 1', (name,))
		
		try:
			row = cursor.fetchone()
		except StopIteration:
			row = None
		finally:
			self.connection.commit()
			cursor.close()
		
		return None if row == None else row[0]
	
	def add_feed(self, message, keywords):
		try:	
			args = message.bot_args.split(' ', 1)
			
			url = Format.remove(args[1])
			# Check URL
			if not self._validate_url(url):
				raise RssException, self.lang.get('invalid_url')
			
			name = Format.remove(args[0])
			
			regexp = re.compile('^[a-zA-Z0-9\-_.]+$')
			if not regexp.match(name):
				raise RssException, self.lang.get('invalid_name')
			
			cursor = self.connection.cursor()
			cursor.execute('INSERT INTO feeds (name, url) VALUES (?, ?)', (name, url))
			self.connection.commit()
			cursor.close()
			
			self.bot.client.send_notice(message.nick, self.lang.get('feed_added'))
		except RssException, error:
			self.bot.client.send_pm(message.channel, error)
	
	def review_feeds(self, message, keywords):
		if not self.bot.auth.check_logged_in(message.nick):
			self.bot.client.send_notice(message.nick, self.lang.get('access_denied'))
			return
		
		args = message.bot_args.split()
		
		if len(args) == 0:
			# Display a list of unreviewed feeds
			cursor = self.connection.cursor()
			cursor.execute('SELECT * FROM feeds WHERE moderated = 0 ORDER BY id ASC')
			
			self.bot.client.send_notice(message.nick,  \
				Format.color('darkblue') + Format.bold() +  \
				self.lang.get('unreviewed_feeds'))
			for row in cursor:
				self.bot.client.send_notice(message.nick, \
					"%s%s:%s %d %s%s:%s %s" % (Format.bold(),
						self.lang.get('id'), Format.bold(), int(row[0]),
						Format.bold(), self.lang.get('url'), 
						Format.bold(), row[2]
					)
				)
		elif len(args) == 2:
			if not args[0].isdigit():
				self.bot.client.send_notice(message.nick, self.lang.get('invalid_id'))
				return
			
			# Review a feed
			if args[1] in ['ok', 'good', 'yes']:
				cursor = self.connection.cursor()
				cursor.execute('UPDATE feeds SET moderated = 1 WHERE id = ?', (args[0],))
				
				self.connection.commit()
				cursor.close()
				
				self.bot.client.send_notice(message.nick, self.lang.get('feed_reviewed'))
			elif args[1] in ['wrong', 'bad', 'no']:
				cursor = self.connection.cursor()
				cursor.execute('DELETE FROM feeds WHERE id = ?', (args[0],))
				
				self.connection.commit()
				cursor.close()
				
				self.bot.client.send_notice(message.nick, self.lang.get('feed_reviewed'))
			else:
				self.bot.client.send_notice(message.nick, self.lang.get('review_syntax').replace('!', self.bot.settings.get('Bot', 'command_prefix')))
		else:
			self.bot.client.send_notice(message.nick, self.lang.get('review_syntax').replace('!', self.bot.settings.get('Bot', 'command_prefix')))			
	
	def destroy(self):
		self.connection.commit()
		self.connection.close()
	
