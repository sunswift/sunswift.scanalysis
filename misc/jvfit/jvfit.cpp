/*
Name: jvfit.cpp
Copyright: 
Author: Bonne Eggleston
Date: 03/09/04 11:27
Description: Methods for performing jv curve fitting for solar cells.
TODO: Allow for parameter disclusion (if the coefficient is really small)
*/
#include "jvfit.h" 
//#include <stdio.h>//TODO: Remove me!! last


int JVFit::doFit(void){
  int err = 0;
  //Determine how many parameters we are fitting
  err = checkParamScheme();
  if (err != JVFIT_ERROR_NONE)
    return err;

  //Prepare data for fitting (Area, pos/neg, Cells etc) and order.
  err = fixInputData();
  if (err != JVFIT_ERROR_NONE)
    return err;

  //Smooth the data and optionally calculate the derivative
  err = smoothData();
  if (err != JVFIT_ERROR_NONE)
    return err;

  err = doSkippedFit();
  if (err != JVFIT_ERROR_NONE)
    return err;

  //This skips parameters that are negative. It does so in a very slow way, however
  //as it does a full Rs fit (outer loop) for each parameter to skip
  //I think this is the only way, though. 
  if (option_[JVFIT_OPTION_USE_SKIPPING]){
    for (int i = 0; i < JVFIT_PARAM_MAX; i++){
      if ((whichParamsToFit_[JVFIT_PARAM_SKIP[i]] == true) &&
          (params_[JVFIT_PARAM_SKIP[i]] < 0.0) ){
        whichParamsToFit_[JVFIT_PARAM_SKIP[i]] = false; 
        if (JVFIT_PARAM_SKIP[i] != JVFIT_PARAM_RS)
          nParams_--;
        params_[JVFIT_PARAM_SKIP[i]] = 0.0;
        doSkippedFit();
      }    
    }    
  }
  //TODO: This part may not be needed with the skipping section that's above
  if(params_[JVFIT_PARAM_GSH] < 1/input_[JVFIT_INPUT_MAX_SHUNT] &&
      whichParamsToFit_[JVFIT_PARAM_GSH] == true){
    whichParamsToFit_[JVFIT_PARAM_GSH] = false; nParams_--;
    params_[JVFIT_PARAM_GSH] = 0.0;
    doSkippedFit();
  }

  return JVFIT_ERROR_NONE;

}   

int JVFit::doSkippedFit(void){
  int err = 0;
  //Initialise the Two Diode Model (tdm) and Least Squares (lsq) Objects.
  LeastSquares          lsq(fixedJVSD_, nPoints_, JVFIT_N_DATA_COLS, nParams_); 
  LsqColumnCallback     vectorCallback(JVFIT_DATA_COL_J);
  TwoDiodeModel         tdm;
  tdm.setTempC(input_ + JVFIT_INPUT_TEMP_C);

  //Bind Two Diode Model to basis functions in Least Squares Algorithm
  err = bindModelToLsq(lsq, tdm, vectorCallback);
  if (err != JVFIT_ERROR_NONE)
    return err;

  //Do the fit
  err = doActualFit(lsq, tdm);
  if (err != JVFIT_ERROR_NONE)
    return err;  

  //Find parameters and variance
  err = fetchParams(lsq);
  if (err != JVFIT_ERROR_NONE)
    return err;  

  return JVFIT_ERROR_NONE;


}   

