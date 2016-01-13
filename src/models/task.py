class Task(object):
    """
    A simple class that models the `SCHEDULEDTASKS` table.
    """

    # Unnamed argument indexes for the class attributes.
    TASK_ID_IDX = 0
    TIME_TO_START_IDX = 1
    REPEAT_IN_IDX = 2
    RESOURCE_IDX = 3
    APP_IDX = 4
    RESOURCE_PARAM_IDX = 5
    APP_PARAM_IDX = 6
    TASK_PARAM_IDX = 7
    GROUP_ID_IDX = 8
    PARENT_TASK_ID_IDX = 9

    # Named argument keys for the class attributes
    TASK_ID_NAME = 'task_id'
    TIME_TO_START_NAME = 'time_to_start'
    REPEAT_IN_NAME = 'repeat_in'
    RESOURCE_NAME = 'resource'
    APP_NAME = 'app'
    RESOURCE_PARAM_NAME = 'resource_param'
    APP_PARAM_NAME = 'app_param'
    TASK_PARAM_NAME = 'task_param'
    GROUP_ID_NAME = 'group_id'
    PARENT_TASK_ID_NAME = 'parent-id'

    def __or(self, items, index, default):
        """
        A functional method that allows for the providing of a 'default' value
        if the provided list of items 'length' is less than the requested
        'index'
        """
        if len(items) > index:
            return items[index]
        else:
            return default

    def __init__(self, *args, **kwargs ):
        """
        Default Constructor that handles both unnamed, named and empty
        construction. Note that if you provide unnamed parameters they
        must be before named parameters.
        """

        self.task_id = self.__or(args, Task.TASK_ID_IDX, kwargs.get(Task.TASK_ID_NAME, None))
        self.time_to_start = self. __or(args, Task.TIME_TO_START_IDX, kwargs.get(Task.TIME_TO_START_NAME, None))
        self.repeat_in = self.__or(args, Task.REPEAT_IN_IDX, kwargs.get(Task.REPEAT_IN_NAME, None))
        self.resource = self.__or(args, Task.RESOURCE_IDX, kwargs.get(Task.RESOURCE_NAME, None))
        self.app = self.__or(args, Task.APP_IDX, kwargs.get(Task.APP_NAME, None))
        self.resource_param = self.__or(args, Task.RESOURCE_PARAM_IDX, kwargs.get(Task.RESOURCE_PARAM_NAME, None))
        self.app_param = self.__or(args, Task.APP_PARAM_IDX, kwargs.get(Task.APP_PARAM_NAME, None ))
        self.task_param = self.__or(args, Task.TASK_PARAM_IDX, kwargs.get(Task.TASK_PARAM_NAME, None))
        self.group_id = self.__or(args, Task.GROUP_ID_IDX, kwargs.get(Task.GROUP_ID_NAME, None))
        self.parent_task_id = self.__or(args, Task.PARENT_TASK_ID_IDX, kwargs.get(Task.PARENT_TASK_ID_NAME, None))

    def __str__(self):
        return "{ %s }" % ', '.join(['%s: %s' % (key, value) for (key, value) in self.__dict__.iteritems() ])
