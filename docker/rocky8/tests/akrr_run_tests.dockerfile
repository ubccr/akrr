FROM nsimakov/akrr_ready:latest

LABEL description="image to run akrr tests with"

ENV REPO_FULL_NAME=ubccr/akrr

ENTRYPOINT ["/usr/local/sbin/cmd_start"]
CMD ["-set-no-exit-on-fail", \
     "chown -R akrruser:akrruser /home/akrruser/akrr_src", \
     "su akrruser -c 'bash /home/akrruser/akrr_src/tests/regtest1/run_tests.sh'", \
     "bash_akrruser"]

