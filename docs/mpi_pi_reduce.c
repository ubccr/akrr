/**********************************************************************
 * FILE: mpi_pi_reduce.c
 * OTHER FILES: dboard.c
 * DESCRIPTION:  
 *   MPI pi Calculation Example - C Version 
 *   Collective Communication example:  
 *   This program calculates pi using a "dartboard" algorithm.  See
 *   Fox et al.(1988) Solving Problems on Concurrent Processors, vol.1
 *   page 207.  All processes contribute to the calculation, with the
 *   master averaging the values for pi. This version uses mpc_reduce to 
 *   collect results
 * AUTHOR: Blaise Barney. Adapted from Ros Leibensperger, Cornell Theory
 *   Center. Converted to MPI: George L. Gusciora, MHPCC (1/95) 
 * LAST REVISED: 06/13/13 Blaise Barney
 * 
 * 
 * 03/09/2015 Modifide for application kernel installation tutorial
 *      added input file reading, timing and GDaPS calculations
 * 
**********************************************************************/



#include "mpi.h"
#include <stdio.h>
#include <stdlib.h>

void srandom (unsigned seed);
double dboard (int darts);
int DARTS=50000;     /* number of throws at dartboard */
int ROUNDS=10;      /* number of times "darts" is iterated */
#define MASTER 0        /* task ID of master task */

int main (int argc, char *argv[])
{
    double    homepi,         /* value of pi calculated by current task */
        pisum,            /* sum of tasks' pi values */
        pi,            /* average of pi after "darts" is thrown */
        avepi;            /* average pi value for all iterations */
    int    taskid,            /* task ID - also used as seed number */
        numtasks,       /* number of tasks */
        rc,             /* return code */
        i;
    double  t1, t2;
    MPI_Status status;

    /* Obtain number of tasks and task ID */
    MPI_Init(&argc,&argv);
    MPI_Comm_size(MPI_COMM_WORLD,&numtasks);
    MPI_Comm_rank(MPI_COMM_WORLD,&taskid);
    printf ("MPI task %d has started...\n", taskid);
    
    /* Read input file */
    if(argc!=2){
        if(taskid==MASTER){
            printf("usage: mpi_pi_reduce input_file\n",argc);
        }
        exit(1);
    }
    
    fflush(stdout);
    MPI_Barrier(MPI_COMM_WORLD);
    if(taskid==MASTER){
        printf("version: 2015.3.9\n",argc);
    }
    DARTS=0;
    ROUNDS=0;
    if(taskid==MASTER){
        while(1)
        {
            FILE * fin=fopen(argv[1],"r");
            if(fin==NULL){
                printf("ERROR: Can not open input file: %s\n",argv[1]);
                fclose(fin);
                break;
            }
            char ctmp[512];
            if(fgets (ctmp , 512 , fin) == NULL){
                printf("ERROR: Can not read input file: %s\n",argv[1]);
                fclose(fin);
                break;
            }
            DARTS=atoi(ctmp);
            if(DARTS <= 0){
                printf("ERROR: incorrect value for DARTS: %s\n",argv[1]);
                fclose(fin);
                break;
            }
            if(fgets (ctmp , 512 , fin) == NULL){
                printf("ERROR: Can not read input file: %s\n",argv[1]);
                fclose(fin);
                break;
            }
            ROUNDS=atoi(ctmp);
            if(ROUNDS<=0){
                printf("ERROR: incorrect value for ROUNDS: %s\n",argv[1]);
                fclose(fin);
                break;
            }
            fclose(fin);
            printf("number of throws at dartboard: %d\n",DARTS);
            printf("number of rounds for dartz throwing %d\n",ROUNDS);
            break;
        }
    }
    
    MPI_Bcast(&DARTS,1,MPI_INT,MASTER,MPI_COMM_WORLD);
    MPI_Bcast(&ROUNDS,1,MPI_INT,MASTER,MPI_COMM_WORLD);
    
    
    if(ROUNDS<=0||DARTS<=0){
        exit(1);
    }
    fflush(stdout);
    MPI_Barrier(MPI_COMM_WORLD);
    
    
    /* Set seed for random number generator equal to task ID */
    srandom (taskid);
    
    t1=MPI_Wtime();

    avepi = 0;
    for (i = 0; i < ROUNDS; i++) {
        /* All tasks calculate pi using dartboard algorithm */
        homepi = dboard(DARTS);

        /* Use MPI_Reduce to sum values of homepi across all tasks 
            * Master will store the accumulated value in pisum 
            * - homepi is the send buffer
            * - pisum is the receive buffer (used by the receiving task only)
            * - the size of the message is sizeof(double)
            * - MASTER is the task that will receive the result of the reduction
            *   operation
            * - MPI_SUM is a pre-defined reduction function (double-precision
            *   floating-point vector addition).  Must be declared extern.
            * - MPI_COMM_WORLD is the group of tasks that will participate.
            */

        rc = MPI_Reduce(&homepi, &pisum, 1, MPI_DOUBLE, MPI_SUM,
                        MASTER, MPI_COMM_WORLD);
        if (rc != MPI_SUCCESS)
            printf("%d: failure on mpc_reduce\n", taskid);

        /* Master computes average for this iteration and all iterations */
        if (taskid == MASTER) {
            pi = pisum/numtasks;
            avepi = ((avepi * i) + pi)/(i + 1); 
            printf("   After %8d throws, average value of pi = %10.8f\n",
                    (DARTS * (i + 1)),avepi);
        }
    }
    t2=MPI_Wtime(); 
    fflush(stdout);
    MPI_Barrier(MPI_COMM_WORLD);
    
    if (taskid == MASTER){
        printf ("\nReal value of PI: 3.1415926535897 \n");
        double t=t2-t1;
        printf ("Time for PI calculation: %.3f\n",t);
        printf ("Giga Darts Throws per Second (GDaPS): %.3f\n",((double)numtasks*(double)DARTS*(double)ROUNDS)/t/1.0e9);
        
    }

    MPI_Finalize();
    return 0;
}



