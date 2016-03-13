#ifndef JV_FIT_DLL_H
#define JV_FIT_DLL_H
/*
  Name: jvfitdll.h
  Copyright: 
  Author: Bonne Eggleston
  Date: 16/09/04 11:27
  Description: dll interface for vb or other to jvfit.dll

*/
#include "jvfit.h"
#include "jvcalc.h"

#if BUILDING_DLL
#define DLLIMPORT __declspec (dllexport) //__attribute__((stdcall)) extern "C" 
#else /* Not BUILDING_DLL */
#define DLLIMPORT __declspec (dllimport)
#endif /* Not BUILDING_DLL */


int doJVFit(double *inputI, double *inputV, double *inputS, int nPoints, double *params, double *paramVariance, 
    double *doubleOptions, int *useDoubleOptions, int *intOptions, int *useIntOptions);
int calcJVCurve (const double *inputJ, const double *inputV, const double *inputS, const int nPoints, 
    double *params, double *outputJ, double *outputV, double *tempC);
double calcSGivenJVS(const double *j, const double *v, const double *s, double *params, double *tempC);
double calcJscGivenS(const double *s, double *params, double *tempC);
int calcJmpVmpGivenS(const double *s, double *jmp, double *vmp, double *params, double *tempC);
int calcVocGivenS(const double *s, double *vOut, double *params, double *tempC);
int getVersion(void);



#endif //JV_FIT_DLL_H
