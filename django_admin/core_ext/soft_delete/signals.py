"""
    定义一些逻辑删除需要使用到的信号。需要注意，逻辑删除/物理删除前的信号发生在
    models.signals.pre_delete之前，逻辑删除/物理删除后的信号发生在
    models.signals.post_delete之后
"""
from django.dispatch import Signal


pre_soft_delete = Signal(providing_args=['instance'])           # 逻辑删除前
post_soft_delete = Signal(providing_args=['instance'])          # 逻辑删除后

pre_hard_delete = Signal(providing_args=['instance'])           # 物理删除前
post_hard_delete = Signal(providing_args=['instance'])          # 物理删除后

pre_restore = Signal(providing_args=['instance'])               # 逻辑删除恢复前
post_restore = Signal(providing_args=['instance'])              # 逻辑删除回复后
