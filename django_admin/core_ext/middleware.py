import time
import json
import logging
from django.utils.deprecation import MiddlewareMixin


class LogMiddleware(MiddlewareMixin):
    """ 通过session的认证方式记录 """

    def process_request(self, request):
        try:
            if request.session.session_key is not None:
                data = {
                    "name": str(request.user),
                    "sid": request.session.session_key,
                    "action_time": time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime()),
                    "uri": request.path,
                    "system": "new_lms"
                }
                logger = logging.getLogger('access_log')
                logger.info(msg=json.dumps(data))
        except Exception as e:
            pass

    def process_response(self, request, response):
        return response


class OpenAPILogMiddleware(MiddlewareMixin):
    """ 测试环境OpenAPI接口日志记录 """
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.start_time = None
        self.end_time = None

    @property
    def time_pass(self):
        if self.start_time is None or self.end_time is None:
            return -1
        return (self.end_time - self.start_time) / 1000000

    def parse_url_path(self, url_path):
        """ 解析url """
        try:
            url_prefix, rest = url_path.strip('/').split('/', 1)
        except Exception as e:
            return '', ''
        return url_prefix, rest

    def get_logger(self, rest):
        """ 根据url后缀获取logger """
        _app = rest.strip('/').split('/')[0]
        logger_name = f'openapi_{_app}'
        logger = logging.getLogger(logger_name)
        return logger

    def __call__(self, request):
        url_prefix, rest = self.parse_url_path(request.path)
        if url_prefix != 'openapi':
            return self.get_response(request)

        # 记录请求开始时间
        self.start_time = time.perf_counter_ns()
        # 给request对象添加process_code
        process_code = str(time.perf_counter_ns())
        setattr(request, 'process_code', process_code)
        log_dict = {
            'uri': rest,
            'method': request.method,
            "action_time": time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime()),
            'process_code': process_code,
        }

        if request.GET:
            # 记录查询参数
            log_dict['params'] = json.dumps(request.GET.dict(), ensure_ascii=False)

        # 记录body参数
        if request.body:
            body_str = request.body.decode('utf8')
            log_dict['request_body'] = json.dumps(json.loads(body_str), ensure_ascii=False)
        elif request.POST:
            log_dict['request_body'] = json.dumps(request.POST.dict(), ensure_ascii=False)

        response = self.get_response(request)

        self.end_time = time.perf_counter_ns()
        log_dict.update({
            'time_pass': f'{self.time_pass:.3f}ms',
            'status_code': response.status_code,
            'response_body': response.content.decode('utf8'),
        })

        logger = self.get_logger(rest)
        logger.info(json.dumps(log_dict, ensure_ascii=False))

        return response
