def object_convert_duck_model(instance, model_class):
    """
    将一个model对象转换为使用相同数据表的Model类
    :param instance: 实例对象
    :param model_class: model类
    :return: model类的实例对象
    """
    # 目标类的字段字典， {数据库字段名: Field对象}
    target_field_map = {
        f.db_column or f.name: f for f in model_class._meta.fields
    }
    object_data = {}
    for source_field in instance._meta.fields:
        target_field = target_field_map.get(source_field.db_column or source_field.name, None)
        if not target_field:
            continue
        field_value = getattr(instance, source_field.name)
        try:
            # 先将值转换为数据库存储值，再转换为目标字段python值
            object_data[target_field.name] = target_field.to_python(source_field.get_prep_value(field_value))
        except:
            object_data[target_field.name] = field_value

    return model_class(**object_data)
