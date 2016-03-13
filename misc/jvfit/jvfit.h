#ifndef JV_FIT_H
#define JV_FIT_H
/*
  Name: jvfit.h
  Copyright: 
  Author: Bonne Eggleston
  Date: 03/09/04 11:27
  Description: Methods for performing jv curve fitting for solar cells.
  //TODO: Add more errors to everything
  //TODO: Check all variable initialisation
  //TODO: Add itteration hooks to stop crashing
*/

#include "leastsquares.h"
#include "quadsmooth.h"
#include "twodiodemodel.h"
#include <stdlib.h>

const int JVFIT_WEIGHT_SCHEME_NONE =                0;
const int JVFIT_WEIGHT_SCHEME_ODR =                 1;
const int JVFIT_WEIGHT_SCHEME_DEFAULT =             JVFIT_WEIGHT_SCHEME_NONE;

const int JVFIT_FIT_SCHEME_LSQ =                    0;
const int JVFIT_FIT_SCHEME_DEFAULT =                JVFIT_FIT_SCHEME_LSQ;

const int JVFIT_SMOOTH_SCHEME_NONE =                0;
const int JVFIT_SMOOTH_SCHEME_QUAD =                1;
const int JVFIT_SMOOTH_SCHEME_DEFAULT =             JVFIT_SMOOTH_SCHEME_NONE;
const int JVFIT_POINTS_TO_SMOOTH_DEFAULT =          20;

const int JVFIT_PARAM_SCHEME_ONE_DIODE_JL =         0;
const int JVFIT_PARAM_SCHEME_TWO_DIODE_JL =         1;
const int JVFIT_PARAM_SCHEME_TWO_DIODE_RPH_JL =     2;
const int JVFIT_PARAM_SCHEME_ONE_DIODE_SUNS_VOC =   3;
const int JVFIT_PARAM_SCHEME_TWO_DIODE_SUNS_VOC =   4;
const int JVFIT_PARAM_SCHEME_ONE_DIODE_DJL =        5;
const int JVFIT_PARAM_SCHEME_TWO_DIODE_DJL =        6;
const int JVFIT_PARAM_SCHEME_DEFAULT =              JVFIT_PARAM_SCHEME_TWO_DIODE_JL;

const int JVFIT_SORT_SCHEME_NONE = 0;
const int JVFIT_SORT_SCHEME_QSORT = 1;
const int JVFIT_SORT_SCHEME_DEFAULT = JVFIT_SORT_SCHEME_QSORT;

const int JVFIT_USE_SKIPPING_DEFAULT = 0;

const int JVFIT_PARAM_JL  =                         0;
const int JVFIT_PARAM_JO1 =                         1;
const int JVFIT_PARAM_JO2 =                         2;
const int JVFIT_PARAM_GSH =                         3;
const int JVFIT_PARAM_GPH =                         4;
const int JVFIT_PARAM_RS  =                         5;
const int JVFIT_PARAM_MAX =                         6;

//Order in which to skip parameters.
const int JVFIT_PARAM_SKIP[JVFIT_PARAM_MAX] = {
                JVFIT_PARAM_GPH,
                JVFIT_PARAM_GSH,
                JVFIT_PARAM_JO2,
                JVFIT_PARAM_JL,
                JVFIT_PARAM_RS,
                JVFIT_PARAM_JO1};


const double JVFIT_CELL_AREA_DEFAULT =      1;      //m2
const int    JVFIT_N_CELLS_DEFAULT =        1;      //Cell
const double JVFIT_RS_TOLLERANCE_DEFAULT =  0.0000000001;  //ohm m2
const double JVFIT_MAX_SHUNT_DEFAULT =      0.0001;     //ohm m2
const double JVFIT_JL_DEFAULT =             400.0;    //A / m2
const double JVFIT_TEMPC_DEFAULT =          25.0;
const double JVFIT_I_JITTER_DEFAULT =       0.1;      //A
const double JVFIT_V_JITTER_DEFAULT =       0.0005;      //V
const double JVFIT_S_JITTER_DEFAULT =       0.01; //Suns
const double JVFIT_LARGE_GRADIENT =         10000; //Value of gradient to give to poor fits (so that weight is small)
const double JVFIT_RS_STEP_INITIAL =        5e-3;   //ohm m2

