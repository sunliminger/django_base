class ProcessError(Exception):
    """
    业务逻辑处理时引发的异常。
    """
    pass


# ====================== API 接口返回异常 ========================
class APIException(Exception):
    def __init__(self, brief='', error='', error_code=0):
        self.brief = brief
        self.error = error
        self.error_code = error_code

    def __str__(self):
        return self.brief or self.error


class APIProcessException(APIException):
    """ 接口400，业务处理异常，通常是字段错误 """
    pass


class APINotFoundException(APIException):
    """ 接口404，通常是API地址失效 """
    pass


class APIAuthException(APIException):
    """ 接口401或403，通常是认证信息失效 """
    pass


class APIServerException(APIException):
    """ 接口500，通常是对方服务器异常 """
    pass


# ======================= 分布式锁异常 ============================
class LockError(Exception):
    """ 分布式锁异常 """
    pass


# ======================= 自定义数据检测锁异常 ============================
class DataCheckException(Exception):
    """ 自定义数据检测锁异常 """
    pass
