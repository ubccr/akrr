## Notes on trying to follow what akrr is doing with pycharm...?
pycharms started with 
```bash
sudo /usr/local/bin/charm &
```

```bash
#nikolay suggested doing something like
akrr daemon startdeb
# as well as somehow using pycharm debugger
# so i'm trying to figure out what it all means now
```

```bash
# stopped the daemon with
akrr daemon stop

# then did that above
akrr daemon startdeb
# Result:
[2019-05-31 15:07:25,306 - INFO] Starting Application Remote Runner
[2019-05-31 15:07:25,317 - INFO] AKRR Scheduler PID is 9448.
[2019-05-31 15:07:25,327 - INFO] Starting REST-API Service
[2019-05-31 15:07:25,329 - INFO] ####################################################################################################
[2019-05-31 15:07:25,329 - INFO] Got into the running loop on 2019-05-31 15:07:25
[2019-05-31 15:07:25,329 - INFO] ####################################################################################################

Starting REST-API Service
Bottle v0.12.13 server starting up (using SSLWSGIRefServer())...
Listening on http://localhost:8091/
Hit Ctrl-C to quit.

#So its running in foreground now? unsure

```


Pycharm Debugging:
- need to set a break point (click next to line number) - debugger goes runs to that point and then stops. Then can step forward and proceed through the program step by step (i believe)
- cli init calls the util and log init too
- cli provides access to command line and uses log from akrr.util
- Anytime import happens, first goes through init
- So import akrr.cli -> akrr/__init__.py then once that is done it goes to cli/__init__
- __init__ files only look at the function definitions, don't run anything in functions
- In cli/init it eventually gets to the class defined as CLI - looks at those functions in there
- Once all the initing is done, goes to do akrr.cli.CLI().run()
	- This statement goest to the cli init file, where the class CLI is in. Now CLI calls its __init__ before its run can be called
- with arg parser in cli/__init__, it goes to commands to import those things - sets up argument parser
- in the cli run it looks at the args - and with debug there are no args so its an error

- To run the debugger with arguments, you have to go to Run -> Edit Configurations -> "+" and add a new config there
	- This sets the short_log_prefix to false

- It does cli_arg.func(cli_args) -> i think this tells the arg parser to just find the proper function based on the arguments given. It does end up going to the handler for daemon_startdeb in commands, which goes to daemon.py
- The daemon init starts gets a bunch of defaults started - also imports cfg (AKRR config?)
	- The config sets up some defaults as to what everything is called, what port things are connected to, where the data goes, job submit time wait/max time for job submit attempts, etc.
- Then cfg gets the directories where things are located
- Then goes to get akrr dirs - where it tries to get directories where everything is it seems
	- Unsure what all the directories are supposed to be, it seems the akrr_cli_fillpath isn't completely correct, unsure though - seems to just be pointing to the very initial akrr.py script
- All the variables from the config now come in and are present in cfg
- Then from cfg goes to cfg_util - this imports akrrError and some variables from akrr.cfg and util
- Towards end of cfg, reads in akrr.conf file
- Then verifies akrr conf - checks if files/variables needed exist
	- Seems to raise warnings if certain variables aren't in config file (akrr.conf)? but they do seem to be in the python script that did the config things...?
