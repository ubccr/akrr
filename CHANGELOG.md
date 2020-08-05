# Application Kernels Remote Runner (AKRR ) Change Log

## 2020-08-10 v2.1.0

- new CLI interface. Single entry to all routines: ```akrr [-v] <command> [arguments]```.
- Converted to python3.
- RPM installation is available for CentOS 7.8.
- New AppKernels: HPCG, MDTest and ENZO.
- New resource types support: OpenStack and stand alone machine without queue system (shell). 
- Batch appkernels task submission, for example run all appkernels 10 times each as soon as possible.
  Usable for checking performance before/after update.
- Docker container based appkernel execution (HPCC on single node on docker enabled resources).
- Many other improvements and bug fixes.

## 2015-08-15 v1.0

- Initial AKRR v1.0 release.