int JVFit::fixInputData(void){
  int polarity = 1; // 1 for pos, -1 for neg.

  //Here we adjust for area, number of cells and polarity of current. 
  //TODO: We should also check that the data is consistent with the type of fit requested

  //The easiest way to check for polarity is to do a linear least squares fit i = mv + c
  //If m is +ve then the current is neg

  //Copy the input data straight into the jvs matrix
  for (int i = 0; i < nPoints_; i++){ 
    fixedJVSD_[JVFIT_N_DATA_COLS * i + JVFIT_DATA_COL_J] = inputI_[i]/input_[JVFIT_INPUT_CELL_AREA];
    fixedJVSD_[JVFIT_N_DATA_COLS * i + JVFIT_DATA_COL_V] = inputV_[i]/option_[JVFIT_OPTION_N_CELLS];
    fixedJVSD_[JVFIT_N_DATA_COLS * i + JVFIT_DATA_COL_S] = inputS_[i];
  }    

  //Sort the data
  if (option_[JVFIT_OPTION_SORT] == JVFIT_SORT_SCHEME_QSORT)
    qsort(fixedJVSD_, nPoints_, JVFIT_N_DATA_COLS * sizeof(double), jvfitCompareArray);

  //If fitting J Check for polarity by linear fit.
  //We know we're fittin to J if we fit Rs.
  if (whichParamsToFit_[JVFIT_PARAM_RS]){
    LeastSquares          lsq(fixedJVSD_, nPoints_, JVFIT_N_DATA_COLS,2); //X,Y inputs, m,c outputs
    LsqColumnCallback     lsqJCallback(JVFIT_DATA_COL_J);
    LsqColumnCallback     lsqVCallback(JVFIT_DATA_COL_V);
    LsqConstantCallback   lsqConstCallback(1.0);

    lsq.setBasisFunction(0, MakeDelegate(&lsqVCallback,     &LsqColumnCallback::Callback));
    lsq.setBasisFunction(1, MakeDelegate(&lsqConstCallback, &LsqConstantCallback::Callback));
    lsq.setVectorFunction(  MakeDelegate(&lsqJCallback,     &LsqColumnCallback::Callback));
    lsq.setWeightsFunction( MakeDelegate(&lsqConstCallback, &LsqConstantCallback::Callback));

    lsq.setLsqMethod(LEASTSQ_METHOD_NO_WEIGHT);
    lsq.setDecompMethod(LEASTSQ_DECOMP_LU);

    if(lsq.calcLeastSquares() == LEASTSQ_ERROR_NONE){
      if (lsq.getParam(0) > 0 ){
        polarity = -1;
      }else polarity = 1;
    } else return JVFIT_ERROR_COULD_NOT_DETERMINE_POLARITY;


    //Change polarity of current.     
    for (int i = 0; i < nPoints_; i++){
      fixedJVSD_[JVFIT_N_DATA_COLS * i + JVFIT_DATA_COL_J] *= polarity;
    }    
  }     
  return JVFIT_ERROR_NONE;    
} 


