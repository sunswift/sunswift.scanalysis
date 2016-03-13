#!/bin/sh

export AUTOMAKE=/usr/bin/automake
export AUTOCONF=/usr/bin/autoconf
export ACLOCAL=/usr/bin/aclocal
export LIBTOOLIZE=/usr/bin/libtoolize

FILES="
 stamp-h*
 INSTALL
 config.cache
 decomp
 config.guess
 missing
 mkinstalldirs
 mdate-sh
 ltconfig
 ltmain.sh
 install-sh
 compile
 ltcf-c.sh
 ltcf-cxx.sh
 ltcf-gcj.sh
 libtool
"

rm -f ${FILES}

find .  -lname "/*" -exec rm {} \;

${LIBTOOLIZE} --force
${ACLOCAL}
${AUTOCONF}
${AUTOMAKE} -a

./configure --enable-static=no $@
