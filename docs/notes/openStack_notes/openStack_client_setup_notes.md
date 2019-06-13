## Notes on trying to get openstack client thing installed on local machine

Following the notes given by Dr. Simakov - OpenStackNotes.Rmd

```bash
#Need to get pip3 first it looks like
sudo yum install python36-setuptools
sudo easy_install-3.6 pip

# had to do this bc sudo wasn't recognizing pip3
sudo python3 -m pip install python-cinderclient==3.6.1
sudo python3 -m pip install python-openstackclient
sudo python3 -m pip install git+https://github.com/ubccr/v3oidcmokeyapikey.git

```
Get enviroment setup script from OpenStack portal https://lakeeffect.ccr.buffalo.edu

On top left Project->API Access; then right middle Download OpenStack RC File (Identity API v3) - Check

- I put the resulting script in ~/projects/openstack

Then I had to get api key - that was done on ub ccr profile

```bash
# then I could source fine
source lakeeffect-xdmod-openrc.sh
openstack flavor list
openstack image list

```

```bash
# trying to spin-off instance
openstack server create --flavor c8.m16 --volume aktestvolume --network lakeeffect-199.109.195 --security-grou default --security-group SSH --key-name openstack-testing test_create_from_cl
# note: with the key-name, that's from the key pairs in openstack

```
Things seem to be set up fine

