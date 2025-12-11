"""
Schema深化模块使用示例

提供各种使用场景的示例代码
"""

from code.schema_deepening import (
    SmartHomeConverter,
    OAConverter,
    MaritimeConverter,
    FoodIndustryConverter,
    DeviceProtocol,
    DeviceType,
    DocumentFormat,
    DocumentType,
    EPCISEventType,
    TraceDirection
)
from code.schema_deepening.logger import setup_logger

# 设置日志
logger = setup_logger('examples', level=20)  # INFO级别


def example_smart_home():
    """智慧家居转换示例"""
    print("\n=== 智慧家居转换示例 ===")
    
    converter = SmartHomeConverter()
    
    # 注册Matter设备
    device = converter.register_device({
        'device_id': 'matter_light_1',
        'name': '客厅智能灯',
        'device_type': 'light',
        'protocol': 'matter',
        'state': {'power': False, 'brightness': 0},
        'capabilities': ['on_off', 'dimming', 'color']
    })
    
    print(f"注册设备: {device.name} ({device.device_id})")
    
    # Matter到Zigbee转换
    matter_device = {
        'device_id': 'matter_light_1',
        'name': '客厅灯',
        'device_type': 'light',
        'protocol': 'matter',
        'clusters': [{
            'cluster_id': 0x0006,
            'cluster_name': 'OnOff',
            'attributes': {'OnOff': True}
        }]
    }
    
    zigbee_device = converter.convert_matter_to_zigbee(matter_device)
    print(f"转换结果: {zigbee_device['friendly_name']}")
    
    # 创建场景
    scene = converter.create_scene({
        'name': '回家场景',
        'triggers': [{'type': 'manual'}],
        'actions': [{
            'type': 'set_state',
            'device_id': 'matter_light_1',
            'attribute': 'power',
            'value': True
        }],
        'conditions': [{
            'type': 'time',
            'start_time': '18:00:00',
            'end_time': '23:00:00'
        }]
    })
    
    print(f"创建场景: {scene.name} ({scene.scene_id})")
    
    # 执行场景
    result = converter.execute_scene(scene.scene_id)
    print(f"场景执行结果: {'成功' if result['success'] else '失败'}")


def example_oa():
    """OA转换示例"""
    print("\n=== OA转换示例 ===")
    
    converter = OAConverter()
    
    # 注册文档
    document = converter.register_document({
        'document_id': 'doc_001',
        'name': '项目计划书',
        'document_type': 'text',
        'format': 'odf',
        'content': {
            'title': '项目计划',
            'sections': ['概述', '目标', '计划']
        }
    })
    
    print(f"注册文档: {document.name} ({document.document_id})")
    print(f"文档类型: {document.document_type.value}, 格式: {document.format.value}")


def example_maritime():
    """Maritime转换示例"""
    print("\n=== Maritime转换示例 ===")
    
    converter = MaritimeConverter()
    
    # 解析EDIFACT消息
    edifact_msg = (
        "UNH+1+ORDERS:D:96A:UN'"
        "BGM+220+12345'"
        "DTM+137:20240101:102'"
        "NAD+BY+123456789::9'"
        "LIN+1++1234567890123:EN'"
        "QTY+21:100:PCE'"
        "UNT+6+1'"
    )
    
    message = converter.parse_edifact(edifact_msg)
    print(f"解析EDIFACT消息: {message.message_type.value}")
    print(f"消息ID: {message.message_id}")
    print(f"段数量: {len(message.segments)}")


def example_food_industry():
    """食品行业转换示例"""
    print("\n=== 食品行业转换示例 ===")
    
    converter = FoodIndustryConverter()
    
    # 处理EPCIS事件
    event_data = {
        'event_type': 'ObjectEvent',
        'epc': 'urn:epc:id:sgtin:0614141.107346.2017',
        'action': 'OBSERVE',
        'biz_step': 'receiving',
        'event_time': '2024-01-21T10:00:00Z',
        'read_point': 'urn:epc:id:sgln:0614141.00725.0',
        'biz_location': 'urn:epc:id:sgln:0614141.00725.0'
    }
    
    event = converter.process_epcis_event(event_data)
    print(f"处理EPCIS事件: {event.event_type.value}")
    print(f"事件ID: {event.event_id}")
    print(f"EPC: {event.epc}")
    
    # 注册质量规则
    rule = converter.register_quality_rule({
        'rule_id': 'temp_rule_1',
        'name': '温度检查',
        'field': 'temperature',
        'rule_type': 'range',
        'rule_config': {'min': -20, 'max': 5},
        'threshold': 0.95
    })
    
    print(f"注册质量规则: {rule.name} ({rule.rule_id})")
    
    # 质量检查
    food_data = {
        'temperature': 2.5,
        'humidity': 65,
        'batch_number': 'BATCH001'
    }
    
    quality_result = converter.check_quality(food_data, [rule.rule_id])
    print(f"质量检查结果: 通过 {quality_result['passed_rules']}/{quality_result['total_rules']} 项规则")


def example_utils():
    """工具函数示例"""
    print("\n=== 工具函数示例 ===")
    
    from code.schema_deepening.utils import (
        validate_email,
        parse_datetime,
        format_file_size,
        generate_id,
        deep_merge_dict
    )
    
    # 验证邮箱
    email = "test@example.com"
    is_valid = validate_email(email)
    print(f"邮箱验证: {email} -> {is_valid}")
    
    # 解析日期时间
    dt_str = "2024-01-21T10:00:00"
    dt = parse_datetime(dt_str)
    print(f"日期时间解析: {dt_str} -> {dt}")
    
    # 格式化文件大小
    size = format_file_size(1024 * 1024 * 5)  # 5MB
    print(f"文件大小: {size}")
    
    # 生成ID
    id1 = generate_id("device", timestamp=True)
    print(f"生成ID: {id1}")
    
    # 深度合并字典
    dict1 = {'a': 1, 'b': {'c': 2}}
    dict2 = {'b': {'d': 3}, 'e': 4}
    merged = deep_merge_dict(dict1, dict2)
    print(f"字典合并: {merged}")


def main():
    """主函数"""
    print("Schema深化模块使用示例")
    print("=" * 50)
    
    try:
        example_smart_home()
        example_oa()
        example_maritime()
        example_food_industry()
        example_utils()
        
        print("\n" + "=" * 50)
        print("所有示例执行完成！")
        
    except Exception as e:
        logger.error(f"示例执行失败: {str(e)}", exc_info=True)
        print(f"\n错误: {str(e)}")


if __name__ == '__main__':
    main()
