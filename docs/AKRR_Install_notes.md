These are notes on the installation of AKRR (05/20/19)

- EPEL does not have python34-mysql or python34-typing
	- rpm of python34-typing can be found here: https://centos.pkgs.org/7/puias-unsupported-x86_64/python34-typing-3.5.2.2-3.sdl7.noarch.rpm.html

	- Eventual fix: just change all the setup things to python36 instead of python34 and no error
	- Also changed the Install file to have python36 in it
