# require automake-1.5
AUTOMAKE_OPTIONS = 1.5

SUBDIRS = gtkextra

CLEANFILES =
EXTRA_DIST = 

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = python-gtkextra.pc

EXTRA_DIST += \
  python-gtkextra.spec \
  python-gtkextra.spec.in \
  python-gtkextra.pc.in \
  examples/test.sh \
  examples/common.py \
  examples/icons.py \
  examples/pixmaps.py \
  examples/testboxes.py \
  examples/testbubbles.py \
  examples/testcharsel.py \
  examples/testcontour.py \
  examples/testflux.py \
  examples/testgtkfilesel.py \
  examples/testgtkfont.py \
  examples/testgtkiconlist.py \
  examples/testgtkplot3d.py \
  examples/testgtkplot.py \
  examples/testgtksheet.py \
  examples/testiterator.py \
  examples/testpixmap.py \
  examples/testpolar.py \
  examples/testrealtime.py 

snap:
	$(MAKE) dist distdir=$(PACKAGE)-SNAP-`date +"%Y%m%d"`
