# Configuration


Execute setup script, it will ask several question about you system and will setup AKRR: 

```bash
akrr setup
```

Upon successful execution, AKRR should be properly configured and AKRR daemon should be running.
You can check that by execution:
```bash
akrr daemon status
``` 

The script add cron table for periodic health checking of AKRR and log rotation.

The configuration and log are in _~/akrr_ in case of RPM installation or _withing the source code_ 
in case of in source code installation.

Once AKRR daemon is running you can start adding resources and applications. 

The following are more detailed  
