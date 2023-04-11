from django.utils.deprecation import MiddlewareMixin
from .processors import processor_factory


class DebugMiddleware(MiddlewareMixin):
    """
    debug中间件
        在接口参数上添加参数debug=true即可触发debug模式请求接口，使当次请求以debug模式执行

    debug模式表现为:
        Request对象添加debug属性为True，使用者可以通过`getattr(request, 'debug', False)`获取
        接口将会被一个或多个debug中间件调用

    通用url参数支持:
        * debug: true/True-触发debug模式
        * debug_processor: 处理的debug中间件，默认为do_nothing
    """
    def __call__(self, request):
        debug = request.GET.get('debug') in ['true', 'True', True]
        if not debug:
            return super().__call__(request)
        setattr(request, 'debug', True)
        debug_processor = request.GET.get('debug_processor', 'do_nothing')
        processor = processor_factory(debug_processor)
        kwargs = {k: request.GET.get(k) for k in request.GET}       # 防止歧义，不支持列表参数传入
        response = processor(**kwargs).call(super().__call__, request)
        return response