//TODO: Grouped smoothing. Should adjust J data for Suns when smoothing, and finding derivative
//Smoothes data, from fixedJVSD column, and puts it back there.
int JVFit::smoothData(void){
  //If we need to do any smoothing, or to calc di/dv for weighting
  //And the weight scheme is quadratic
  if((option_[JVFIT_OPTION_WEIGHT_SCHEME] == JVFIT_WEIGHT_SCHEME_ODR) ||
      (option_[JVFIT_OPTION_SMOOTH_SCHEME] == JVFIT_SMOOTH_SCHEME_QUAD)){

    //If there aren't enough points to smooth, then throw error
    if ((option_[JVFIT_OPTION_POINTS_TO_SMOOTH] > nPoints_) ||
        (option_[JVFIT_OPTION_POINTS_TO_SMOOTH] < 3)){
      return JVFIT_ERROR_TOO_FEW_SMOOTHING_POINTS;
    }       

    double smoothedPoints[nPoints_];
    int first = 0, last = 0;

    QuadSmooth qs(fixedJVSD_, nPoints_, JVFIT_N_DATA_COLS);
    qs.setColumnX(JVFIT_DATA_COL_V); 
    if (whichParamsToFit_[JVFIT_PARAM_RS])
      qs.setColumnY(JVFIT_DATA_COL_J); 
    else qs.setColumnY(JVFIT_DATA_COL_S);

    //else continue and do the smoothing
    for (int i = 0; i < nPoints_; i++){
      //Make sure points are in range.
      first = i - option_[JVFIT_OPTION_POINTS_TO_SMOOTH];
      if (first < 0)
        first = 0;
      last = i + option_[JVFIT_OPTION_POINTS_TO_SMOOTH];
      if (last >= nPoints_)
        last = nPoints_ - 1;

      qs.setXYs(fixedJVSD_ + JVFIT_N_DATA_COLS * first, last - first); 
      if (qs.fitCurve() == QUADSMOOTH_ERROR_NONE){

        //If we're smoothing, calculate the smoothe value
        if (option_[JVFIT_OPTION_SMOOTH_SCHEME] == JVFIT_SMOOTH_SCHEME_QUAD)
          smoothedPoints[i] = qs.calcYGivenX(fixedJVSD_ + JVFIT_N_DATA_COLS * i + JVFIT_DATA_COL_V);

        //If we are weighting, calculate the derivative
        if (option_[JVFIT_OPTION_WEIGHT_SCHEME] == JVFIT_WEIGHT_SCHEME_ODR)
          fixedJVSD_[JVFIT_N_DATA_COLS * i + JVFIT_DATA_COL_DJDV] = qs.calcdYdXGivenX(fixedJVSD_ + JVFIT_N_DATA_COLS * i + JVFIT_DATA_COL_V);

      }else { //For bad fits
        //Just don't smooth (no need to throw an error)
        //TODO: Maybe disclude poorly fitted points.           
        if (option_[JVFIT_OPTION_SMOOTH_SCHEME] == JVFIT_SMOOTH_SCHEME_QUAD)
          smoothedPoints[i] = fixedJVSD_[JVFIT_N_DATA_COLS * i + JVFIT_DATA_COL_J];
        if (option_[JVFIT_OPTION_WEIGHT_SCHEME] == JVFIT_WEIGHT_SCHEME_ODR)
          fixedJVSD_[JVFIT_N_DATA_COLS * i + JVFIT_DATA_COL_DJDV] = JVFIT_LARGE_GRADIENT;
      }    


    } 
    //Copy the smoothed points back to the original matrix
    if (option_[JVFIT_OPTION_SMOOTH_SCHEME] == JVFIT_SMOOTH_SCHEME_QUAD){
      if (whichParamsToFit_[JVFIT_PARAM_RS]){
        for (int i = 0; i < nPoints_; i++){ 
          fixedJVSD_[JVFIT_N_DATA_COLS * i + JVFIT_DATA_COL_J] = smoothedPoints[i];
        }
      }else {
        for (int i = 0; i < nPoints_; i++){ 
          fixedJVSD_[JVFIT_N_DATA_COLS * i + JVFIT_DATA_COL_S] = smoothedPoints[i];
        }
      }
    }    

  }

  return JVFIT_ERROR_NONE;
}    


int JVFit::checkParamScheme(){

  //start with all false
  for (int i = 0; i < JVFIT_PARAM_MAX; i++){
    whichParamsToFit_[i] = false;
  }   
  nParams_ = 0; 

  switch(option_[JVFIT_OPTION_PARAM_SCHEME]){
    case JVFIT_PARAM_SCHEME_TWO_DIODE_RPH_JL:
      whichParamsToFit_[JVFIT_PARAM_GPH] = true; nParams_++;
      //Fallthrough      
    case JVFIT_PARAM_SCHEME_TWO_DIODE_JL:
      whichParamsToFit_[JVFIT_PARAM_JO2] = true; nParams_++;
      //Fallthrough        
    case JVFIT_PARAM_SCHEME_ONE_DIODE_JL:
      whichParamsToFit_[JVFIT_PARAM_JL] = true; nParams_++;
      //Fallthrough
    case JVFIT_PARAM_SCHEME_ONE_DIODE_DJL:
      whichParamsToFit_[JVFIT_PARAM_RS] = true; //Rs not for Lsq
      //Fallthrough
    case JVFIT_PARAM_SCHEME_ONE_DIODE_SUNS_VOC:
      whichParamsToFit_[JVFIT_PARAM_JO1] = true; nParams_++;
      whichParamsToFit_[JVFIT_PARAM_GSH] = true; nParams_++;
      break;

    case JVFIT_PARAM_SCHEME_TWO_DIODE_DJL:
      whichParamsToFit_[JVFIT_PARAM_RS] = true; //Rs not for Lsq           
      //Fallthrough
    case JVFIT_PARAM_SCHEME_TWO_DIODE_SUNS_VOC:
      whichParamsToFit_[JVFIT_PARAM_JO2] = true; nParams_++;
      whichParamsToFit_[JVFIT_PARAM_JO1] = true; nParams_++;
      whichParamsToFit_[JVFIT_PARAM_GSH] = true; nParams_++;            
      break;      

    default:
      return JVFIT_ERROR_PARAM_SCHEME_NOT_EXIST;
      break;   
  }    

  return JVFIT_ERROR_NONE;   
}


