from django.db import models


class GROUP_CONCAT(models.Aggregate):
    """
    自定义Django聚合函数实现GROUP_CONCAT
    """
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(distinct)s%(expressions)s%(separator)s)'

    def __init__(self, expression, distinct=False, separator=',', **extra):
        super(GROUP_CONCAT, self).__init__(
            expression,
            distinct='DISTINCT ' if distinct else '',
            separator=' SEPARATOR "{}"'.format(separator.replace('\"', r'\"')),
            output_field=models.CharField(),
            **extra)