#! /usr/bin/env bash
# A `qsub` submission script that runs GrainHill 
#
## Send email when the job is aborted, started, or stopped
#PBS -m abe

## Send email here
#PBS -M gtucker@colorado.edu

source /home/gtucker/.bashrc

MODEL=/home/gtucker/Runs/GrainHill/ParamStudy5x5_Mar2017/dakota_friendly_driver.py

runcmd="python $MODEL"

# Create a working directory on the compute node. Copy the contents of
# the original PBS working directory to it.
working=/state/partition1/$PBS_JOBNAME-$PBS_JOBID #${TMPDIR}
if [ ! -d $working ]; then
    mkdir $working
fi
trap "rm -rf $working" EXIT
cd $working && cp $PBS_O_WORKDIR/* .

# echo "--> Running on nodes: " `uniq $PBS_NODEFILE`
# echo "--> Number of available cpus: " $ncpu
# echo "--> Number of available nodes: " $nnodes
echo "--> Run command: " $runcmd
echo "--> Working directory: " $working
echo "init workdir: " $PBS_O_WORKDIR
$runcmd

# Copy the completed run to scratch storage.
#cp -R $working/* $PBS_O_WORKDIR
cp -R $working /scratch/gtucker/GrainHill/ParamStudy5x5_Mar2017

