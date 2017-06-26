def __or(items, index, default):
        """
        A functional method that allows for the providing of a 'default' value
        if the provided list of items 'length' is less than the requested
        'index'
        """
        if len(items) > index:
            return items[index]
        else:
            return default