int JVFit::bindModelToLsq(LeastSquares &lsq, TwoDiodeModel &tdm, LsqColumnCallback &vectorCallback){

  int i = 0;
  if (whichParamsToFit_[JVFIT_PARAM_JL] == true){
    lsq.setBasisFunction(i, MakeDelegate(&tdm, &TwoDiodeModel::calcJlcoeff));
    i++;
  }
  if (whichParamsToFit_[JVFIT_PARAM_JO1] == true){
    lsq.setBasisFunction(i, MakeDelegate(&tdm, &TwoDiodeModel::calcJo1coeff));
    i++;
  }
  if (whichParamsToFit_[JVFIT_PARAM_JO2] == true){
    lsq.setBasisFunction(i, MakeDelegate(&tdm, &TwoDiodeModel::calcJo2coeff));
    i++;
  }    
  if (whichParamsToFit_[JVFIT_PARAM_GSH] == true){
    lsq.setBasisFunction(i, MakeDelegate(&tdm, &TwoDiodeModel::calcGshcoeff));
    i++;
  }
  if (whichParamsToFit_[JVFIT_PARAM_GPH] == true){
    lsq.setBasisFunction(i, MakeDelegate(&tdm, &TwoDiodeModel::calcGphcoeff));
    i++;
  }
  if (whichParamsToFit_[JVFIT_PARAM_RS] == true){
    vectorCallback.setColumn(JVFIT_DATA_COL_J);
  }else vectorCallback.setColumn(JVFIT_DATA_COL_S);

  lsq.setVectorFunction(MakeDelegate(&vectorCallback, &LsqColumnCallback::Callback));
  lsq.setWeightsFunction(MakeDelegate(this, &JVFit::calcWeight)); 
  //Take out weighting if not needed. 
  if (option_[JVFIT_OPTION_WEIGHT_SCHEME] == JVFIT_WEIGHT_SCHEME_NONE)
    lsq.setLsqMethod(LEASTSQ_METHOD_NO_WEIGHT);
  else lsq.setLsqMethod(LEASTSQ_METHOD_WEIGHT);

  return JVFIT_ERROR_NONE; 

}    

void JVFit::calcWeight(double *inputs, double *value){
  if (JVFIT_WEIGHT_SCHEME_ODR == option_[JVFIT_OPTION_WEIGHT_SCHEME]){
    if(whichParamsToFit_[JVFIT_PARAM_RS]){
      *value = 1 / ((input_[JVFIT_INPUT_I_JITTER] * input_[JVFIT_INPUT_I_JITTER]) + 
          (input_[JVFIT_INPUT_V_JITTER] * inputs[JVFIT_DATA_COL_DJDV]) * 
          (input_[JVFIT_INPUT_V_JITTER] * inputs[JVFIT_DATA_COL_DJDV]));
    } else {
      *value = 1 / ((input_[JVFIT_INPUT_S_JITTER] * input_[JVFIT_INPUT_S_JITTER]) + 
          (input_[JVFIT_INPUT_V_JITTER] * inputs[JVFIT_DATA_COL_DJDV]) * 
          (input_[JVFIT_INPUT_V_JITTER] * inputs[JVFIT_DATA_COL_DJDV]));
    }

  } else *value = 1;

  return;
}    

