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

import os

__settingsdir = os.path.expanduser('~/.luckybot')
__basedir = "."

def init():
	global __basedir
	try:
		root = __file__
		
		if os.path.islink(root):
			root = os.path.realpath(root)
		
		root = os.path.dirname(os.path.abspath(root))
	except:
		print "Could not determine path!"
		sys.exit(1)
			
	__basedir = root
	print __basedir

def get_personal_file(*elems):
	return os.path.join(__settingsdir, *elems)

def get_base_path(*elems):
	return os.path.join(__basedir, *elems)

