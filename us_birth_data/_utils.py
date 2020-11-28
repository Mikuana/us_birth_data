def _recurse_subclasses(class_to_recurse):
    """ List subclasses """
    def generator(x):
        for y in x.__subclasses__():
            for z in generator(y):
                yield z
        if x != class_to_recurse:
            yield x

    return list(generator(class_to_recurse))