- loading resources - goes to resource directory and calls load_resource from cfg_util
- it reads in the config files and stores in all the variables they give - has stuff like the usernames and such to use for that resource, I'm assuming
- removes the built ins - so dictionary only has the variables given in the config file
- So then it has all the variables for that resource in a dictionary - that is then passed to a validation system
- sets various other things in the resource dictionary (like file names and times
- lots of checking for valid things in dictionary
- Once resources are loaded into dictionary, then load_all_app() is called in cfg
- again validation with app config
- so the daemon import cfg basically loads up all the configs
- eventually goes to init of akrr_task
	- which goes to akrr_task_base
		- which goes to ssh things
- daemon sets up all of its functions and definitions and whatnot
- in commands, finally does daemon_start_in_debug_mode
- Ends up initializing AkrrDaemon
- Running into problem, gives this error message:

```bash
  File "/opt/pycharm-community-2019.1.3/helpers/pydev/pydevd.py", line 1758, in <module>
    main()
  File "/opt/pycharm-community-2019.1.3/helpers/pydev/pydevd.py", line 1752, in main
    globals = debugger.run(setup['file'], None, None, is_module)
  File "/opt/pycharm-community-2019.1.3/helpers/pydev/pydevd.py", line 1147, in run
    pydev_imports.execfile(file, globals, locals)  # execute the script
  File "/opt/pycharm-community-2019.1.3/helpers/pydev/_pydev_imps/_pydev_execfile.py", line 18, in execfile
    exec(compile(contents+"\n", file, 'exec'), glob, loc)
  File "/home/hoffmaps/projects/akrr/bin/akrr", line 65, in <module>
    akrr.cli.CLI().run()
  File "/home/hoffmaps/projects/akrr/akrr/cli/__init__.py", line 154, in run
    return cli_args.func(cli_args)
  File "/home/hoffmaps/projects/akrr/akrr/cli/commands.py", line 155, in handler
    redirect_task_processing_to_log_file=args.redirect_task_processing_to_log_file)
  File "/home/hoffmaps/projects/akrr/akrr/daemon.py", line 1546, in daemon_start_in_debug_mode
    akrr_scheduler = AkrrDaemon()
  File "/home/hoffmaps/projects/akrr/akrr/daemon.py", line 91, in __init__
    self.dbCon, self.dbCur = akrr.db.get_akrr_db()
  File "/home/hoffmaps/projects/akrr/akrr/db.py", line 17, in get_akrr_db
    passwd=akrr_db_passwd, db=akrr_db_name)
  File "/usr/lib64/python3.6/site-packages/MySQLdb/__init__.py", line 86, in Connect
    return Connection(*args, **kwargs)
  File "/usr/lib64/python3.6/site-packages/MySQLdb/connections.py", line 204, in __init__
    super(Connection, self).__init__(*args, **kwargs2)
_mysql_exceptions.OperationalError: (1045, "Access denied for user 'akrruser'@'localhost' (using password: NO)")
Exception ignored in: <bound method AkrrDaemon.__del__ of <akrr.daemon.AkrrDaemon object at 0x7fc455cfb5c0>>
Traceback (most recent call last):
  File "/home/hoffmaps/projects/akrr/akrr/daemon.py", line 117, in __del__
    if self.dbCon is not None:
AttributeError: 'AkrrDaemon' object has no attribute 'dbCon'

```
Unsure what error is, but right now it seems that theres some sort of error with mysql:
{OperationalError}(1045, "Access denied for user 'akrruser'@'localhost' (using password: NO)")
Interestingly, this doesn't happen with running akrr from the command line, so I'm not sure whats happening

So I deleted akrruser and added the user again. That made it work in the debugger, but now when you typed in the console
```bash
akrr daemon startdeb
```
Then it would give the same error as above, 

UPDATE: so if you do 
```bash
/usr/bin/python3.6 /home/hoffmaps/projects/akrr/bin/akrr daemon startdeb
```
in the command line then it works FINE, so there has to be something to do with the install of akrr or something that makes those things different...
- not exactly sure how it works but now I'm gonna continue debugging
- Also for some reason whenever i'm editing files in pycharm it changes the user and group of that file to root.... maybe bc I started pycharm with sudo?

- We're in AkrrDaemon init, just got the connection to the database 
- Initializes a bunch of variables, many from the cfg
- checks if there's an existing pid file, which would mean another akrr is running
- the signal.signal call sets it so that anytime the program gets that signal, it calls the python function instead
- then AKRRDaemon goes to start the akrrRestApi... unsure what that is.. found this: https://restfulapi.net/
And this: https://searchmicroservices.techtarget.com/definition/RESTful-API
and this: https://en.wikipedia.org/wiki/Representational_state_transfer#Architectural_properties
- Basically it seems the idea of something being RESTful has to do with how it is set up - basically to improve/standardize interactions between the client and data

- The restapi then sets up bottle_api_json_formatting for formatting of output?
- So akrrrestapi seems to be setting up a bunch of functions to be able to use, and it uses something called bottle, so I'm gonna look into that real quick:
Seems like bottle is an easy way to do web application stuff...? to deal with web data and whatnot? not sure
see https://bottlepy.org/docs/dev/index.html
Used as a sort of web server thingy?
Did some basic bottle stuff, seems that its a way to work with a web server or something? Or to make your own? - has a lot of capability looks like. For now I guess I'm okay saying its just a way of implementing the whole restful api I think
- proc start then starts the process of restapi with a bunch of other process things - parent/child processes etc
- It specifically calls the start_rest_api function and sends over the proper arguments
- The starting of rest api starts the SSLWSGIRefServer, which is also in akrrrestapi
- That creates the server, which is then run with bottle.run! - app in the bottle.run is the bottle object made in akrrrestapi I think...
- So it calls the run of bottle, which then calls the run of the SSLWSGIRefServer
- The SSLWSGIRefServer is a subclass of bottle.ServerAdapter since that is what is in () at class declaration
- The make_server creates a WSGI server, accepting connections 
- Then once it does the serve forever, its done.. debugger exits
- Done with this for now: moving over to work on docker images for namd, nwchem, and gamess










