#!/bin/sh
PYTHON=${PYTHON:-python}

[ $1 = "-gdb" ] && DEBUG=1 && shift

if test -z $1; then
	echo
	echo "Run example program in development tree"
	echo "Use: $0 [-gdb] filename.py"
	echo "Toby D. Reeves <toby@solidstatescientific.com>"
	exit 0
fi

export PYTHONPATH=../:$PYTHONPATH

if test -z $DEBUG; then
    $PYTHON -c "\
try:
    import common;
    print 'Using:', common.__file__
except ImportError:
    pass
execfile('$1')
"
else
    $PYTHON -c "\
try:
    import common;
    print 'Using:', common.__file__
except ImportError:
    pass
import os
raw_input('Attach gdb on %d. Press return to begin \"$1\".' % os.getpid())
del os
execfile('$1')"
fi
