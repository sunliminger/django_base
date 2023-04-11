"""
    自定义Django Field和Lookup
"""
from typing import Iterable
from django.db import models


class FlagField(models.BigIntegerField):
    """
    通过继承BigInteger类型来实现标记位的列表存储，在数据库中的表现为一个64位整数，在python中的表现为一个包含整数的列表，
    整数的二进制第i位表示数值i存在于列表中.
    eg:
    数据库 9 = 2**0 + 2**3 <==> [0, 3] Python
    """
    description = "标记列表"

    def __init__(self, verbose_name=None, name=None, **kwargs):
        kwargs['default'] = kwargs.get('default', [])
        super().__init__(verbose_name, name, **kwargs)

    def _to_storage_value(self, values):
        """
        将标记位列表转换为BigInteger类型
        :param values: 标记位列表
        :return: 存储值
        """
        value = 0
        for i in values:
            if 0 <= i < 64:
                value |= 2**i
        return value

    def _to_python_value(self, value):
        """
        将大数改成数字列表
        :param value: 存储值
        :return: 标记位列表
        """
        if value <= 0:
            return []
        data = []
        for i in range(64):
            if value & 2**i > 0:
                data.append(i)
        return data

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return self._to_python_value(value)

    def to_python(self, value):
        if value is None:
            return value
        return self._to_python_value(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return self._to_storage_value(value)


@FlagField.register_lookup
class FlagIncludeLookup(models.Lookup):
    """
    FlagField的自定义查询
    eg:
    class TestModel(models.Model):
        product_types = FlagField()
    qs = TestModel.objects.filter(product_types__include=[1, 2])
    等价sql: product_types` & 6 = 6， 判断列表中是否包含 [1, 2] 这个子列表
    """
    lookup_name = 'include'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        rhs = rhs_params[0]
        return f'{lhs} & {rhs} = {rhs}', []


@FlagField.register_lookup
class FlagContainsLookup(FlagIncludeLookup):
    """
    FlagField的自定义查询
    eg:
    class TestModel(models.Model):
        product_types = FlagField()
    qs = TestModel.objects.filter(product_types__contains=3)
    等价sql: product_types` & 8 = 8， 判断列表中是否包含 3 这个元素
    qs = TestModel.objects.filter(product_types__contains=[1, 2])
    参数传入列表可以实现include的效果
    """
    lookup_name = 'contains'

    def __init__(self, lhs, rhs):
        if not isinstance(rhs, Iterable):
            rhs = [rhs]
        super().__init__(lhs, rhs)


class CharListField(models.CharField):
    description = "字符串列表"

    def __init__(self, verbose_name=None, name=None, sep='|', **kwargs):
        kwargs['default'] = kwargs.get('default', [])
        self._sep = sep
        super().__init__(verbose_name, name, **kwargs)

    def _to_storage_value(self, values):
        """
        将字符串列表转换为字符串
        :param values: 字符串列表
        :return: 存储值
        """
        long_string = self._sep.join(str(i) for i in values)
        if not long_string:
            return ''
        value = f'{self._sep}{long_string}{self._sep}'
        return value

    def _to_python_value(self, value):
        """
        将数据库存储的字符串转换为字符串列表
        :param value: 存储值
        :return: 字符串列表
        """
        value = value.strip(self._sep)
        if not value:
            return []
        data = value.split(self._sep)
        return data

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return self._to_python_value(value)

    def to_python(self, value):
        if value is None:
            return value
        return self._to_python_value(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return self._to_storage_value(value)


@CharListField.register_lookup
class CharListContainsLookup(models.Lookup):
    """
    CharListField的自定义查询
    eg:
    class TestModel(models.Model):
        char_list = CharListField(sep='|')
    qs = TestModel.objects.filter(char_list__contains='193')
    等价于sql:
    char_list like "%|193|%"
    """
    lookup_name = 'contains'

    def __init__(self, lhs, rhs):
        if not isinstance(rhs, Iterable) or isinstance(rhs, str):
            rhs = [rhs]
        super().__init__(lhs, rhs)

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        return f'{lhs} like "%%{self.rhs}%%"', []


class CharListLookupMixin:
    """
    针对lookup_value（即rhs）是列表的情况处理，如查找包含列表中所有值的数据，该Mixin是为了对列表右值进行预处理
    eg:
    class TestModel(models.Model):
        char_list = CharListField(sep='|')
    qs = TestModel.objects.filter(char_list__xxxx=['aaa', 'bbb', 'ccc'])
    右值将会由['aaa', 'bbb', 'ccc'] 处理成['|aaa|', '|bbb|', '|ccc|']，进行之后sql生成
    否则会处理成'|aaa|bbb|ccc|'，进行之后sql生成
    """
    def get_prep_lookup(self):
        """ 针对CharListField对右值添加sep """
        if hasattr(self.rhs, '_prepare'):
            return self.rhs._prepare(self.lhs.output_field)
        if self.prepare_rhs and hasattr(self.lhs.output_field, 'get_prep_value'):
            return [self.lhs.output_field.get_prep_value([i]) for i in self.rhs]
        return self.rhs


@CharListField.register_lookup
class CharListIncludeLookup(CharListLookupMixin, models.Lookup):
    """
    CharListField的自定义查询: 筛选包含列表中所有值的数据，即set(lookup_value).issubset(char_list) == True
    eg:
    class TestModel(models.Model):
        char_list = CharListField(sep='#')
    qs = TestModel.objects.filter(char_list__include=['aaa', 'bbb'])
    等价于sql:
    char_list like "%#aaa#%" and char_list like "%#bbb#%"
    """
    lookup_name = 'include'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        sql = ' AND '.join(f'{lhs} like "%%{i}%%"' for i in self.rhs)
        return f'({sql})', []


@CharListField.register_lookup
class CharListIntersectLookup(CharListLookupMixin, models.Lookup):
    """
    CharListField的自定义查询: 筛选包含列表中任意一个值的数据，即 any(map(lambda x: x in char_list, lookup_value)) == True
    eg:
    class TestModel(models.Model):
        char_list = CharListField(sep='#')
    qs = TestModel.objects.filter(char_list__intersect=['aaa', 'bbb'])
    等价于sql:
    char_list like "%#aaa#%" or char_list like "%#bbb#%"
    """
    lookup_name = 'intersect'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        sql = ' OR '.join(f'{lhs} like "%%{i}%%"' for i in self.rhs)
        return f'({sql})', []


class SkuAttrsField(models.CharField):
    description = "sku属性列表"

    def __init__(self, verbose_name=None, name=None, sep='|', **kwargs):
        kwargs['default'] = kwargs.get('default', [])
        self._sep = sep
        super().__init__(verbose_name, name, **kwargs)

    def _to_storage_value(self, values):
        """
        将sku属性值列表转换为字符串
        :param values: sku属性值列表
        :return: 存储值
        """
        # 填充默认属性，校验传值都为整数
        from utils.sku import fill_default_sku_attrs
        if values is None:
            values = set()
        values = fill_default_sku_attrs(values)

        # 转换字符串
        long_string = self._sep.join(str(i) for i in values)
        value = f'{self._sep}{long_string}{self._sep}'
        return value

    def _to_python_value(self, value):
        """
        将数据库存储的字符串转换为sku属性值列表
        :param value: 存储值
        :return: sku属性值列表
        """
        from utils.sku import fill_default_sku_attrs
        data = set()
        if value:
            try:
                data = {int(i) for i in value.strip(self._sep).split(self._sep)}
            except:
                pass
        return fill_default_sku_attrs(data)

    def from_db_value(self, value, expression, connection, context):
        return self._to_python_value(value)

    def to_python(self, value):
        return self._to_python_value(value)

    def get_prep_value(self, value):
        return self._to_storage_value(value)

    def contribute_to_class(self, cls, name, **kwargs):
        """ 对模型类添加额外属性 """
        super().contribute_to_class(cls, name, **kwargs)

        def _property(instance):
            from elm.configs import SKU_ATTRS
            value = getattr(instance, self.name)
            return [{'id': a, 'name': SKU_ATTRS[a]} for a in value if a in SKU_ATTRS]

        def _pretty_property(instance):
            from utils.sku import sku_attrs_pretty
            value = getattr(instance, self.name)
            return sku_attrs_pretty(value)

        setattr(cls, f'get_{self.name}_display', _property)
        setattr(cls, f'get_{self.name}_pretty', _pretty_property)
