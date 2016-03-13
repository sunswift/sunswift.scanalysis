/*
  Name: decompose.cpp
  Copyright: 
  Author: Bonne Eggleston
  Date: 03/09/04 11:27
  Description: Functions to decompose matricies and solve matrix equations.
*/

#include "decompose.h"


//Takes in an array m (matrix) with dimension nxn, and decomposes it using 
//cholesky decomposition.
//NB. The matrix must be positive-definite symmetric (as in AtA would be from Least Squares fitting)
//The lower diagonal is changed, and the diagonal is returned in d.
//TODO: Make sure that the input matrix not overridden

int Decomposition::decompose(void){
    if (decompositionMethod_ == DECOMPOSE_METHOD_CHOL){
        return decomposeChol();
    }
    else return DECOMPOSE_ERROR_NO_SUCH_METHOD;
}

int Decomposition::solve(double *b, double *x){
        if (decompositionMethod_ == DECOMPOSE_METHOD_CHOL){
        return solveChol(b, x);
    }
    else return DECOMPOSE_ERROR_NO_SUCH_METHOD;   
}    


int Decomposition::decomposeChol(void)
{
    int i, j, k;
    i=0;
    j=0;
    k=0;
    double sum = 0.0;
    
    for (i = 0; i < nPoints_; i++){
        for (j = i; j < nPoints_; j++){
            sum = matrix_[i * nPoints_ + j];
            for (k = i - 1; k >= 0; k--) 
                sum -= matrix_[i * nPoints_ + k] * matrix_[j * nPoints_ + k];    
           
            //For diagonal elements
            if (i == j){ 
                if (sum <= 0.0) 
                    return DECOMPOSE_ERROR_CHOL_NOT_POSDEF; //TODO: Do something more sensible with singular matricies.
                diagonal_[i] = sqrt(sum);
            }else matrix_[j * nPoints_ + i] = sum / diagonal_[i];
        }        
    } 
    return DECOMPOSE_ERROR_NONE;    
}



//Solves Ax=b where m (above and including the diagonal) is from A,
//and below the diagonal is from L (where LLt = A), and d is the diagonal vector
//from L
int Decomposition::solveChol (double *b, double *x)
{
    int i, k;
    double sum = 0.0;
    
    //Solve L · y = b, storing y in x.
    for (i = 0; i < nPoints_; i++) {
        if (diagonal_[i] == 0)
            return DECOMPOSE_ERROR_NO_SOLUTION;
        sum = b[i];
        for (k = i - 1;k >= 0; k--) 
            sum -= matrix_[i * nPoints_ + k] * x[k];
        x[i] = sum / diagonal_[i];
    }
    
    //Solve Lt · x = y.
    for (i = nPoints_ - 1; i >= 0; i--) { 
        sum = x[i];
        for (k = i + 1; k < nPoints_; k++) 
            sum -= matrix_[k * nPoints_ + i] * x[k];
        x[i] = sum / diagonal_[i];
    }
    return DECOMPOSE_ERROR_NONE; 
}    


Decomposition::Decomposition(double *matrix, int nPoints, int decompositionMethod) 
                            : matrix_(matrix), nPoints_(nPoints), decompositionMethod_(decompositionMethod){
    
    diagonal_ = new double[nPoints];
    
    for (int i = 0; i < nPoints; i++){
        diagonal_[i] = 0;
    }    
    
}

Decomposition::~Decomposition(void){
    delete [] diagonal_;
}

        
    


