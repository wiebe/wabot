#
# Sysinfo plugin
# (c) Copyright 2008 by Wiebe Verweij
# http://www.wiebelt.nl
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

import os
from gettext import gettext as _
from luckybot.bot.plugins import Plugin
from luckybot.luckynet.protocols.irc import Format

class SysinfoPlugin(Plugin):
	
	def initialize(self):
		self.register_command('uptime', self.get_uptime, help=_('Displays the server\'s uptime and stress level.'))
		self.register_command('os', self.get_os, help=_('Shows wich OS is running on this server.'))
		self.register_command('usage', self.get_usage, help=_('Calculates how much memory and CPU i use.'))
		self.register_command('cpu', self.get_cpu, help=_('Returns the CPU model and stress level.'))
		self.register_command('memory', self.get_memory, help=_('Calculates how much memory is used.'))
	
	def get_uptime(self, message, keywords):
		load = os.popen('uptime')
		load = load.read().splitlines()
		self.bot.client.send_pm(message.channel, load[0])

	def get_os(self, message, keywords):
		# Get kernel version
		kernel	= os.popen('uname -r')
		kernel	= kernel.read().splitlines()
		kernel	= kernel[0]

		# Get release version
		distro	= os.popen('lsb_release -a 2> /dev/null').read()
		distro	= distro.strip()
		distro	= distro.splitlines()

		for line in distro:
			split = line.split(':')
			if split[0] == 'Description':
				distro = split[1]
				break

		# Make and send the message!		
		send = '[ Os:' + Format.color('red') + ' Linux ' + Format.normal() + '|\
				 Kernel:' + Format.color('red') + ' ' + kernel + Format.normal() + ' |\
				 Distro:' + Format.color('red') + ' ' + distro + Format.normal() + ' ]'

		self.bot.client.send_pm(message.channel, send)

	def get_usage(self, message, keywords):
		# Get process information
		pid		= os.getpid()
		usage	= os.popen('ps -eo%cpu,%mem,rss,pid | grep ' + str(pid))
		pieces 	= usage.read().split(' ')

		# Strip all the data that we dont need..
		data	= []
		for piece in pieces:
			if piece != ' ':
				data.append(piece)

		# Now calculate and define the data		
		cpu		= data[1]
		memory 	= int(data[5]) / 1024

		# Make and send the message :)
		send 	= '[' + Format.color('red') + ' Usage ' + Format.normal() + \
		'| CPU:' + Format.color('red') + ' ' + cpu + Format.normal() + ' % \
		| Memory:' + Format.color('red') + ' ' + str(memory) + Format.normal() + ' MB ]'	
		self.bot.client.send_pm(message.channel, send)

	def get_cpu(self, message, keywords):
		# Get proccessor information
		cpu_info = os.popen('cat /proc/cpuinfo')
		cpu_info = cpu_info.read().splitlines()

		# Now get the specific information we want to display.
		for info in cpu_info:
			info = info.split(':')	
			info[0] = info[0].strip()
			if info[0] == 'model name': 
				cpu_model 	= info[1]
			elif info[0] == 'cpu MHz':
				cpu_mhz		= info[1]
			elif info[0] == 'cache size':
				cpu_cache	= info[1]

		# Get temperature information		
		show_temp = self.bot.settings.get('SysInfo', 'sensors')	
		if (show_temp == 'true'):
			sensors = os.popen('sensors')
			sensors = sensors.read().splitlines()

			for sensor in sensors:
				type = sensor.split(':')
				if type[0] == 'CPU Temp':
					cpu_temp = type[1].split('(')
					pieces = cpu_temp[0].split(' ')
					for piece in pieces:
						if piece != '':
							cpu_temp = piece
							break

					temp = '| Temp:' + Format.color('red') + ' ' + cpu_temp + ' ' + Format.normal() + ' ]' 
		else:
			temp = ']'

		# Now, lets format the message and send the message!
		send	= '[' + Format.color('red') + ' CPU ' + Format.normal() + ' |'
		send	= send + ' Model:' + Format.color('red') + cpu_model + ' ' + Format.normal() + '|'
		send	= send + ' Speed: ' + Format.color('red') + cpu_mhz + Format.normal()
		send	= send + ' (' + Format.color('red') + cpu_cache + Format.normal() + ' ) '
		send	= send + temp	
		self.bot.client.send_pm(message.channel, send)

	def get_memory(self, message, keywords):
		# Get memory usage information
		memory_info = os.popen('free -m')
		memory_info = memory_info.read().splitlines()

		# Get RAM specific information
		pieces	= memory_info[1].split(' ')
		ram_info	= []
		for piece in pieces:
			if piece != '':
				ram_info.append(piece)

		ram_total	= ram_info[1]
		ram_used	= ram_info[2]
		ram_free	= ram_info[3]

		# Get Swap specific information
		pieces	= memory_info[3].split(' ')
		swap_info	= []
		for piece in pieces:
			if piece != '':
				swap_info.append(piece)

		swap_total	= swap_info[1]
		swap_used	= swap_info[2]
		swap_free	= swap_info[3]

		# Format and send it! :)
		send	= '[' + Format.color('red') + ' Memory ' + Format.normal() + ' |'
		send	= send + ' Ram:' + Format.color('red') + ' ' + ram_used + ' / ' + ram_total + Format.normal() + ' MB |'
		send	= send + ' Swap:' + Format.color('red') + ' ' + swap_used + ' / ' + swap_total + Format.normal() + ' MB ]'	
		self.bot.client.send_pm(message.channel, send)
		
	def destroy(self):
		return true