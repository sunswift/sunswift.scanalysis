#ifndef LEAST_SQUARES_H
#define LEAST_SQUARES_H
/*
  Name: leastsquares.h
  Copyright: 
  Author: Bonne Eggleston
  Date: 09/09/04 17:02
  Description: Does linear least squares fitting for arbitrary input parameters
               and basis functions. Uses delegates for basis function callback.
*/

#include "fastdelegate.h"
#include "decompose.h"



using namespace fastdelegate;


//TODO: Remove globals and use something nicer (maybe a singular class)
//TODO: Check for bad number of input/output params
//TODO: Check for unbound basis functions


const int LEASTSQ_METHOD_WEIGHT =    0;
const int LEASTSQ_METHOD_NO_WEIGHT = 1;
const int LEASTSQ_METHOD_DEFAULT =   LEASTSQ_METHOD_WEIGHT;

const int LEASTSQ_DECOMP_LU =        0;
const int LEASTSQ_DECOMP_SVD =       1;
const int LEASTSQ_DECOMP_DEFAULT =   LEASTSQ_DECOMP_LU;

const int LEASTSQ_ERROR_NONE =        0;
const int LEASTSQ_ERROR_SINGULAR =    1;
const int LEASTSQ_ERROR_TOO_FEW =     2;


//Should take an array of values (arg 1), and turn it into one value (arg 2)
//The return value should be the inverse square of the weighting for the corresponding input values.
typedef FastDelegate2<double *, double *> Function;


class LeastSquares{
    public:

        //Constructor: input values are in an array[i*num_input_params + j] where i is row number and j is column number
        //number_output_params is the number of parameters to fit (remember to allocate a callback for each)
        //number of points is the number of points to take from the array for fitting
        LeastSquares(double *valuesIn, int nPoints, int nParamsIn, int nParamsOut);
        ~LeastSquares(void);

        void setBasisFunction(const int nBasis, Function function);
        void setWeightsFunction(Function function);
        void setVectorFunction(Function function);
        void setXYs(double *valuesIn, const int nPoints);
        void setDecompMethod(const int methodDecomp);
        void setLsqMethod(const int methodLsq);
        
        void   getParams(double *);
        double getParam(int);
        void getVariances(double *);
        double getVariance(int);
        double getSumOfSq(void);
        
        int calcLeastSquares(void); //actually do the fit (return an error code)
        double calcSumOfSq(void); //calculate the sum of sq error
        int calcVariance(void); //caclulate the variance in the fit params
        

        
        
    private:
        Function *functionBases_; 
        Function functionWeights_;
        Function functionVector_;
        double *params_;
        double *variance_;
        int methodDecomp_;
        int methodLsq_;
        double *valuesIn_;
        int nPoints_;
        int nParamsIn_;
        int nParamsOut_;
        double sumOfSq_;
        double sumOfVectorSq_;
        double *matrixATA_; 
        double *vectorATB_; //TODO: Check size of dynamically allocated arrays.

               
};

//Basic column callback class for LeastSquares delgates. Can be used externally. 
class LsqColumnCallback{
    public:
        LsqColumnCallback(int column);
        void setColumn(int column);
        void Callback(double *, double *);
        
    private:
        int column_;
        
};    

class LsqConstantCallback{
    public:
        LsqConstantCallback(double constant);
        void setConstant(double constant);
        void Callback(double *, double *);
        
    private:
        double constant_;
};       


#endif //LEAST_SQUARES_H
