import logging
from .base import BaseDebugProcessor


class LoggerProcessor(BaseDebugProcessor):
    def __init__(self, logger_name, logger_level=logging.DEBUG, **kwargs):
        """
        局部修改logger level
        :param logger_name: logger名称, 多个日志以逗号分隔
        :param logger_level: 日志层级
        :param kwargs: 需要支持其他参数传入
        """
        super().__init__(**kwargs)
        self.logger_names = [l.strip() for l in logger_name.split(',')]
        self.logger_level = logger_level

    def call(self, fn, *args, **kwargs):
        old_logger_level = dict()
        old_logger_handlers_level = {logger_name: dict() for logger_name in self.logger_names}

        # 所选logger及其handlers都切换为指定logger_level级别
        for logger_name in self.logger_names:
            logger = logging.getLogger(logger_name)
            old_logger_level[logger_name] = logger.level
            logger.setLevel(self.logger_level)

            for handler in logger.handlers:
                old_logger_handlers_level[logger_name][handler] = handler.level
                handler.setLevel(self.logger_level)

            # debug日志开始
            logger.debug(f'debug mode on')

        ret_val = fn(*args, **kwargs)

        # 恢复logger及其handlers级别
        for logger_name in self.logger_names:
            # debug日志结束
            logger.debug(f'debug mode off')

            logger = logging.getLogger(logger_name)
            logger.setLevel(old_logger_level.get(logger_name))

            for handler in logger.handlers:
                handler.setLevel(old_logger_handlers_level[logger_name][handler])

        return ret_val
