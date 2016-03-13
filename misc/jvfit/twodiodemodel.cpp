/*
  Name: twodiode.cpp
  Copyright: 
  Author: Bonne Eggleston
  Date: 03/09/04 11:27
  Description: Equations required for two diode model of solar cells. Can be used
               to prepare callback functions for a curve fitting program.
*/
#include "twodiodemodel.h"
#include <stdio.h>

TwoDiodeModel::TwoDiodeModel(){
    paramTempC_ = STANDARD_TEMP;
    paramVt_ = BOLTZMANN * (STANDARD_TEMP + CELC_TO_KELVIN) / ELECTRON_CHARGE; 
    paramRs_ = TWO_DIODE_MODEL_PARAM_RS_DEFAULT;
    columnJ_ = TDM_COL_J_DEFAULT;
    columnV_ = TDM_COL_V_DEFAULT;
    columnS_ = TDM_COL_S_DEFAULT;
}    

void TwoDiodeModel::setTempC(const double *tempC){
    paramVt_ = BOLTZMANN * ((*tempC) + CELC_TO_KELVIN) / ELECTRON_CHARGE;
    return;
}    

void TwoDiodeModel::setRs(const double *Rs){
    paramRs_ = *Rs;
} 

void TwoDiodeModel::setColumns(int columnJ, int columnV, int columnS){
    columnJ_ = columnJ;
    columnV_ = columnV;
    columnS_ = columnS;
}    

void TwoDiodeModel::calcJlcoeff(double *inputs, double *value){
    *value = calcJlcoeff(inputs + columnJ_, inputs + columnV_, inputs + columnS_);
    return;
}    

double TwoDiodeModel::calcJlcoeff(const double *J, const double *V, const double *S){
  return *S;
}

void TwoDiodeModel::calcJo1coeff(double *inputs, double *value){
  *value = calcJo1coeff(inputs + columnJ_, inputs + columnV_, inputs + columnS_);
  return;
}    

double TwoDiodeModel::calcJo1coeff(const double *J, const double *V, const double *S){
  return -(exp(((*V) + (*J) * paramRs_) / paramVt_) - 1);
}

void TwoDiodeModel::calcJo2coeff(double *inputs, double *value){
    *value = calcJo2coeff(inputs + columnJ_, inputs + columnV_, inputs + columnS_);
    return;
}    

double TwoDiodeModel::calcJo2coeff(const double *J, const double *V, const double *S){
  return -(exp(((*V) + (*J) * paramRs_) / (2 * paramVt_)) - 1);
}

void TwoDiodeModel::calcGshcoeff(double *inputs, double *value){
    *value = calcGshcoeff(inputs + columnJ_, inputs + columnV_, inputs + columnS_);
    return;
}   

double TwoDiodeModel::calcGshcoeff(const double *J, const double *V, const double *S){
  return -((*V) + (*J) * paramRs_);
}

void TwoDiodeModel::calcGphcoeff(double *inputs, double *value){
    *value = calcGphcoeff(inputs + columnJ_, inputs + columnV_, inputs + columnS_);
    return;
}

double TwoDiodeModel::calcGphcoeff(const double *J, const double *V, const double *S){
  return - (*S) * ((*V) + (*J) * paramRs_);
}

