#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/7/1
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : result
# @Software: PyCharm
from pydantic import BaseModel


class Result[T](BaseModel):
    code: int
    message: str
    data: T | None = None

    @classmethod
    def ok(cls, data: T | None = None, code: int = 200, message: str = "Success"):
        return cls(code=code, message=message, data=data)

    @classmethod
    def error(cls, code: int = 500, message: str = "Internal Server Error"):
        return cls(code=code, message=message)
