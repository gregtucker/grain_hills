# launch_gh_dakota_local.sh: shell script to copy files and start dakota to execute
# a batch of grain hill runs

SOURCEDIR=/Users/gtucker/Documents/Papers/_InProgress/GrainHill/grain_hills/ModelRuns/WeatheringParamStudy
RUNDIR=/Users/gtucker/Runs/GrainHill/WeatheringParamStudy

echo "launch_gh_dakota_beach.sh here."
echo "  the source dir is:"
echo $SOURCEDIR
echo "  and the run dir is:"
echo $RUNDIR

echo "  copying files..."
cp $SOURCEDIR/dakota_param_study.in $RUNDIR
cp $SOURCEDIR/grain_hill_dakota_run_driver.py $RUNDIR
cp $SOURCEDIR/grain_hill_run_config.py $RUNDIR

echo "  launching Dakota..."
cd $RUNDIR
dakota -i dakota_param_study.in -o dakota.out # > run.log &
echo "launch_gh_dakota_beach.sh DONE."
