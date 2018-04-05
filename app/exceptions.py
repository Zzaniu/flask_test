# coding=utf8


# 主要是为了友好，你使用ValueError自然是可以的，
# 但是在抛出异常的时候，我们只知道是值错误，
# 至于为什么会出现错误呢，我们利用ValidationError继承ValueError异常类的来告知，这里是验证错误
class ValidationError(ValueError):
    pass