# Quick hack to help populate objects definitions in defs files.

# Copy C field definitions to this string.
# Then run me.

lines = """
  gdouble rx1, rx2, ry1, ry2;
  gint min_width, min_height;

  GdkRectangle allocation;

  guint state;

  GtkPlotCanvasType type;
  GtkPlotCanvasFlag flags;
  GtkPlotCanvasSelection selection;
  GtkPlotCanvasSelectionMode mode;

  gpointer data;

"""

import string

def process_field(t,v):
    t = t.strip()
    v = v.strip()
    if v[0] == '*':
        v = v[1:]
        t += '*'
    
    print """    '("%s" "%s")""" % (t,v)

def fields(lines):
    print """  (fields"""
    for line in lines.split('\n'):
        line = line.strip()
        line = line.replace(';', '')
        if not line:
            continue


        x = line.split(',')
        t,v = x[0].split(' ')
        vlist = [v]+x[1:]

        for v in vlist:
            process_field(t,v)


    print """  )"""


fields(lines)

    

    
    
    
