#ifndef JV_CALC_H
#define JV_CALC_H
/*
  Name: jvcalc.h
  Copyright: 
  Author: Bonne Eggleston
  Date: 20/09/04 11:27
  Description: Methods for calculating jv curves and other params from cell parameters. 
*/
#include "jvfit.h"
#include "twodiodemodel.h"


const int JVCALC_VOC_LOOP_MAX =     200;  //Loops
const double JVCALC_VOC_J_TOLL =    0.001;  //A/m2
const double JVCALC_VOC_STEP_INITIAL =    0.2;  //V

const int JVCALC_PMAX_LOOP_MAX =    200;  //Loops
const double JVCALC_PMAX_V_TOLL =     0.0001; //V
const double JVCALC_PMAX_V_STEP_INITIAL = 0.2;  //V

const int JVCALC_ERROR_NONE =       0;
const int JVCALC_ERROR_VOC_LOOPS_EXCEEDED =   1;
const int JVCALC_ERROR_PMAX_LOOPS_EXCEEDED =  2;


class JVCalc{
  public:
    JVCalc(double *params);
    ~JVCalc(void);
    int calcVocGivenS(const double *s, double *vOut);
    void calcJVGivenJVS(const double *j, const double *v, const double *s, double *jOut, double *vOut);
    int calcJmpVmpGivenS(const double *s, double *jmp, double *vmp);
    double calcJscGivenS(const double *s);
    double calcSGivenJVS(const double *j, const double *v, const double *s);

    void setTempC(const double *tempC);
    void setRs(const double *rs);

    

  private:
    double *params_;
    TwoDiodeModel tdm_;
};



#endif //JV_CALC_H
