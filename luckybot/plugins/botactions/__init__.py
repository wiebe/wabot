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

from gettext import gettext as _
from luckybot.luckynet.protocols.irc import Format

def initialize():
	plugin.register_command('quit', quit, help=_("Quit the bot"), args="[quit message]")
	plugin.register_command('join', join_channel, help=_("Join a specified channel"), args="channel")
	plugin.register_command('part', part_channel, help=_("Leave a specified channel"), args="channel")
	plugin.register_command('eval', eval_code, help=_("Run python code from the bot"), args="code")
	plugin.register_command('nick', change_nick, help=_("Change the nick of the bot"), args="new_nick")

def quit(message, keywords):
	if not plugin.bot.auth.check_logged_in(message.nick):
		plugin.bot.client.send_notice(message.nick, _("You do not have enough rights to use this command"))
		return
		
	plugin.bot.client.send('QUIT :%s' % message.bot_args)
	plugin.bot.client.connection.close()

def join_channel(message, keywords):
	if not plugin.bot.auth.check_logged_in(message.nick):
		plugin.bot.client.send_notice(message.nick, _("You do not have enough rights to use this command"))
		return
	
	if len(message.bot_args) == 0 or not message.bot_args.startswith('#'):
		plugin.bot.client.send_notice(message.nick, _("No channel given"))
		return
	
	plugin.bot.client.send('JOIN %s' % message.bot_args)

def part_channel(message, keywords):
	if not plugin.bot.auth.check_logged_in(message.nick):
		plugin.bot.client.send_notice(message.nick, _("You do not have enough rights to use this command"))
		return
	
	if len(message.bot_args) == 0 or not message.bot_args.startswith('#'):
		plugin.bot.client.send_notice(message.nick, _("No channel given"))
		return
	
	plugin.bot.client.send('PART %s' % message.bot_args)

def eval_code(message, keywords):
	if not plugin.bot.auth.check_logged_in(message.nick):
		plugin.bot.client.send_notice(message.nick, _("You do not have enough rights to use this command"))
		return
	
	if len(message.bot_args) == 0:
		return
	
	r = None
	
	try:
		exec message.bot_args
	except Exception, e:
		r = e
	
	if r == "" or r == None:
		plugin.bot.client.send_pm(message.channel, _("No Result"))
	else:
		plugin.bot.client.send_pm(message.channel, _("Result:") + " " + str(r))

def change_nick(message, keywords):
	if not plugin.bot.auth.check_logged_in(message.nick):
		plugin.bot.client.send_notice(message.nick, _("You do not have enough rights to use this command"))
		return
	
	if len(message.bot_args) == 0:
		return
	
	plugin.bot.client.send('NICK %s' % message.bot_args)
