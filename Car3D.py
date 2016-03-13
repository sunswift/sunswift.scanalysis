#!/usr/bin/env python

# You need to install these modules. They don't come with Python. 
import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl
import gobject
import time

from OpenGL.GL import *

class Car3D(gtk.VBox):
    def draw_glarea(self, glarea, event):
        # get GLContext and GLDrawable
        glcontext = glarea.get_gl_context()
        gldrawable = glarea.get_gl_drawable()
    
        # GL calls
        if not gldrawable.gl_begin(glcontext): return
    
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        blue = (0.2, 0.2, 1.0, 1.0)
        red = (0.8, 0.2, 0.2, 1.0)
        green = (0.0, 0.8, 0.2, 1.0)
        white = (0.8, 0.8, 0.8, 1.0)
        
        glPushMatrix()
        glScalef(0.002, 0.002, 0.002)
        glRotatef(-90.0, 1.0, 0.0, 0.0)
        glRotatef(30.0, 1.0, 0.0, 0.0)
        glRotatef(self.angle, 0.0, 0.0, 1.0)
        glTranslatef(2000.0,0.0, 0.0)
        
        glShadeModel(GL_SMOOTH)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, white )
        glCallList(self.car)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, red)
        glCallList(self.panel1)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, green)
        glCallList(self.panel2)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, blue)
        glCallList(self.panel3)

        glPopMatrix()
    
        if gldrawable.is_double_buffered():
            gldrawable.swap_buffers()
        else:
            glFlush()
    
        gldrawable.gl_end()

        diff = time.time() - self.timeval
        self.timeval = time.time()
        
#        print "FPS is: %.01f" % (1.0 / diff)
    
        return True

    def reshape_glarea(self, glarea, event):
        # get GLContext and GLDrawable
        glcontext = glarea.get_gl_context()
        gldrawable = glarea.get_gl_drawable()
    
        # GL calls
        if not gldrawable.gl_begin(glcontext): return
    
        x, y, width, height = glarea.get_allocation()
    
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if width > height:
            w = float(width) / float(height)
            glFrustum(-w, w, -1.0, 1.0, 5.0, 60.0)
        else:
            h = float(height) / float(width)
            glFrustum(-1.0, 1.0, -h, h, 5.0, 60.0)
    
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -40.0)
    
        gldrawable.gl_end()
    
        return True
    
    def init_glarea(self, glarea):
        # get GLContext and GLDrawable
        glcontext = glarea.get_gl_context()
        gldrawable = glarea.get_gl_drawable()
    
        # GL calls
        if not gldrawable.gl_begin(glcontext): return
    
        global gear1, gear2, gear3
    
        pos = (5.0, 5.0, 10.0, 0.0)
        red = (0.8, 0.1, 0.0, 1.0)
        green = (0.0, 0.8, 0.2, 1.0)
        blue = (0.2, 0.2, 1.0, 1.0)
    
        glLightfv(GL_LIGHT0, GL_POSITION, pos)
        glEnable(GL_CULL_FACE)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glRotated(self.angle, 1.0, 0.0, 0.0)
        glPushMatrix()
        
        self.car = glGenLists(1)
        glNewList(self.car, GL_COMPILE)
        self.draw_stl(self.triangles, 
                    notwithin   = (-7000.0, -699.99, 89.999, -0.0, 699.99, 1000.001))
        self.draw_stl(self.triangles, 
                    within= (-7000.001, -150.001, -0.001, -2800.001, 150.001, 1000.001) )
        glEndList()
        
        self.panel1 = glGenLists(1)        
        glNewList(self.panel1, GL_COMPILE)
        self.draw_stl(self.triangles, 
                    within   = (-7000.0, -700.1, 90, -2399.0, 700.1, 1000.0),
                    notwithin= (-7000.0, -150.0, 0, -2800.0, 150.0, 1000.0) )
        glEndList()

        self.panel2 = glGenLists(1)        
        glNewList(self.panel2, GL_COMPILE)
        self.draw_stl(self.triangles, 
                    within   = (-2401.0, -700.1, 90, -1149.0, 700.1, 1000.0),
                    notwithin= (-7000.0, -150.0, 0, -2800.0, 150.0, 1000.0) )
        glEndList()

        self.panel3 = glGenLists(1)        
        glNewList(self.panel3, GL_COMPILE)
        self.draw_stl(self.triangles, 
                    within   = (-1151.0, -700.1, 90, -69.0, 700.1, 1000.0),
                    notwithin= (-7000.0, -150.0, 0, -2800.0, 150.0, 1000.0) )
        glEndList()
        
        glEnable(GL_NORMALIZE)
        glPopMatrix()
   
        gldrawable.gl_end()

    def idle_glarea(self, glarea):
        self.angle = (time.time() * 90.0) % 360.0
