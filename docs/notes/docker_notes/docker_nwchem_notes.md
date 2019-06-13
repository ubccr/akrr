## Trying to get a nwchem thing working with docker


Did the following pull (seemed to be a respectable org)

```bash
docker pull nwchemorg/nwchem-qc
```

Then ran it in the nwchem inputs directory with

```bash
docker run -v `pwd`:/opt/data nwchemorg/nwchem-qc "aump2.nw"
```

This did work and ran decently, till it got to an error about geometry, looking into that

