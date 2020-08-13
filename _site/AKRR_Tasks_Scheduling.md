# Start Appkernels Right-a-way 

```bash
# Run appkernels on 1,2,4 and 8 nodes
akrr task new -r <resource_name> -a <appkernel_name> -n 1,2,4,8

# Run appkernels on all configured nodes
akrr task new -r <resource_name> -a <appkernel_name> -n all

# Run all configure appkernels on all configured nodes
akrr task new -r <resource_name> -a all -n all

# Run all configure appkernels on all configured nodes
# and run each of them 10 times
akrr task new -r <resource_name> -a all -n all --n-runs 10
```

# Schedule regular execution of application kernel.


```bash
# Start daily execution from today on nodes 1,2,4,8 and distribute execution time between 1:00 and 5:00
akrr task new -r $RESOURCE -a $APPKER -n 1,2,4,8 -t0 "01:00" -t1 "05:00" -p 1
```

The periodicity supports multiple formats

* years-months-days hours:minutes:seconds
  * "0-00-001 00:00:00" repeat every 1 day
  * "0-00-000 06:00:00" repeat every 6 hours
* days
  * "3" repeat every 3 day
* hours:minutes
  * "12:00" repeat every 12 hours

# List Tasks

```bash
akrr task list
```

# Delete Tasks

Delete tasks scheduled for execution in the future.


```bash
akrr task delete [-h] [-t TASK_ID] [-r RESOURCE] [-a APPKERNEL]
                      [-n NODES] [--group-id GROUP_ID]
```

```
optional arguments:
  -h, --help            show this help message and exit
  -t TASK_ID, --task-id TASK_ID
                        delete task from scheduled and active tasks (not
                        compatible with other options)
  -r RESOURCE, --resource RESOURCE
                        delete all tasks from resource. Can be combined with
                        --appkernel, --nodes and --group-id.
  -a APPKERNEL, --appkernel APPKERNEL
                        delete appkernel from scheduled tasks. Multiple
                        appkernels separated by comma. Can be combined with
                        --resource, --nodes and --group-id.
  -n NODES, --nodes NODES
                        delete tasks which specified nodes count. Multiple
                        nodes separated by comma. Can be combined with
                        --resource, --appkernel and --group-id.
  --group-id GROUP_ID   delete all tasks with same group-id.Can be combined
                        with --resource, --appkernel and --nodes.
```

# Delete Active Tasks

Delete active tasks, that is the one which is already running.

```bash
akrr task delete_active [-h] [-t TASK_ID] [-r RESOURCE] [-a APPKERNEL]
                        [-n NODES] [--group-id GROUP_ID]
```
