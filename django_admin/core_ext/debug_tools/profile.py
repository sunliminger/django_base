import cProfile
import io
import logging
import os
import pstats
import time
from django.conf import settings
from functools import wraps

from .base import BaseDebugProcessor


def profile(*dargs, **dkw):
    """
    profile装饰器方法，调用Profile对象
    @param *dargs: positional arguments passed to Profile object
    @param **dkw: keyword arguments passed to the Profile object
    """
    # support both @profile and @profile() as valid syntax
    if len(dargs) == 1 and callable(dargs[0]):
        def wrap_simple(f):
            @wraps(f)
            def wrapped_f(*args, **kw):
                return Profile().call(f, *args, **kw)
            return wrapped_f

        return wrap_simple(dargs[0])

    else:
        def wrap(f):
            @wraps(f)
            def wrapped_f(*args, **kw):
                return Profile(*dargs, **dkw).call(f, *args, **kw)
            return wrapped_f

        return wrap


def prof2svg(file_path):
    """
    Profile文件转换svg
    :param file_path: 文件路径
    :return:
    """
    if not os.path.exists(file_path):
        raise Exception(f'prof文件 {file_path} 不存在')
    content = os.popen(f'flameprof {file_path}')
    svg_path = f'{file_path.rsplit(".", maxsplit=1)[0]}.svg'
    with open(svg_path, 'w') as f:
        f.write(content.read())


class Profile(BaseDebugProcessor):
    default_logger_name = 'profile'

    def __init__(self, stats_processor=None,
                 prof_name=None, get_prof_name=None,
                 logger_name=None, logger=None, **kwargs):
        """
        Profile对象
        :param stats_processor: 自定义结果处理函数
        :param prof_name: 保存的prof文件名
        :param get_prof_name: 获取prof文件名的方法
        :param logger_name: logger name
        :param logger: logger
        :param kwargs: 需要支持其他参数传入
        """
        super().__init__(**kwargs)
        self.stats_processor = stats_processor or self.dump_stats
        self.prof_name = prof_name
        self.get_prof_name = get_prof_name or self.default_get_prof_name
        self.logger_name = logger_name or self.default_logger_name
        self.logger = logger or logging.getLogger(self.logger_name)

    def default_get_prof_name(self):
        return self.prof_name or str(time.perf_counter_ns())

    def dump_stats(self, pr):
        """ 导出文件 """
        filename = os.path.join(settings.PROFILE_PATH, f'{self.get_prof_name()}.prof')
        pr.dump_stats(filename)
        self.logger.debug(filename)
        prof2svg(filename)

    def logger(self, pr, level=logging.DEBUG):
        """ 记日志形式保存结果 """
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s)
        ps.print_stats()
        self.logger.log(level=level, msg=s.getvalue())

    def call(self, fn, *args, **kwargs):
        """ 以profile模式执行某个函数 """
        pr = cProfile.Profile()
        pr.enable()
        ret_val = fn(*args, **kwargs)
        pr.disable()
        self.stats_processor(pr)
        return ret_val
