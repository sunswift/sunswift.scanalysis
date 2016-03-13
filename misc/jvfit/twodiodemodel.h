#ifndef TWO_DIODE_MODEL_H
#define TWO_DIODE_MODEL_H
/*
  Name: twodiode.h
  Copyright: 
  Author: Bonne Eggleston
  Date: 03/09/04 11:27
  Description: Equations required for two diode model of solar cells. Can be used
               to prepare callback functions for a curve fitting program.
*/

#include <math.h>
//The basis functions expect an array with values in the following order:
// J,V,S,dJ/dV

const int TDM_COL_J_DEFAULT =       0;
const int TDM_COL_V_DEFAULT =       1;
const int TDM_COL_S_DEFAULT =       2;

const double BOLTZMANN =         1.38066e-23;
const double CELC_TO_KELVIN =    273.15;
const double ELECTRON_CHARGE =   1.60219e-19;
const double STANDARD_TEMP =     25.0;

const double TWO_DIODE_MODEL_PARAM_RS_DEFAULT = 0;


class TwoDiodeModel{
    public:
        TwoDiodeModel();
        void calcJlcoeff(double *inputs, double *value);
  double calcJlcoeff(const double *J, const double *V, const double *S);
        void calcJo1coeff(double *inputs, double *value);
  double calcJo1coeff(const double *J, const double *V, const double *S);
        void calcJo2coeff(double *inputs, double *value);
  double calcJo2coeff(const double *J, const double *V, const double *S);
        void calcGshcoeff(double *inputs, double *value);
  double calcGshcoeff(const double *J, const double *V, const double *S);
        void calcGphcoeff(double *inputs, double *value);
  double calcGphcoeff(const double *J, const double *V, const double *S);
        void setTempC(const double *tempC);
        void setRs(const double *rs);
        void setColumns(const int columnJ, const int columnV, const int columnS);

                                                
    private:
        int columnJ_;
        int columnV_;
        int columnS_;
        double paramRs_;
        double paramTempC_;
        double paramVt_;


        
        
};
#endif //TWO_DIODE_MODEL_H
  
