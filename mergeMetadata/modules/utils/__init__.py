import os
import __main__

PWD = os.path.dirname( os.path.realpath( __main__.__file__ ) )

PATH_SRC				= 'AP_SALESFORCE/src'
PATH_SRC_RETRIEVED		= 'srcRetrieved'
PATH_DESCRIBE			= 'describe.log'

SET_PARSEABLE_FOLDERS	= { 'profiles' }

XMLNS_DEF				= 'http://soap.sforce.com/2006/04/metadata'
XMLNS					= f'{{{XMLNS_DEF}}}'
STANDARD_ATTRIBUTES		= [ 'nameField', 'searchLayouts', 'articleTypeChannelDisplay' ]
IDENTATION				= '    '