/*
  Name: leastsquares.cpp
  Copyright: 
  Author: Bonne Eggleston
  Date: 09/09/04 17:02
  Description: Does linear least squares fitting for arbitrary input parameters
               and basis functions. Uses delegates for basis function callback.
*/

#include "leastsquares.h"

int LeastSquares::calcLeastSquares(void)
{

    double vector_val = 0.0;
    double weight_val = 0.0;
    double coeffs[nParamsOut_];
    for(int j = 0; j < nParamsOut_; j++){
        vectorATB_[j] = 0.0;
        coeffs[j] = 0.0;
    }    
    
    for(int i = 0; i < nParamsOut_ * nParamsOut_; i++){
        matrixATA_[i] = 0.0;
    }           

    //Step 1 create the coefficient matrix and constant vector
    //Jump straight to the AtA and AtB step (saves memory)        
    //For each data point
    sumOfVectorSq_ = 0.0;
    for(int i = 0; i < nPoints_; i++){
        //For each parameter
        for(int j = 0; j < nParamsOut_; j++){ 
            //Calculate the coefficient for that value/parameter
            functionBases_[j](valuesIn_ + (i * nParamsIn_), coeffs + j);
        }
        //Calculate the vector value for that value
        functionVector_(valuesIn_ + i * nParamsIn_, &vector_val);
        //If we're weighting calculate the weight  for the value
        if(methodLsq_ == LEASTSQ_METHOD_WEIGHT){
            functionWeights_(valuesIn_ + i * nParamsIn_, &weight_val);
           }
        else weight_val = 1;
        //For each parameter, add the coefficient to create the ata matrix
        //We're not storing the A matrix, only AtA. This means we have to recalc
        //the coefficients for sum of squares calculations. (Could be slow)
        for(int j = 0; j< nParamsOut_; j++){
            for(int k = j; k < nParamsOut_; k++){//Only do it for the top half of the matrix
                double sum = coeffs[k] * coeffs[j] * weight_val;
                matrixATA_[j* nParamsOut_ + k] += sum;
            }            
            //Add the constant part to the atb vector
            vectorATB_[j] += coeffs[j] * vector_val * weight_val;
        }   
        
        //Add up the vector squares for Sum Of Square calculation (later)
        sumOfVectorSq_ += vector_val * vector_val * weight_val;     
    }
    
    //Decompose the matrix, then solve it for the vector. 
    Decomposition decomp(matrixATA_, nParamsOut_, DECOMPOSE_METHOD_CHOL);
    int err = 0;
    err = decomp.decompose();
    if (err != DECOMPOSE_ERROR_NONE)
        return LEASTSQ_ERROR_SINGULAR;
        
    err = decomp.solve(vectorATB_, params_);
    if (err != DECOMPOSE_ERROR_NONE)
        return LEASTSQ_ERROR_SINGULAR;   
    

    return LEASTSQ_ERROR_NONE;
    
}           

double LeastSquares::calcSumOfSq(void){
    //I use a quick method to calculate the sum of squares. 
    //Instead of calculating for each point (we have not saved the full matrix)
    //I calculate directly from the ata and atb matrix and vector. 
    //The sum of ys (over all points) must be added afterwards!
    
    int j,k;
    sumOfSq_ = 0.0;
    for(j = 0; j < nParamsOut_; j++){
        for(k = j; k < nParamsOut_; k++){
                if (k == j){
                    sumOfSq_ += params_[k] * params_[j] * matrixATA_[j * nParamsOut_ + k];
                }    
                else sumOfSq_ += 2* params_[k] * params_[j] * matrixATA_[j * nParamsOut_ + k];
        }    
    }    
    for(j = 0; j < nParamsOut_; j++){
        sumOfSq_ -= 2 * params_[j] * vectorATB_[j];
    }    
        
    sumOfSq_ += sumOfVectorSq_;
    
    return sumOfSq_;
}    

