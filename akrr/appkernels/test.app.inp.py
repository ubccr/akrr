walllimit=2

parser="test_parser.py"

#path to run script relative to AppKerDir on particular resource
executable="execs"
input="inputs"

akrrRunAppKer="""
#normally in runScriptPreRun
#create working dir
export AKRR_TMP_WORKDIR=`mktemp -d {networkScratch}/test.XXXXXXXXX`
echo "Temporary working directory: $AKRR_TMP_WORKDIR"
cd $AKRR_TMP_WORKDIR

#Generate AppKer signature
appsigcheck.sh {appKerDir}/{executable}/appsig/libelf/appsiggen > $AKRR_APP_STDOUT_FILE

echo "Checking that the shell is BASH"
echo $BASH 


#normally in runScriptPostRun
#clean-up
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

