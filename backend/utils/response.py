"""
统一 API 响应格式

所有接口必须使用 ok() / fail() 返回，禁止手动构造 {"code": 0, ...}
"""


def ok(data=None, message="操作成功"):
    """成功响应"""
    return {"code": 0, "data": data, "message": message}


def fail(message="操作失败", code=-1, data=None):
    """业务错误响应"""
    return {"code": code, "data": data, "message": message}