//Parameter variance is equal to the diagonal element of the inverse ATA Matrix
//We can't get away without finding the full inverse, but we only need to store the diagonal elements
int LeastSquares::calcVariance(void){
    //Since the decomposition wasn't saved from when we initialled solved, we do it again
    //Decompose the matrix
    Decomposition decomp(matrixATA_, nParamsOut_, DECOMPOSE_METHOD_CHOL);
    int err = 0;
    err = decomp.decompose();
    if (err != DECOMPOSE_ERROR_NONE)
        return LEASTSQ_ERROR_SINGULAR;  
    
    double *b, *x;
    b = new double[nParamsOut_];
    x = new double[nParamsOut_];
    //Initialise
    for (int i = 0; i < nParamsOut_; i++){
        b[i] = 0;
        x[i] = 0;
    }    
    //Find diagonal element by solving for a column of the I matrix
    for (int i = 0; i < nParamsOut_; i++){
        for (int j = 0; j < nParamsOut_; j++){
            if (i == j)
                b[j] = 1;
            else b[j] = 0;
        }
        err = decomp.solve(b,x);    
        if (err != DECOMPOSE_ERROR_NONE)
                return LEASTSQ_ERROR_SINGULAR;  
        variance_[i] = x[i];
    }    
    
    delete [] b;
    delete [] x;
    return LEASTSQ_ERROR_NONE;
    
}    




LeastSquares::LeastSquares(double *valuesIn, int nPoints, int nParamsIn, int nParamsOut)
                            : valuesIn_(valuesIn), nPoints_(nPoints), nParamsIn_(nParamsIn), 
                            nParamsOut_(nParamsOut){

    params_ =     new double[nParamsOut];
    variance_ =   new double[nParamsOut];
    matrixATA_ =  new double[nParamsOut * nParamsOut];
    vectorATB_ =  new double[nParamsOut];
    functionBases_ = new Function[nParamsOut]; 
        
    methodDecomp_ =  LEASTSQ_DECOMP_DEFAULT;
    methodLsq_ =     LEASTSQ_METHOD_DEFAULT; 
    sumOfSq_ =       0.0;
    sumOfVectorSq_ = 0.0;
    
    for (int i = 0; i < nParamsOut; i++){
        params_[i] = 0.0;
        variance_[i] = 0.0;
        vectorATB_[i] = 0.0;
    }    
    for (int i = 0; i < nParamsOut * nParamsOut; i++){
        matrixATA_[i] = 0.0;
    }    

}

LeastSquares::~LeastSquares(void){
    delete [] params_;
    delete [] matrixATA_;
    delete [] vectorATB_;
    delete [] functionBases_;
}    


void LeastSquares::setBasisFunction(int nFunction, Function function){
    functionBases_[nFunction] = function;
} 

void LeastSquares::setVectorFunction(Function function){
    functionVector_ = function;
} 

void LeastSquares::setWeightsFunction(Function function){
    functionWeights_ = function;
} 
 
void LeastSquares::setXYs(double *valuesIn, int nPoints){
    valuesIn_    = valuesIn;
    nPoints_     = nPoints;
}    
 
void LeastSquares::setDecompMethod(int methodDecomp){
    methodDecomp_ = methodDecomp;
}

void LeastSquares::setLsqMethod(int methodLsq){
    methodLsq_ = methodLsq;
}        
  
double LeastSquares::getParam(int iParam){
    return params_[iParam];
}

void LeastSquares::getParams(double *params){
    for (int i = 0; i < nParamsOut_; i++){
        params[i] = params_[i];
    }
    return;
}            

double LeastSquares::getSumOfSq(void){
    return sumOfSq_;
}

double LeastSquares::getVariance(int iParam){
    return variance_[iParam];
}    

void LeastSquares::getVariances(double *variance){
    for (int i = 0; i < nParamsOut_; i++){
        variance[i] = variance_[i];
    }
    return;
}    

LsqColumnCallback::LsqColumnCallback(int column) : column_(column){
}

void LsqColumnCallback::setColumn(int column){
    column_ = column;
}

void LsqColumnCallback::Callback(double *inputs, double *value){
    *value = inputs[column_];
}    

LsqConstantCallback::LsqConstantCallback(double constant) : constant_(constant){
}

void LsqConstantCallback::setConstant(double constant){
    constant_ = constant;
}

void LsqConstantCallback::Callback(double *inputs, double *value){
    *value = constant_;
}    
