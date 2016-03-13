/*
  Name: jvfitdll.c
  Copyright: 
  Author: Bonne Eggleston
  Date: 16/09/04 11:27
  Description: dll interface for vb or other to jvfit.cpp

*/

#include "jvfitdll.h"

int getVersion(void){
return 101;
}

int doJVFit(double *inputI, double *inputV, double *inputS, int nPoints, double *params, double *paramVariance, 
    double *doubleOptions, short *useDoubleOptions, int *intOptions, short *useIntOptions)
{

  double nothing[8]; //TODO: This is a hack, and without it the whole thing doesn't work. I dont know why
  int err = JVFIT_ERROR_NONE;

  JVFit jvfit(inputI, inputV, inputS, nPoints);

  for (int i = 0; i < JVFIT_N_OPTIONS; i++){
    if (useIntOptions[i] != 0)
      jvfit.setOption(i, intOptions[i]);
  }

  for (int i = 0; i < JVFIT_N_INPUTS; i++){
    if (useDoubleOptions[i] != 0)
      jvfit.setInput(i, doubleOptions[i]);
  }
  
  err = jvfit.doFit();
  //if (err != JVFIT_ERROR_NONE)
  //  return err;

  
  jvfit.getParams(params);
  params[JVFIT_PARAM_RS] = jvfit.getRs();
  jvfit.getParamVariance(paramVariance);


  return err;

}


int calcJVCurve (const double *inputJ, const double *inputV, const double *inputS, const int nPoints, 
    double *params, double *outputJ, double *outputV, double *tempC){

  JVCalc jvcalc(params);
  jvcalc.setTempC(tempC);
  jvcalc.setRs(params + JVFIT_PARAM_RS);
  for (int i = 0; i < nPoints; i++){
    jvcalc.calcJVGivenJVS(inputJ + i, inputV + i, inputS + i, outputJ + i, outputV + i);
  }
  return JVCALC_ERROR_NONE;
}

int calcSVOCCurve (const double *v, const double *s, const int nPoints, 
     double *params, double *sOut, double *tempC){
  JVCalc jvcalc(params);
  jvcalc.setTempC(tempC);
  jvcalc.setRs(params + JVFIT_PARAM_RS);

   double dummyJ = 0.0;

  for (int i = 0; i < nPoints; i++){
    sOut[i] = jvcalc.calcSGivenJVS(&dummyJ, v + i, s + i);
  }
  return JVCALC_ERROR_NONE;
}


int calcVocGivenS(const double *s, double *vOut, double *params, double *tempC){
  JVCalc jvcalc(params);
  jvcalc.setTempC(tempC);
  jvcalc.setRs(params + JVFIT_PARAM_RS);
  return jvcalc.calcVocGivenS(s, vOut);
}

int calcJmpVmpGivenS(const double *s, double *jmp, double *vmp, double *params, double *tempC){
  JVCalc jvcalc(params);
  jvcalc.setTempC(tempC);
  jvcalc.setRs(params + JVFIT_PARAM_RS);
  return jvcalc.calcJmpVmpGivenS(s, jmp, vmp);
}

double calcJscGivenS(const double *s, double *params, double *tempC){
  JVCalc jvcalc(params);
  jvcalc.setTempC(tempC);
  jvcalc.setRs(params + JVFIT_PARAM_RS);
  return jvcalc.calcJscGivenS(s);
}


double calcSGivenJVS(const double *j, const double *v, const double *s, double *params, double *tempC){
  JVCalc jvcalc(params);
  jvcalc.setTempC(tempC);
  jvcalc.setRs(params + JVFIT_PARAM_RS);
  return jvcalc.calcSGivenJVS(j, v, s);
}

