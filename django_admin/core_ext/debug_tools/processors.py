from .base import BaseDebugProcessor
from .logger import LoggerProcessor
from .profile import Profile


def processor_factory(processor_type):
    processor_dict = {
        'do_nothing': BaseDebugProcessor,
        'profile': Profile,
        'logger': LoggerProcessor,
    }
    return processor_dict.get(processor_type, BaseDebugProcessor)
