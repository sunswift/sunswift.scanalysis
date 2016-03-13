#include "Python.h"

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <assert.h>

#include "jvfit.h"

static PyObject *ErrorObject;

/* Prototypes */ 
static PyObject *do_jvfit(PyObject *self, PyObject *args, PyObject *keywds);

/* Method Table */ 
static PyMethodDef jvfit_methods[] = {
    {"jvfit",  (PyCFunction)do_jvfit, METH_VARARGS | METH_KEYWORDS, "Fit a JV Curve"},
    {NULL, (PyCFunction)NULL, 0, NULL}        /* Sentinel */
};

/* Implementation */ 
static PyObject *
do_jvfit(PyObject *self, PyObject *args, PyObject *keywds)
{
    int i, len; 
    
    /* Names of each arg and keyword param */ 
	static char *kwlist[] = {"inputI",\
                            "inputV",\
                            "inputS",\
                            "i_jitter", \
                            "v_jitter", \
                            "s_jitter", \
                            "tempC", \
                            "cell_area", \
                            "rs_toll", \
                            "max_shunt", \
                            "jl", \
                            "n_cells", \
                            "weighting", \
                            "fitting", \
                            "smoothing", \
                            "smoothpoints", \
                            "sorting", \
                            "skipping", \
                            NULL};

    /* Double inputs */
    double double_inputs[JVFIT_N_INPUTS]; 
    int int_options[JVFIT_N_OPTIONS];

    /* JVFit variables */ 
    int err = JVFIT_ERROR_NONE;
    
    /* Outputs */ 
    double params[JVFIT_PARAM_MAX]; 
    
    /* The list inputs */ 
    PyObject *pyInputI=NULL; 
    PyObject *pyInputV=NULL; 
    PyObject *pyInputS=NULL; 
    
    double *inputI=NULL, *inputV=NULL, *inputS=NULL; 
    
    /* Set the inputs array to its default settings */ 
    double_inputs[JVFIT_INPUT_I_JITTER] = JVFIT_I_JITTER_DEFAULT;
    double_inputs[JVFIT_INPUT_V_JITTER] = JVFIT_V_JITTER_DEFAULT;
    double_inputs[JVFIT_INPUT_S_JITTER] = JVFIT_S_JITTER_DEFAULT;
    double_inputs[JVFIT_INPUT_TEMP_C] = JVFIT_TEMPC_DEFAULT;
    double_inputs[JVFIT_INPUT_CELL_AREA] = JVFIT_CELL_AREA_DEFAULT;
    double_inputs[JVFIT_INPUT_RS_TOLL] = JVFIT_RS_TOLLERANCE_DEFAULT;
    double_inputs[JVFIT_INPUT_MAX_SHUNT] = JVFIT_MAX_SHUNT_DEFAULT;
    double_inputs[JVFIT_INPUT_JL] = JVFIT_JL_DEFAULT;

    /* Set the inputs array to its default settings */ 
    int_options[JVFIT_OPTION_N_CELLS] = JVFIT_N_CELLS_DEFAULT; 
    int_options[JVFIT_OPTION_WEIGHT_SCHEME] = JVFIT_WEIGHT_SCHEME_DEFAULT;
    int_options[JVFIT_OPTION_FIT_SCHEME] = JVFIT_FIT_SCHEME_DEFAULT;
    int_options[JVFIT_OPTION_SMOOTH_SCHEME] = JVFIT_SMOOTH_SCHEME_DEFAULT;
    int_options[JVFIT_OPTION_POINTS_TO_SMOOTH] = JVFIT_POINTS_TO_SMOOTH_DEFAULT;
    int_options[JVFIT_OPTION_PARAM_SCHEME] = JVFIT_PARAM_SCHEME_DEFAULT; 
    int_options[JVFIT_OPTION_SORT] = JVFIT_SORT_SCHEME_DEFAULT;
    int_options[JVFIT_OPTION_USE_SKIPPING] = JVFIT_USE_SKIPPING_DEFAULT; 
    
	if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!O!|O!ddddddddiiiiiii", kwlist, \
                &PyList_Type, &pyInputI, \
                &PyList_Type, &pyInputV, \
                &PyList_Type, &pyInputS, \
                &double_inputs[0], \
                &double_inputs[1], \
                &double_inputs[2], \
                &double_inputs[3], \
                &double_inputs[4], \
                &double_inputs[5], \
                &double_inputs[6], \
                &double_inputs[7], \
                &int_options[0], \
                &int_options[1], \
                &int_options[2], \
                &int_options[3], \
                &int_options[4], \
                &int_options[5], \
                &int_options[6], \
                &int_options[7] \
                ))
		return NULL; 
        
    /* Parse the input I list */ 
    len = PyList_Size(pyInputI);
    inputI = (double*)malloc(sizeof(double) * len); 
    for(i=0; i<len; i++){
        PyObject* doubleObj = PyList_GetItem(pyInputI, i);
        inputI[i] = PyFloat_AsDouble(doubleObj); 
    }

    /* Parse the input V list */ 
    i = PyList_Size(pyInputV);
    if(i != len){
        PyErr_SetString(PyExc_ValueError, "JVFit: All sample arrays must be the same length.");
        return NULL; 
    }
    inputV = (double*)malloc(sizeof(double) * len); 
    for(i=0; i<len; i++){
        PyObject* doubleObj = PyList_GetItem(pyInputV, i);
        inputV[i] = PyFloat_AsDouble(doubleObj); 
    }

    /* Check to see whether pyInputS was provided */ 
    inputS = (double*)malloc(sizeof(double) * len); 
    if(pyInputS != NULL){
        /* Parse the input S list */ 
        i = PyList_Size(pyInputS);
        if(i != len){
            PyErr_SetString(PyExc_ValueError, "JVFit: All sample arrays must be the same length.");
            return NULL; 
        }
        for(i=0; i<len; i++){
            PyObject* doubleObj = PyList_GetItem(pyInputS, i);
            inputS[i] = PyFloat_AsDouble(doubleObj); 
        }
    }else{
        for(i=0; i<len; i++)
            inputS[i] = 1.0; 
    }
    
    /*for(i=0; i<len; i++)
        printf("[%d]: (%lf, %lf, %lf)\n", i, inputI[i], inputV[i], inputS[i]); 
        
    for(i=0; i<JVFIT_N_INPUTS; i++)
        printf("Made it to here! -- double_inputs[%d] is %lf\n", i, double_inputs[i]); 
	
    for(i=0; i<JVFIT_N_OPTIONS; i++)
        printf("Made it to here! -- value is int_options[%d] is %d\n", i, int_options[i]); 
    */ 
    
    /* Instantiate the JVfit class with hour inputs */ 
    JVFit jvfit(inputI, inputV, inputS, len);
    
    /* Set the options/inputs the way we have them */ 
    for(i=0; i<JVFIT_N_OPTIONS; i++)
        jvfit.setOption(i, int_options[i]);
    for(i=0; i<JVFIT_N_INPUTS; i++)
        jvfit.setInput(i, double_inputs[i]);
        
    /* Do the fit */ 
    err = jvfit.doFit(); 
    if(err != JVFIT_ERROR_NONE){
        switch(err){
        case JVFIT_ERROR_COULD_NOT_DETERMINE_POLARITY:
            PyErr_SetString(PyExc_RuntimeError, "JVFit: Could not determine polarity"); 
            return NULL; 
        case JVFIT_ERROR_PARAM_SCHEME_NOT_EXIST:
            PyErr_SetString(PyExc_RuntimeError, "JVFit: Parameter scheme does not exist"); 
            return NULL; 
        case JVFIT_ERROR_TOO_FEW_SMOOTHING_POINTS:
            PyErr_SetString(PyExc_RuntimeError, "JVFit: Too few smoothing points"); 
            return NULL; 
        case JVFIT_ERROR_RS_LOOP_MAX_EXCEEDED:
            PyErr_SetString(PyExc_RuntimeError, "JVFit: Maximum RS loops exceeded"); 
            return NULL; 
        }
    }
    
    jvfit.getParams(params); 
    params[JVFIT_PARAM_RS] = jvfit.getRs();
    
    /* Free the arrays which we malloc'd */ 
    free(inputS); 
    free(inputV); 
    free(inputI); 
    
    return Py_BuildValue("{sdsdsdsdsdsd}", 
        "JL", params[0], 
        "J01", params[1], 
        "J02", params[2], 
        "GSH", params[3], 
        "GPH", params[4], 
        "RS", params[5]);
}    
    
static char jvfit_module_documentation[] = 
"Documentation goes here"
;

   
PyMODINIT_FUNC
initjvfit(void)
{
        PyObject *m, *d;

        /* Create the module and add the functions */
        m = Py_InitModule4("jvfit", jvfit_methods,
                jvfit_module_documentation,
                (PyObject*)NULL,PYTHON_API_VERSION);

        /* Add some symbolic constants to the module */
        d = PyModule_GetDict(m);
        ErrorObject = PyString_FromString("jvfit.error");
        PyDict_SetItemString(d, "error", ErrorObject);

        /* XXXX Add constants here */

        /* Check for errors */
        if (PyErr_Occurred())
                Py_FatalError("can't initialize module jvfit");
}
