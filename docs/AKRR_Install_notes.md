These are notes on the installation of AKRR (05/20/19)

- There may be errors with sudo yum install akrr....rpm
	- If error is that akrr_test is not available or whatever: run the following in the top directory of AKRR:
```bash
sudo docker build -t akrr_test -f Dockerfile_run_tests .
```

- EPEL does not have python34-mysql or python34-typing
	- rpm of python34-typing can be found here: https://centos.pkgs.org/7/puias-unsupported-x86_64/python34-typing-3.5.2.2-3.sdl7.noarch.rpm.html

	- Eventual fix: just change all the setup things to python36 instead of python34 and no error
	- Also changed the Install file to have python36 in it

- For whatever reason, there was trouble with finding the modules when running 'akrr setup'
	- When typing akrr in terminal, it went to /usr/bin/akrr
	- Had to end up appending the entire akrr repository to the sys path with sys.append
	- That seems to have fixed the problem