/**************************************************************************
* subroutine dboard
* DESCRIPTION:
*   Used in pi calculation example codes. 
*   See mpi_pi_send.c and mpi_pi_reduce.c  
*   Throw darts at board.  Done by generating random numbers 
*   between 0 and 1 and converting them to values for x and y 
*   coordinates and then testing to see if they "land" in 
*   the circle."  If so, score is incremented.  After throwing the 
*   specified number of darts, pi is calculated.  The computed value 
*   of pi is returned as the value of this function, dboard. 
*
*   Explanation of constants and variables used in this function:
*   darts       = number of throws at dartboard
*   score       = number of darts that hit circle
*   n           = index variable
*   r           = random number scaled between 0 and 1
*   x_coord     = x coordinate, between -1 and 1
*   x_sqr       = square of x coordinate
*   y_coord     = y coordinate, between -1 and 1
*   y_sqr       = square of y coordinate
*   pi          = computed value of pi
****************************************************************************/

double dboard(int darts)
{
    #define sqr(x)    ((x)*(x))
    long random(void);
    double x_coord, y_coord, pi, r; 
    int score, n;
    unsigned int cconst;  /* must be 4-bytes in size */
    /*************************************************************************
    * The cconst variable must be 4 bytes. We check this and bail if it is
    * not the right size
    ************************************************************************/
    if (sizeof(cconst) != 4) {
        printf("Wrong data size for cconst variable in dboard routine!\n");
        printf("See comments in source file. Quitting.\n");
        exit(1);
    }
    /* 2 bit shifted to MAX_RAND later used to scale random number between 0 and 1 */
    cconst = 2 << (31 - 1);
    score = 0;

    /* "throw darts at board" */
    for (n = 1; n <= darts; n++)  {
        /* generate random numbers for x and y coordinates */
        r = (double)random()/cconst;
        x_coord = (2.0 * r) - 1.0;
        r = (double)random()/cconst;
        y_coord = (2.0 * r) - 1.0;

        /* if dart lands in circle, increment score */
        if ((sqr(x_coord) + sqr(y_coord)) <= 1.0)
            score++;
    }

    /* calculate pi */
    pi = 4.0 * (double)score/(double)darts;
    return(pi);
} 


