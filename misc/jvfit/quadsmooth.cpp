/*
  Name: quadsmooth.cpp
  Copyright: 
  Author: Bonne Eggleston
  Date: 03/09/04 11:27
  Description: Does quadratic smoothing over a set of xy points, and calculates 
               the smoothed value as well as the derivative. It uses linar least
               squares fitting. Expects values[2i + j] 
               where i is the pair number and j=0 for x, j=1 for y.
*/

#include "quadsmooth.h"
//#include <stdio.h>

//Calcs least squares fit to equation y = a + bx + cx2
//Expects arrays with inputs[0] = x, inputs[1] = y

int QuadSmooth::fitCurve(void){
    if(lsq_.calcLeastSquares() == LEASTSQ_ERROR_NONE){
        params_[0] = lsq_.getParam(0);
        params_[1] = lsq_.getParam(1);
        params_[2] = lsq_.getParam(2);
        return QUADSMOOTH_ERROR_NONE;
    }
    else {
        params_[0] = 0.0;
        params_[1] = 0.0;
        params_[2] = 0.0;
        return QUADSMOOTH_ERROR_BAD_FIT;    
    }    
}    


double QuadSmooth::calcYGivenX(double *X){
    return params_[0] + params_[1]* (*X) + params_[2] * (*X) * (*X);   
}    

double QuadSmooth::calcdYdXGivenX(double *X){
    return params_[1] + 2 * params_[2] * (*X);
}    



QuadSmooth::QuadSmooth(double *values, int nPoints, int nColumns) : values_(values), 
                       nPoints_(nPoints), nColumns_(nColumns), 
                       lsq_(LeastSquares(values, nPoints,nColumns,3)), //3 is for a,b,c in quadratic
                       getX_(LsqColumnCallback(QUADSMOOTH_COLUMN_X_DEFAULT)), 
                       getY_(LsqColumnCallback(QUADSMOOTH_COLUMN_Y_DEFAULT)),
                       get1_(LsqConstantCallback(1.0))
{
    //Bind the callbacks for leastsquares to our functions. (Using fastdelegates)
    lsq_.setBasisFunction(0, MakeDelegate(&get1_, &LsqConstantCallback::Callback));
    lsq_.setBasisFunction(1, MakeDelegate(&getX_, &LsqColumnCallback::Callback));
    lsq_.setBasisFunction(2, MakeDelegate(this, &QuadSmooth::calcCcoeff));
    lsq_.setWeightsFunction(MakeDelegate(&get1_, &LsqConstantCallback::Callback));
    lsq_.setVectorFunction(MakeDelegate(&getY_, &LsqColumnCallback::Callback));
    
    columnX_ = QUADSMOOTH_COLUMN_X_DEFAULT;
    columnY_ = QUADSMOOTH_COLUMN_Y_DEFAULT;

}    

void QuadSmooth::setXYs(double *values, int nPoints){
    values_ = values;
    nPoints_ = nPoints;
    lsq_.setXYs(values_,nPoints_);
    return;
}    

void QuadSmooth::setColumnX(int columnX){
    columnX_ = columnX;
    getX_.setColumn(columnX);
}

void QuadSmooth::setColumnY(int columnY){
    columnY_ = columnY;
    getY_.setColumn(columnY);
}
   
void QuadSmooth::calcCcoeff(double *inputs, double *value){
    *value = inputs[columnX_]*inputs[columnX_];
    return;
}    


    
