/* -*- Mode: C; c-basic-offset: 4 -*- */
#ifdef HAVE_CONFIG_H
#  include "config.h"
#endif
#include <Python.h>
/* include this first, before NO_IMPORT_PYGOBJECT is defined */
#include <pygobject.h>
#include <pygtk/pygtk.h>
#include <gtkextra/gtkextra.h>
#include <gtkextra/gtkextratypebuiltins.h>

void pygtkextra_register_classes(PyObject *d);
void pygtkextra_add_constants(PyObject *module, const gchar *strip_prefix);

extern PyMethodDef pygtkextra_functions[];

DL_EXPORT(void)
init_gtkextra(void)
{
    PyObject *m, *d;

    m = Py_InitModule("gtkextra._gtkextra", pygtkextra_functions);
    d = PyModule_GetDict(m);

    init_pygobject();
    init_pygtk();

    pygtkextra_register_classes(d);
    pygtkextra_add_constants(m, "GTK_");

#define _ADD_CONST( _x ) \
    PyModule_AddIntConstant(m, #_x, GTK_ ## _x);

    /* These were #defines's */
    _ADD_CONST(PLOT_LETTER_W);
    _ADD_CONST(PLOT_LETTER_H);
    _ADD_CONST(PLOT_LEGAL_W);
    _ADD_CONST(PLOT_LEGAL_H);
    _ADD_CONST(PLOT_A4_W);
    _ADD_CONST(PLOT_A4_H);
    _ADD_CONST(PLOT_EXECUTIVE_W);
    _ADD_CONST(PLOT_EXECUTIVE_H);
    _ADD_CONST(PLOT_CANVAS_DND_FLAGS);

    /* These were anonymous enum's. They really should be fixed in gtkextra. */
    _ADD_CONST(ICON_LIST_ICON);
    _ADD_CONST(ICON_LIST_TEXT_RIGHT);
    _ADD_CONST(ICON_LIST_TEXT_BELOW);

    _ADD_CONST(PLOT_DATA_X);
    _ADD_CONST(PLOT_DATA_Y);
    _ADD_CONST(PLOT_DATA_Z);
    _ADD_CONST(PLOT_DATA_A);
    _ADD_CONST(PLOT_DATA_DX);
    _ADD_CONST(PLOT_DATA_DY);
    _ADD_CONST(PLOT_DATA_DZ);
    _ADD_CONST(PLOT_DATA_DA);
    _ADD_CONST(PLOT_DATA_LABELS);

#undef _ADD_CONST

    gtk_psfont_init();

    if (PyErr_Occurred())
        Py_FatalError("could not initialise module gtkextra._gtkextra");
}