//TODO: Add error returns for actualfit loops from lsq. (Maybe) 
int JVFit::doActualFit(LeastSquares &lsq, TwoDiodeModel &tdm){

  //Do a basic fit if no Rs Fitting
  if (whichParamsToFit_[JVFIT_PARAM_RS] == false){
    double dummy = 0.0;
    tdm.setRs(&dummy);
    lsq.calcLeastSquares();
    sumOfSquares_ = lsq.calcSumOfSq();
  } else { //Do a complex fit if we are Rs Fitting

    double rs[5], sumsq[5];
    int nLoop=0;
    for (int i = 0; i < 5; i++){
      rs[i] = 0;
      sumsq[i] = 0;
    }

    //Get first three guesses. 
    for (int i = 0; i < 3; i++){
      rs[2 * i] = JVFIT_RS_STEP_INITIAL * i;
      tdm.setRs(rs + 2* i);
      lsq.calcLeastSquares();
      sumsq[2 * i] = lsq.calcSumOfSq();
    }



    //Shift along in Rs until we are around the min point. 
    while ((sumsq[4] < sumsq[2] ) ||
        (sumsq[0] < sumsq[2] )){
      nLoop++;
      if (nLoop > JVFIT_RS_LOOP_MAX){
        params_[JVFIT_PARAM_RS] = rs[2];
        return JVFIT_ERROR_RS_LOOP_MAX_EXCEEDED;
      }
      //Move along one more step
      sumsq[0] = sumsq[2]; rs[0] = rs[2];
      sumsq[2] = sumsq[4]; rs[2] = rs[4];

      rs[4] = rs[2] + JVFIT_RS_STEP_INITIAL;

      tdm.setRs(rs + 4);
      lsq.calcLeastSquares();
      sumsq[4] = lsq.calcSumOfSq();
    } 

    //Now that we are centered over the min, focus it down
    while (rs[2] - rs[0] > input_[JVFIT_INPUT_RS_TOLL]){
      nLoop++;
      if (nLoop > JVFIT_RS_LOOP_MAX){
        params_[JVFIT_PARAM_RS] = rs[2];
        return JVFIT_ERROR_RS_LOOP_MAX_EXCEEDED;
      }

      rs[3] = (rs[2] + rs[4]) / 2;
      tdm.setRs(rs + 3);
      lsq.calcLeastSquares();
      sumsq[3] = lsq.calcSumOfSq();
      if (sumsq[3] < sumsq[2]){
        sumsq[0] = sumsq[2]; rs[0] = rs[2];
        sumsq[2] = sumsq[3]; rs[2] = rs[3];
      }else {
        rs[1] = (rs[0] + rs[2]) / 2;
        tdm.setRs(rs + 1);
        lsq.calcLeastSquares();
        sumsq[1] = lsq.calcSumOfSq();
        if (sumsq[1] < sumsq[2]){ 
          sumsq[4] = sumsq[2]; rs[4] = rs[2];
          sumsq[2] = sumsq[1]; rs[2] = rs[1];
        }else {
          sumsq[4] = sumsq[3]; rs[4] = rs[3];
          sumsq[0] = sumsq[1]; rs[0] = rs[1];
        }
      }
    }
    params_[JVFIT_PARAM_RS] = rs[2];
    sumOfSquares_ = sumsq[2];

  }       

  return JVFIT_ERROR_NONE;
}


int JVFit::fetchParams(LeastSquares &lsq){              
  //Find basic parameters
  int n = 0;
  for (int i = 0; i < JVFIT_PARAM_MAX; i++){
    if ((whichParamsToFit_[i] == true) && (i != JVFIT_PARAM_RS)){
      if (whichParamsToFit_[JVFIT_PARAM_RS]){
        params_[i] = lsq.getParam(n);
        n++;
      }else {
        params_[i] = - lsq.getParam(n) * input_[JVFIT_INPUT_JL];
        n++;
      }
    } 
  }    

  //Rs is added to the param array during fitting. 

  //Find variance in basic parameters
  lsq.calcVariance();
  n = 0;
  for (int i = 0; i < JVFIT_PARAM_MAX; i++){
    if ((whichParamsToFit_[i] == true) && (i != JVFIT_PARAM_RS)){
      if (whichParamsToFit_[JVFIT_PARAM_RS]){
        paramVariance_[i] = lsq.getVariance(n);
        n++;
      }else {
        paramVariance_[i] = lsq.getVariance(n) * input_[JVFIT_INPUT_JL];
        n++;
      }    
    } 
  } 
  return JVFIT_ERROR_NONE;
}   



