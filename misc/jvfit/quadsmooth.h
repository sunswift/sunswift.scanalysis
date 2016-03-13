#ifndef QUADSMOOTH_H
#define QUADSMOOTH_H
/*
  Name: quadsmooth.h
  Copyright: 
  Author: Bonne Eggleston
  Date: 03/09/04 11:27
  Description: Does quadratic smoothing over a set of xy points, and calculates 
               the smoothed value as well as the derivative. It uses linar least
               squares fitting. Expects values[2i + j] 
               where i is the pair number and j=0 for x, j=1 for y.
*/


#include "leastsquares.h"

const int QUADSMOOTH_ERROR_NONE =       0;
const int QUADSMOOTH_ERROR_BAD_FIT =    1;

const int QUADSMOOTH_COLUMN_X_DEFAULT = 0;
const int QUADSMOOTH_COLUMN_Y_DEFAULT = 1;


class QuadSmooth{
    public:
        QuadSmooth(double *values, int nPoints, int nColumns);
        void setXYs( double *values, const int nPoints );
        void setColumnX(const int columnX);
        void setColumnY(const int columnY);
        void getParams(double *params);
        int fitCurve(void);
        double calcYGivenX(double *);
        double calcdYdXGivenX(double *);
        
            
    private:
        double params_[3];
        void calcCcoeff(double *, double *); //X^2,
        double *values_;
        int nPoints_;
        int nColumns_;
        LeastSquares lsq_;
        LsqColumnCallback getX_;
        LsqColumnCallback getY_;
        LsqConstantCallback get1_;
        int columnX_;
        int columnY_;
        
        
    
};  

#endif //QUADSMOOTH_H  
