/*
  Name: jvcalc.cpp
  Copyright: 
  Author: Bonne Eggleston
  Date: 20/09/04 11:27
  Description: Methods for calculating jv curves and other params from cell parameters. 
*/

#include "jvcalc.h"


int JVCalc::calcVocGivenS(const double *s, double *vOut){

  //x is v + j*rs. 
  double x[2], j[2];
  double dummyJ = 0;
  double v;
        int nLoop = 0;
  double step = JVCALC_VOC_STEP_INITIAL; 
  
        for (int i = 0; i < 2; i++){
            x[i] = 0;
            j[i] = 10;
        }
        
        
  //Shift along in x until we cross 0
  while (j[0] > JVCALC_VOC_J_TOLL){
    nLoop++;
    if (nLoop > JVCALC_VOC_LOOP_MAX)
      return JVCALC_ERROR_VOC_LOOPS_EXCEEDED;
    //Move along one more step
    
    x[1] = x[0] + step;
    calcJVGivenJVS(&dummyJ, x + 1, s, j + 1, &v); //Input the already fixed voltage, and assume j = 0
    
    if (j[1] < 0.0) 
      {step /= 2.0;}
    else 
      {x[0] = x[1]; j[0] = j[1];}
  } 

  *vOut = v;
  return JVCALC_ERROR_NONE;
}

void JVCalc::calcJVGivenJVS(const double *j, const double *v, const double *s, double *jOut, double *vOut){
  *jOut =  params_[JVFIT_PARAM_JL]  * tdm_.calcJlcoeff( j, v, s);
  *jOut += params_[JVFIT_PARAM_JO1] * tdm_.calcJo1coeff(j, v, s);
  *jOut += params_[JVFIT_PARAM_JO2] * tdm_.calcJo2coeff(j, v, s);
  *jOut += params_[JVFIT_PARAM_GSH] * tdm_.calcGshcoeff(j, v, s);
  *jOut += params_[JVFIT_PARAM_GPH] * tdm_.calcGphcoeff(j, v, s);

  *vOut = (*v) + ((*j) - (*jOut)) * params_[JVFIT_PARAM_RS];

  return;
}


int JVCalc::calcJmpVmpGivenS(const double *s, double *jmp, double *vmp){

        double x[5], p[5];
          double j = 0, v = 0;
          double dummyJ = 0;
        int nLoop = 0;
        for (int i = 0; i < 5; i++){
            x[i] = 0;
            p[i] = 0;
        }
        
        //Get first three guesses. 
        for (int i = 0; i < 3; i++){
            x[2 * i] = JVCALC_PMAX_V_STEP_INITIAL * i;
      calcJVGivenJVS(&dummyJ, x + 1, s, &j, &v);
            p[2 * i] = j * (x[2 * i] - j * params_[JVFIT_PARAM_RS]);
        }
        
        
        //Shift along in Rs until we are around the max point. 
        while ((p[4] > p[2] ) ||
               (p[0] > p[2] )){
            nLoop++;
            if (nLoop > JVCALC_PMAX_LOOP_MAX)
                return JVCALC_ERROR_PMAX_LOOPS_EXCEEDED;
            //Move along one more step
            p[0] = p[2]; x[0] = x[2];
            p[2] = p[4]; x[2] = x[4];
            
            x[4] = x[2] + JVCALC_PMAX_V_STEP_INITIAL;

      calcJVGivenJVS(&dummyJ, x + 4, s, &j, &v);
      p[4] = j * (x[4] - j * params_[JVFIT_PARAM_RS]);
        } 
        
        //Now that we are centered over the max, focus it down
        while (x[2] - x[0] > JVCALC_PMAX_V_TOLL){
            nLoop++;
            if (nLoop > JVCALC_PMAX_LOOP_MAX)
                return JVCALC_ERROR_PMAX_LOOPS_EXCEEDED;
                
            x[3] = (x[2] + x[4]) / 2;

      calcJVGivenJVS(&dummyJ, x + 3, s, &j, &v);
      p[3] = j * (x[3] - j * params_[JVFIT_PARAM_RS]);
      
            if (p[3] > p[2]){
                p[0] = p[2]; x[0] = x[2];
                p[2] = p[3]; x[2] = x[3];
            }else {
                x[1] = (x[0] + x[2]) / 2;
    calcJVGivenJVS(&dummyJ, x + 1, s, &j, &v);
    p[1] = j * (x[1] - j * params_[JVFIT_PARAM_RS]);
                if (p[1] > p[2]){ 
                    p[4] = p[2]; x[4] = x[2];
                    p[2] = p[1]; x[2] = x[1];
                }else {
                    p[4] = p[3]; x[4] = x[3];
                    p[0] = p[1]; x[0] = x[1];
                }
            }
        }
        *vmp = v;
        *jmp = j;
  
  return JVCALC_ERROR_NONE;
}

double JVCalc::calcJscGivenS(const double *s){
  double jsc = 0.0;
  double jls = 0.0;
  double dummy = 0.0;
  jls = params_[JVFIT_PARAM_JL] * tdm_.calcJlcoeff(&jsc, &dummy, s);
  
  jsc += jls;
  jsc += params_[JVFIT_PARAM_JO1] * tdm_.calcJo1coeff(&jls, &dummy, s); //Approximation
  jsc += params_[JVFIT_PARAM_JO2] * tdm_.calcJo2coeff(&jls, &dummy, s); //Approximation
  jsc /= (1 + params_[JVFIT_PARAM_RS] * params_[JVFIT_PARAM_GSH] + 
      (*s) *  params_[JVFIT_PARAM_RS] * params_[JVFIT_PARAM_GPH]);
  return jsc;
  
}

double JVCalc::calcSGivenJVS(const double *j, const double *v, const double *s){
  double suns = 0.0;
  suns = *j;
  suns -= params_[JVFIT_PARAM_JO1] * tdm_.calcJo1coeff(j, v, s); //Jo1 coeff doesn't depend on suns
  suns -= params_[JVFIT_PARAM_JO2] * tdm_.calcJo2coeff(j, v, s); //Jo2 coeff doesn't depend on suns
  suns -= params_[JVFIT_PARAM_GSH] * tdm_.calcGshcoeff(j, v, s); //Gsh coeff doesn't depend on suns
  suns -= params_[JVFIT_PARAM_GPH] * tdm_.calcGphcoeff(j, v, s); //Approximation
  suns /= params_[JVFIT_PARAM_JL];

  return suns;
}

JVCalc::JVCalc (double *params): params_(params)
{
  tdm_.setRs(params + JVFIT_PARAM_RS);
}

JVCalc::~JVCalc(void){
}

void JVCalc::setTempC(const double *tempC){
  tdm_.setTempC(tempC);
}

void JVCalc::setRs(const double *rs){
  tdm_.setRs(rs);
}
