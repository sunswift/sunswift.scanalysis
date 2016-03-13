#!/bin/env python

# Use the PyGtk2 codegen modules.
# Allow new types to be registered.

import _config
import sys
import os
sys.path.append(os.path.join(_config.PYGTK_DEFSDIR, '../'))

from codegen.argtypes import matcher
import codegen.codegen

matcher.register('GdkWChar', matcher.get('gint32'))

codegen.codegen.main(sys.argv)
