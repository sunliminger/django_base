class BaseDebugProcessor(object):
    """ debug处理器基类 """
    def __init__(self, **kwargs):
        """ 需要支持kwargs传入 """
        self.kwargs = kwargs

    def call(self, fn, *args, **kwargs):
        """ do nothing """
        return fn(*args, **kwargs)

