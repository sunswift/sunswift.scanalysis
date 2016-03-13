#ifndef DECOMPOSE_H
#define DECOMPOSE_H
/*
  Name: decompose.h
  Copyright: 
  Author: Bonne Eggleston
  Date: 03/09/04 11:27
  Description: Functions to decompose matricies and solve matrix equations.
  TODO: Do matrix size checking
  TODO: Implement other decomposition methods
  TODO: Don't change the input matrix
*/

#include <math.h>

const int DECOMPOSE_ERROR_NONE =            0;
const int DECOMPOSE_ERROR_CHOL_NOT_POSDEF = 1;
const int DECOMPOSE_ERROR_NO_SUCH_METHOD =  2;
const int DECOMPOSE_ERROR_NO_SOLUTION =     3;

const int DECOMPOSE_METHOD_CHOL = 1;


class Decomposition{
    public:
        Decomposition(double *matrix, int nPoints, int decompositionMethod);
        ~Decomposition(void);
        int decompose(void);
        int solve(double *b, double *x);
        
        
        
    private:
        int decomposeChol(void);
        int solveChol(double *b, double *x);
         
        double *matrix_;
        double *diagonal_;
        
        int nPoints_;
        
        int decompositionMethod_;
};    



#endif //DECOMPOSE_H
