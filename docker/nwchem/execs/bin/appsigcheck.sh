#! /bin/bash

myName='===ExeBinSignature==='
myPath=$(readlink -f $0 | xargs dirname )
md5sumUtil=${myPath}/md5sum2
errMsgPrefix="${myName} ERROR:"
md5MsgPrefix="${myName} MD5: "


# Perl-like die function
die()
{
  echo "${errMsgPrefix} ${1}"
  exit 1
}


if [ $# -lt 1 ]
then
    echo "Display application signature from an executable binary file"
    echo "Usage: $0 exeBinFile"
    exit 1
fi

[ -f $1 -a -x $1 ] || die "$1 is not an executable binary file"

exeBinBasename=`basename $1`
exeBinFullname=`readlink -f $1`


dynlibs=`/usr/bin/ldd ${exeBinFullname} | fgrep -v "not a dynamic" | cut -d' ' -f 3`

for f in ${exeBinFullname} ${dynlibs}
do

if [ "$f" != "" ] 
then
echo ${md5MsgPrefix}`${md5sumUtil} -b $f`
fi

done

exit 0
