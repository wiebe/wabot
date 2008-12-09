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

import threading

def threaded(f):
	"""
		A decorator that will make any function run in a new thread
		
		@type f: function
		@param f: The function to wrap in a thread
	"""
	
	def wrapper(*args, **kwargs):
		t = threading.Thread(target=f, args=args, kwargs=kwargs)
		t.setDaemon(True)
		t.start()

	wrapper.__name__ = f.__name__
	wrapper.__dict__ = f.__dict__
	wrapper.__doc__ = f.__doc__

	return wrapper
