#!/bin/sh

MYPROXY_SERVER=myproxy.teragrid.org
MYPROXY_SERVER_PORT=7514
export MYPROXY_SERVER MYPROXY_SERVER_PORT
myproxy-logon -S -T -t 24000 -l xdtas << END
@pp+k3rnel_Runner
END