const int JVFIT_RS_LOOP_MAX =               1000;

// Indicies for option array
const int JVFIT_OPTION_N_CELLS =  0;
const int JVFIT_OPTION_WEIGHT_SCHEME =  1;
const int JVFIT_OPTION_FIT_SCHEME =   2;
const int JVFIT_OPTION_SMOOTH_SCHEME =  3;
const int JVFIT_OPTION_POINTS_TO_SMOOTH = 4;
const int JVFIT_OPTION_PARAM_SCHEME =   5;
const int JVFIT_OPTION_SORT =   6;
const int JVFIT_OPTION_USE_SKIPPING = 7;
const int JVFIT_N_OPTIONS =     8;

// Indicies for input array
const int JVFIT_INPUT_I_JITTER =  0;
const int JVFIT_INPUT_V_JITTER =  1;
const int JVFIT_INPUT_S_JITTER =  2;
const int JVFIT_INPUT_TEMP_C =    3;
const int JVFIT_INPUT_CELL_AREA =   4;
const int JVFIT_INPUT_RS_TOLL =   5;
const int JVFIT_INPUT_MAX_SHUNT =   6;
const int JVFIT_INPUT_JL =    7;
const int JVFIT_N_INPUTS =    8;

// Error codes
const int JVFIT_ERROR_NONE =                         0;
const int JVFIT_ERROR_COULD_NOT_DETERMINE_POLARITY = 1;
const int JVFIT_ERROR_PARAM_SCHEME_NOT_EXIST =       2;
const int JVFIT_ERROR_TOO_FEW_SMOOTHING_POINTS =     3;
const int JVFIT_ERROR_RS_LOOP_MAX_EXCEEDED =         4;

//Data columns
const int JVFIT_DATA_COL_J =    0;
const int JVFIT_DATA_COL_V =    1;
const int JVFIT_DATA_COL_S =    2;
const int JVFIT_DATA_COL_DJDV = 3; //Will be DS/DV for Suns-Voc
const int JVFIT_N_DATA_COLS =   4;


class JVFit{
    public:
        JVFit(double *inputI, double *inputV, double *inputS, int nPoints);
        ~JVFit(void);
        
        void setData(const double *inputI, const double *inputV, const double *inputS, const int nPoints);
  void setOption(const int nOption, const int option);
  void setInput(const int nInput, const double input);
        
  int doFit(void);
  int doSkippedFit(void);
        void getParams(double *params);
  void getParamVariance(double *paramVariance);
  double getRs(void);
       
    private:
        
        double *inputI_;
        double *inputV_;
        double *inputS_;
        
       
        int option_[JVFIT_N_OPTIONS]; 
  double input_[JVFIT_N_INPUTS];
  
        int nPoints_;
        int nParams_;
        bool whichParamsToFit_[JVFIT_PARAM_MAX];

        double *fixedJVSD_;
        double params_[JVFIT_PARAM_MAX];
  double paramVariance_[JVFIT_PARAM_MAX];
        double sumOfSquares_;
        
        int fixInputData();
        int smoothData();
        int checkParamScheme();
        int bindModelToLsq(LeastSquares &, TwoDiodeModel &, LsqColumnCallback &);
        int doActualFit(LeastSquares &, TwoDiodeModel &);
        int fetchParams (LeastSquares &);
        
        //Callback for Least Squares
        void calcWeight(double *, double *);
        
        
        
};   

//Callback for qsort
int jvfitCompareArray(const void *a, const void *b);
   


#endif //JV_FIT_H