#        self.angle = self.angle + 0.1
        # Invalidate whole window.
        glarea.window.invalidate_rect(glarea.allocation, False)
        # Update window synchronously (fast).
        glarea.window.process_updates(False)
        return True
    
    def map_glarea(self, glarea, event):
        gobject.idle_add(self.idle_glarea, glarea)
        return True

    def read_stl(self, filename, mirror_on_y=False):
        try:
            f = file(filename)
        except:
            print "Could not read .stl file"
            return None
            
        normal = None
        vertices = []
        triangles = []
        
        for line in f:
            tokens = line.split()
        
            # Check the first token to see what we're doing. 
            if tokens[0] == "solid":
                print "Reading " + line
                continue
                
            if tokens[0] == "endsolid":
                print "Finished reading: " + line
                continue
                
            if tokens[0] == "facet":
                if tokens[1] == "normal":
                    normal = (float(tokens[2]), float(tokens[3]), float(tokens[4]))
            
            if tokens[0] == "endfacet":
                if len(vertices) != 3:
                    print "Finished a triangle with less than three vertices!"
                    sys.exit()
                if normal == None:
                    print "Finished a triangle without a normal!"
                    sys.exit()
                    
                triangle = (normal, vertices)
                triangles.append(triangle)
                
                if mirror_on_y is True:
                    mirror_vertices=[]
                    for (x,y,z) in vertices:
                        mirror_vertices = [(x,-y,z)] + mirror_vertices
                    (nx,ny,nz) = normal
                    mirror_normal = (nx, -ny, nz)
                    
                    triangle = (mirror_normal, mirror_vertices)
                    triangles.append(triangle)
                
                vertices = []
                normal = None
                continue
            
            if tokens[0] == "outer":
                continue
            if tokens[0] == "endloop":
                continue
            
            if tokens[0] == "vertex":
                vertex = (float(tokens[1]), float(tokens[2]), float(tokens[3]))
                vertices.append(vertex)
                continue
        
        print "Read %d triangles" % len(triangles)
        
        f.close()
        
        return triangles

    def draw_stl(self, stl, within=None, notwithin=None):
        if within != None:
            (ax, ay, az, bx, by, bz) = within
        
        def test_point( (ax, ay, az, bx, by, bz), (x,y,z) ):
            if x < ax:
                return False
            if x > bx: 
                return False
            if y < ay: 
                return False
            if y > by: 
                return False
            if z < az: 
                return False
            if z > bz: 
                return False
            return True
            
        glBegin(GL_TRIANGLES)
        for (normal, vertices) in stl: 
            (x0,y0,z0) = vertices[0]
            (x1,y1,z1) = vertices[1]
            (x2,y2,z2) = vertices[2]
    
            if within != None:
                if not test_point(within, vertices[0]):
                    continue
                if not test_point(within, vertices[1]):
                    continue
                if not test_point(within, vertices[2]):
                    continue

            if notwithin != None:
                if test_point(notwithin, vertices[0]):
                    continue
                if test_point(notwithin, vertices[1]):
                    continue
                if test_point(notwithin, vertices[2]):
                    continue

            if (within == None) or test_point(within, vertices[0]):
                (nx,ny,nz) = normal
                glNormal3f(nx,ny,nz)
                (x,y,z) = vertices[0]; glVertex3f(x,y,z)
                (x,y,z) = vertices[1]; glVertex3f(x,y,z)
                (x,y,z) = vertices[2]; glVertex3f(x,y,z)
            
                glNormal3f(-nx,-ny,-nz)
                (x,y,z) = vertices[2]; glVertex3f(x,y,z)
                (x,y,z) = vertices[1]; glVertex3f(x,y,z)
                (x,y,z) = vertices[0]; glVertex3f(x,y,z)

        glEnd()

    def __init__(self, input_file):
        gtk.VBox.__init__(self)
            
        self.angle = 0
        self.timeval = 0
        
        self.triangles = self.read_stl(input_file, mirror_on_y=True)
        
        major, minor = gtk.gdkgl.query_version()
        print "GLX version = %d.%d" % (major, minor)

        #
        # frame buffer configuration
        #

        # use GLUT-style display mode bitmask
        try:
            # try double-buffered
            glconfig = gtk.gdkgl.Config(mode=(gtk.gdkgl.MODE_RGB    |
                                            gtk.gdkgl.MODE_DOUBLE |
                                            gtk.gdkgl.MODE_DEPTH))
        except gtk.gdkgl.NoMatches:
            # try single-buffered
            glconfig = gtk.gdkgl.Config(mode=(gtk.gdkgl.MODE_RGB    |
                                            gtk.gdkgl.MODE_DEPTH))
                                            
        print "glconfig.is_rgba() =",            glconfig.is_rgba()
        print "glconfig.is_double_buffered() =", glconfig.is_double_buffered()
        print "glconfig.has_depth_buffer() =",   glconfig.has_depth_buffer()

        # get_attrib()
        print "gtk.gdkgl.RGBA = %d"         % glconfig.get_attrib(gtk.gdkgl.RGBA)
        print "gtk.gdkgl.DOUBLEBUFFER = %d" % glconfig.get_attrib(gtk.gdkgl.DOUBLEBUFFER)
        print "gtk.gdkgl.DEPTH_SIZE = %d"   % glconfig.get_attrib(gtk.gdkgl.DEPTH_SIZE)
        
        
        # Get going on the openGL stuff
        self.glarea = gtk.gtkgl.DrawingArea(glconfig)
        self.glarea.set_size_request(300, 300)

        self.glarea.connect_after('realize', self.init_glarea)
        self.glarea.connect('configure_event', self.reshape_glarea)
        self.glarea.connect('expose_event', self.draw_glarea)
        self.glarea.connect('map_event', self.map_glarea)
        
        self.pack_start(self.glarea)