walllimit=20 #used to be 13

parser="xdmod.app.chem.gamess.py"

#path to run script relative to AppKerDir on particular resource
executable="execs"
input="inputs/gamess/c8h10-cct-mp2.inp"

runScriptPreRun="""#create working dir
export AKRR_TMP_WORKDIR=`mktemp -d {networkScratch}/gamess.XXXXXXXXX`
echo "Temporary working directory: $AKRR_TMP_WORKDIR"
cd $AKRR_TMP_WORKDIR

#Copy inputs
cp {appKerDir}/{input} ./
INPUT=$(echo {appKerDir}/{input} | xargs basename )
"""

runScriptPostRun="""#clean-up
cd $AKRR_TASK_WORKDIR
if [ "${{AKRR_DEBUG=no}}" = "no" ]
then
        echo "Deleting temporary files"
        rm -rf $AKRR_TMP_WORKDIR
else
        echo "Copying temporary files"
        cp -r $AKRR_TMP_WORKDIR workdir
        rm -rf $AKRR_TMP_WORKDIR
fi
"""

akrrRunAppKernelTemplate="""ATTEMPTS_TO_LAUNCH=0
while ! grep -q "EXECUTION OF GAMESS TERMINATED NORMALLY" $AKRR_APP_STDOUT_FILE
do
    echo "Attempt to launch GAMESS: $ATTEMPTS_TO_LAUNCH" >> $AKRR_APP_STDOUT_FILE 2>&1
    echo "Attempt to launch GAMESS: $ATTEMPTS_TO_LAUNCH"
    rm -rf *
    mkdir scr
    mkdir supout
    cp {appKerDir}/{input} ./
    $RUN_APPKERNEL >> $AKRR_APP_STDOUT_FILE 2>&1
    
    if [ "$ATTEMPTS_TO_LAUNCH" -ge 6 ]; then
        break
    fi
    
    ((ATTEMPTS_TO_LAUNCH++))
done
writeToGenInfo "attemptsToLaunch" "$ATTEMPTS_TO_LAUNCH"
echo "Total attempt to launch GAMESS is $ATTEMPTS_TO_LAUNCH"
"""
