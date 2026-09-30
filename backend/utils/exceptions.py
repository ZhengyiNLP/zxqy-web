"""
业务异常类
用于在 Service 层抛出业务逻辑错误，由 Router 层统一处理
"""


class BusinessException(Exception):
    """业务异常基类"""
    def __init__(self, message: str, code: int = -1, data=None):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(message)


class NotFoundException(BusinessException):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在", data=None):
        super().__init__(message, 404, data)


class ValidationException(BusinessException):
    """参数验证异常"""
    def __init__(self, message: str = "参数验证失败", data=None):
        super().__init__(message, 400, data)


class ForbiddenException(BusinessException):
    """权限不足异常"""
    def __init__(self, message: str = "权限不足", data=None):
        super().__init__(message, 403, data)
