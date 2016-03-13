"""
Process the examples into html, png, eps, and pdf files.
"""

import sys
pydir='/usr/new-stuff/lib/python2.2/site-packages/'
sys.path.insert(0, pydir)
sys.path.insert(0, pydir+'/gtk-2.0')

import os
import time
import gtk
import gtkextra

def process_html(name, odir):
    os.system('enscript -E --color -W html --color -p %(odir)s%(name)s.py.html %(name)s.py' % locals())

def process_images(app, name, odir):
    eps_filename = "%(odir)s%(name)s.eps" % locals()
    pdf_filename = "%(odir)s%(name)s.pdf" % locals()
    png_filename = "%(odir)s%(name)s.png" % locals()

    if hasattr(app, 'canvas'):
        print 'Saving EPS:', eps_filename
        app.canvas.export_ps_with_size(eps_filename, epsflag=gtk.TRUE)
        print 'Converting to PDF:', pdf_filename
        os.system('ps2pdf %s %s' % (eps_filename, pdf_filename) )

    print 'Saving PNG:', png_filename
    win = app.window
    w, h = win.get_size()
    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, w, h)
    pixbuf.get_from_drawable(win, win.get_colormap(), 0,0,0,0, w,h)
    pixbuf.save(png_filename, "png")

    app.destroy()
    gtk.main_quit()

def process_gui(name, odir, delay=1):
    exec("""\
gtkextra.psfont_init()
import %(name)s
app = %(name)s.Application()\
    """ % locals() )

    gtk.timeout_add(int(delay*1000), process_images, app, name, odir)
    gtk.main()


################################################################################
modules = [
    ['testboxes', 1],
    ['testbubbles', 1],
    ['testcharsel', 1],
    ['testcontour', 1.5],
    ['testflux', 1],
    #['testgtkfilesel', 1],
    ['testgtkfont', 1],
    ['testgtkiconlist', 1],
    ['testgtkplot3d', 1],
    ['testgtkplot', 1],
    #['testgtksheet', 1],
    ['testiterator', 1],
    ['testpixmap', 1],
    ['testpolar', 1],
    ['testrealtime', 5]
    ]

odir = './output/'
if not os.path.exists(odir):
    print 'Making output directory', odir
    os.mkdir(odir)

for m,delay in modules:
    process_html(m, odir)
    process_gui(m, odir, delay)
    
