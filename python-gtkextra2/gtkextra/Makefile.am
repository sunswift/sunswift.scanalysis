pygtkextradir = $(pythondir)/gtk-2.0/gtkextra
pygtkextraexecdir = $(pyexecdir)/gtk-2.0/gtkextra

pygtkextra_PYTHON = \
  __init__.py \
  _config.py

EXTRA_DIST = \
  mycodegen.py


# FIXME: Do we want to drop files in the pygtk directory or in our own pkg directory
defsdir = $(PYGTK_DEFSDIR)
defs_DATA = \
 gtkextra.defs \
 gtkextra-types.defs \
 gtkextra-addons.defs 

EXTRA_DIST += $(defs_DATA)
CLEANFILES =

pkgincludedir = $(includedir)/pygtkextra-2.0/pygtkextra
pkginclude_HEADERS = 

INCLUDES = -I$(top_srcdir) $(PYTHON_INCLUDES)
#COMMONDEFS = $(srcdir)/gtkextra-types.defs 
COMMONDEFS = 

# gtkextra module
pygtkextraexec_LTLIBRARIES = _gtkextramodule.la
_gtkextramodule_la_CFLAGS = $(PYGTK_CFLAGS) $(GTK_CFLAGS) $(GTKEXTRA_CFLAGS)
#_gtkextramodule_la_LDFLAGS = -module -avoid-version -export-symbols-regex init_gtkextra
_gtkextramodule_la_LDFLAGS = -module -avoid-version
_gtkextramodule_la_LIBADD =  $(GTKEXTRA_LIBS) $(PYGTK_LIBS) $(GTK_LIBS)
_gtkextramodule_la_SOURCES = gtkextramodule.c
gtkextra.c: $(COMMONDEFS) gtkextra-addons.defs gtkextra-types.defs gtkextra.override
nodist__gtkextramodule_la_SOURCES = gtkextra.c

CLEANFILES += gtkextra.c
defs_DATA += gtkextra.defs gtkextra-types.defs
EXTRA_DIST += gtkextra.override mycodegen.py

CODEGEN=$(PYTHON) $(srcdir)/mycodegen.py

.defs.c:
	(cd $(srcdir) \
	 && $(CODEGEN) \
	    --register $(PYGTK_DEFSDIR)/pango-types.defs \
	    --register $(PYGTK_DEFSDIR)/gdk-types.defs \
	    --register $(PYGTK_DEFSDIR)/gtk-types.defs \
	    --override $*.override \
	    --prefix py$* $*.defs) > gen-$*.c \
	&& cp gen-$*.c $*.c \
	&& rm -f gen-$*.c

# a hack so that _config.py is not included in the final package.
dist-hook:
	-rm -f $(distdir)/_config.py