//Constructor
JVFit::JVFit (double *inputI, double *inputV, double *inputS, int nPoints) : 
  inputI_(inputI), inputV_(inputV), inputS_(inputS), nPoints_(nPoints){

    option_[JVFIT_OPTION_WEIGHT_SCHEME] =   JVFIT_WEIGHT_SCHEME_DEFAULT;
    option_[JVFIT_OPTION_FIT_SCHEME] =      JVFIT_FIT_SCHEME_DEFAULT;
    option_[JVFIT_OPTION_SMOOTH_SCHEME] =   JVFIT_SMOOTH_SCHEME_DEFAULT;
    option_[JVFIT_OPTION_POINTS_TO_SMOOTH] = JVFIT_POINTS_TO_SMOOTH_DEFAULT;
    option_[JVFIT_OPTION_PARAM_SCHEME] =    JVFIT_PARAM_SCHEME_DEFAULT;
    option_[JVFIT_OPTION_N_CELLS] =          JVFIT_N_CELLS_DEFAULT;
    option_[JVFIT_OPTION_SORT] =    JVFIT_SORT_SCHEME_DEFAULT;
    option_[JVFIT_OPTION_USE_SKIPPING] =    JVFIT_USE_SKIPPING_DEFAULT;

    input_[JVFIT_INPUT_CELL_AREA] =        JVFIT_CELL_AREA_DEFAULT;
    input_[JVFIT_INPUT_RS_TOLL] =    JVFIT_RS_TOLLERANCE_DEFAULT;
    input_[JVFIT_INPUT_MAX_SHUNT] =        JVFIT_MAX_SHUNT_DEFAULT;
    input_[JVFIT_INPUT_JL] =              JVFIT_JL_DEFAULT;
    input_[JVFIT_INPUT_TEMP_C] =      JVFIT_TEMPC_DEFAULT;
    input_[JVFIT_INPUT_V_JITTER] =         JVFIT_V_JITTER_DEFAULT/JVFIT_N_CELLS_DEFAULT;  
    input_[JVFIT_INPUT_I_JITTER] =         JVFIT_I_JITTER_DEFAULT/JVFIT_CELL_AREA_DEFAULT;   
    input_[JVFIT_INPUT_S_JITTER] =      JVFIT_S_JITTER_DEFAULT;

    fixedJVSD_ = new double[JVFIT_N_DATA_COLS * nPoints];

    for (int i = 0; i < JVFIT_N_DATA_COLS * nPoints; i++){
      fixedJVSD_[i] = 0.0;
    }

    for (int i = 0; i < JVFIT_PARAM_MAX; i++){
      whichParamsToFit_[i] = false;
      params_[i] = 0;
      paramVariance_[i] = 0;
    }    

    nParams_ = 0;
    sumOfSquares_ = 0;

  }

//Destructor
JVFit::~JVFit(void){
  delete [] fixedJVSD_;
}

void JVFit::setOption(const int nOption, const int option){
  option_[nOption] = option;

}

  void JVFit::setInput(const int nInput, const double input){
    if (nInput == JVFIT_INPUT_CELL_AREA)
      input_[JVFIT_INPUT_I_JITTER] *= input_[JVFIT_INPUT_CELL_AREA];

    input_[nInput] = input;
    if (nInput == JVFIT_INPUT_I_JITTER || nInput == JVFIT_INPUT_CELL_AREA)
      input_[JVFIT_INPUT_I_JITTER] /= input_[JVFIT_INPUT_CELL_AREA];
    if (nInput == JVFIT_INPUT_V_JITTER)
      input_[JVFIT_INPUT_V_JITTER] /= option_[JVFIT_OPTION_N_CELLS];
  }

void JVFit::getParams (double *params){
  for (int i = 0; i < JVFIT_PARAM_MAX; i++){
    params[i] = params_[i];
  }
  return;
}

double JVFit::getRs(void){
  return params_[JVFIT_PARAM_RS];
}

void JVFit::getParamVariance (double *paramVariance){
  for (int i = 0; i < nParams_; i++){
    paramVariance[i] = paramVariance_[i];
  }
  return;
}


int jvfitCompareArray(const void *a, const void *b){
  const double *aa = (const double *) a;
  const double *bb = (const double *) b;
  double aaa = aa[JVFIT_DATA_COL_V];
  double bbb = bb[JVFIT_DATA_COL_V];
  return (aaa > bbb) - (aaa < bbb);
}
