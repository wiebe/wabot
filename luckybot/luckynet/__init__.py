__all__ = ['connection', 'protocols']

import os
if os.name == 'nt':
	EWOULDBLOCK	= 10035
	EINPROGRESS	= 10036
	EALREADY	= 10037
	ECONNRESET  = 10054
	ENOTCONN	= 10057
else:
	from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, ENOTCONN
