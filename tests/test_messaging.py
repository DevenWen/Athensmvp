"""
消息系统单元测试
测试Message、Conversation、Communication和ContextManager类的功能
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.core.message import (
    Message, MessageType, MessageBuilder,
    create_argument_message, create_counter_message, 
    create_user_input_message, create_summary_message
)
from src.core.conversation import Conversation
from src.core.communication import Communication, CommunicationChannel, CommunicationStatus, MessageDeliveryStatus
from src.core.context_manager import ContextManager


class TestMessage:
    """Message类的单元测试"""
    
    def test_message_basic_creation(self):
        """测试消息基本创建和属性"""
        content = "这是一条测试消息"
        sender = "测试者"
        message_type = MessageType.ARGUMENT
        
        message = Message(content=content, sender=sender, message_type=message_type)
        
        assert message.content == content
        assert message.sender == sender
        assert message.message_type == message_type
        assert message.id is not None
        assert len(message.id) > 0
        assert isinstance(message.timestamp, datetime)
        assert message.recipient is None
        assert message.context == {}
        assert message.references == []
        assert message.metadata == {}
    
    def test_message_with_optional_params(self):
        """测试带可选参数的消息创建"""
        message = Message(
            content="测试内容",
            sender="发送者",
            message_type=MessageType.COUNTER,
            recipient="接收者",
            context={"topic": "AI"},
            metadata={"priority": "high"}
        )
        
        assert message.recipient == "接收者"
        assert message.context["topic"] == "AI"
        assert message.metadata["priority"] == "high"
    
    def test_message_type_string_conversion(self):
        """测试消息类型字符串转换"""
        message = Message(
            content="测试",
            sender="测试者",
            message_type="argument"  # 使用字符串
        )
        
        assert message.message_type == MessageType.ARGUMENT
    
    def test_message_type_invalid_string(self):
        """测试无效消息类型字符串转换"""
        message = Message(
            content="测试",
            sender="测试者",
            message_type="invalid_type"
        )
        
        assert message.message_type == MessageType.GENERAL
    
    def test_add_and_remove_reference(self):
        """测试添加和删除消息引用"""
        message = Message(content="测试", sender="测试者", message_type=MessageType.COUNTER)
        ref_id = "ref_123"
        
        # 添加引用
        message.add_reference(ref_id)
        assert ref_id in message.references
        assert message.has_references()
        assert message.is_reply_to(ref_id)
        
        # 重复添加不会重复
        message.add_reference(ref_id)
        assert message.references.count(ref_id) == 1
        
        # 删除引用
        message.remove_reference(ref_id)
        assert ref_id not in message.references
        assert not message.has_references()
        assert not message.is_reply_to(ref_id)
    
    def test_context_management(self):
        """测试上下文信息管理"""
        message = Message(content="测试", sender="测试者", message_type=MessageType.GENERAL)
        
        # 设置上下文
        message.set_context("key1", "value1")
        message.set_context("key2", 42)
        
        # 获取上下文
        assert message.get_context("key1") == "value1"
        assert message.get_context("key2") == 42
        assert message.get_context("nonexistent") is None
        assert message.get_context("nonexistent", "default") == "default"
    
    def test_metadata_management(self):
        """测试元数据管理"""
        message = Message(content="测试", sender="测试者", message_type=MessageType.GENERAL)
        
        # 设置元数据
        message.set_metadata("version", "1.0")
        message.set_metadata("source", "unit_test")
        
        # 获取元数据
        assert message.get_metadata("version") == "1.0"
        assert message.get_metadata("source") == "unit_test"
        assert message.get_metadata("nonexistent") is None
        assert message.get_metadata("nonexistent", "default") == "default"
    
    def test_to_dict_serialization(self):
        """测试转换为字典格式"""
        message = Message(
            content="测试消息",
            sender="发送者",
            recipient="接收者",
            message_type=MessageType.ARGUMENT,
            context={"topic": "test"},
            metadata={"priority": "high"}
        )
        message.add_reference("ref_123")
        
        data = message.to_dict()
        
        assert data["content"] == "测试消息"
        assert data["sender"] == "发送者"
        assert data["recipient"] == "接收者"
        assert data["message_type"] == "argument"
        assert data["context"]["topic"] == "test"
        assert data["metadata"]["priority"] == "high"
        assert "ref_123" in data["references"]
        assert "id" in data
        assert "timestamp" in data
    
    def test_from_dict_deserialization(self):
        """测试从字典恢复消息对象"""
        original = Message(
            content="测试消息",
            sender="发送者",
            message_type=MessageType.COUNTER
        )
        original.add_reference("ref_456")
        original.set_context("key", "value")
        
        # 序列化再反序列化
        data = original.to_dict()
        restored = Message.from_dict(data)
        
        assert restored.content == original.content
        assert restored.sender == original.sender
        assert restored.message_type == original.message_type
        assert restored.references == original.references
        assert restored.context == original.context
        assert restored.id == original.id
    
    def test_json_serialization(self):
        """测试JSON序列化和反序列化"""
        message = Message(
            content="JSON测试",
            sender="测试者",
            message_type=MessageType.SUMMARY
        )
        message.add_reference("json_ref")
        
        # 转换为JSON
        json_str = message.to_json()
        assert isinstance(json_str, str)
        
        # 验证JSON格式正确
        data = json.loads(json_str)
        assert data["content"] == "JSON测试"
        
        # 从JSON恢复
        restored = Message.from_json(json_str)
        assert restored.content == message.content
        assert restored.sender == message.sender
        assert restored.message_type == message.message_type
        assert restored.references == message.references
    
    def test_message_clone(self):
        """测试消息克隆"""
        original = Message(
            content="原始消息",
            sender="原始发送者",
            message_type=MessageType.ARGUMENT
        )
        original.add_reference("original_ref")
        original.set_context("original_key", "original_value")
        
        # 基本克隆
        cloned = original.clone()
        assert cloned.content == original.content
        assert cloned.sender == original.sender
        assert cloned.id != original.id  # ID应该不同
        assert cloned.references == original.references
        assert cloned.context == original.context
        
        # 带覆盖的克隆
        cloned_with_override = original.clone(
            content="克隆消息",
            sender="克隆发送者"
        )
        assert cloned_with_override.content == "克隆消息"
        assert cloned_with_override.sender == "克隆发送者"
        assert cloned_with_override.message_type == original.message_type
        assert cloned_with_override.id != original.id
    
    def test_display_preview(self):
        """测试显示预览"""
        message = Message(
            content="这是一条很长的消息内容，用于测试预览功能的截断效果",
            sender="测试者",
            message_type=MessageType.ARGUMENT
        )
        
        # 默认长度预览
        preview = message.get_display_preview()
        assert "[测试者][argument]:" in preview
        assert len(preview) <= 70  # 大概长度
        
        # 自定义长度预览
        short_preview = message.get_display_preview(20)
        assert "..." in short_preview
        assert len(short_preview) <= 40
    
    def test_string_representations(self):
        """测试字符串表示"""
        message = Message(
            content="字符串测试",
            sender="测试者",
            message_type=MessageType.GENERAL
        )
        
        # __str__ 方法
        str_repr = str(message)
        assert "[测试者]: 字符串测试" == str_repr
        
        # __repr__ 方法
        repr_str = repr(message)
        assert "Message(" in repr_str
        assert "测试者" in repr_str
        assert "general" in repr_str


class TestMessageBuilder:
    """MessageBuilder类的单元测试"""
    
    def test_basic_message_building(self):
        """测试基本消息构建"""
        builder = MessageBuilder("构建者")
        
        message = (builder
                  .content("构建的消息")
                  .type(MessageType.ARGUMENT)
                  .to("接收者")
                  .build())
        
        assert message.content == "构建的消息"
        assert message.sender == "构建者"
        assert message.message_type == MessageType.ARGUMENT
        assert message.recipient == "接收者"
    
    def test_reply_message_building(self):
        """测试回复消息构建"""
        builder = MessageBuilder("回复者")
        
        message = (builder
                  .content("这是回复")
                  .type(MessageType.COUNTER)
                  .reply_to("original_msg_id")
                  .with_context("context_key", "context_value")
                  .with_metadata("meta_key", "meta_value")
                  .build())
        
        assert message.content == "这是回复"
        assert message.message_type == MessageType.COUNTER
        assert "original_msg_id" in message.references
        assert message.get_context("context_key") == "context_value"
        assert message.get_metadata("meta_key") == "meta_value"
    
    def test_builder_reset(self):
        """测试构建器重置"""
        builder = MessageBuilder("测试者")
        
        # 第一次构建
        msg1 = (builder
                .content("第一条消息")
                .type(MessageType.ARGUMENT)
                .build())
        
        # 重置后构建
        msg2 = (builder
                .reset()
                .content("第二条消息")
                .type(MessageType.COUNTER)
                .build())
        
        assert msg1.content == "第一条消息"
        assert msg1.message_type == MessageType.ARGUMENT
        assert msg2.content == "第二条消息"
        assert msg2.message_type == MessageType.COUNTER


class TestConvenienceCreationFunctions:
    """便捷创建函数的单元测试"""
    
    def test_create_argument_message(self):
        """测试创建论证消息"""
        message = create_argument_message("逻辑者", "这是论证内容", "怀疑者")
        
        assert message.sender == "逻辑者"
        assert message.content == "这是论证内容"
        assert message.recipient == "怀疑者"
        assert message.message_type == MessageType.ARGUMENT
    
    def test_create_counter_message(self):
        """测试创建反驳消息"""
        reply_to_id = "argument_msg_123"
        message = create_counter_message("怀疑者", "这是反驳内容", reply_to_id, "逻辑者")
        
        assert message.sender == "怀疑者"
        assert message.content == "这是反驳内容"
        assert message.recipient == "逻辑者"
        assert message.message_type == MessageType.COUNTER
        assert reply_to_id in message.references
    
    def test_create_user_input_message(self):
        """测试创建用户输入消息"""
        message = create_user_input_message("用户的话题", "用户123")
        
        assert message.content == "用户的话题"
        assert message.sender == "用户123"
        assert message.message_type == MessageType.USER_INPUT
    
    def test_create_summary_message(self):
        """测试创建总结消息"""
        ref_messages = ["msg1", "msg2", "msg3"]
        message = create_summary_message("总结者", "这是总结内容", ref_messages)
        
        assert message.sender == "总结者"
        assert message.content == "这是总结内容"
        assert message.message_type == MessageType.SUMMARY
        assert all(ref_id in message.references for ref_id in ref_messages)


class TestConversation:
    """Conversation类的单元测试"""
    
    def test_conversation_creation(self):
        """测试对话创建"""
        conv = Conversation()
        
        assert conv.conversation_id.startswith("conv_")
        assert conv.is_empty()
        assert len(conv) == 0
        assert conv.get_message_count() == 0
    
    def test_conversation_with_custom_id(self):
        """测试自定义ID的对话创建"""
        custom_id = "test_conversation_123"
        conv = Conversation(custom_id)
        
        assert conv.conversation_id == custom_id
    
    def test_add_and_get_message(self):
        """测试添加和获取消息"""
        conv = Conversation()
        message = Message("测试消息", "发送者", MessageType.ARGUMENT)
        
        conv.add_message(message)
        
        assert not conv.is_empty()
        assert len(conv) == 1
        assert conv.get_message_count() == 1
        
        retrieved = conv.get_message_by_id(message.id)
        assert retrieved is not None
        assert retrieved.content == "测试消息"
    
    def test_duplicate_message_id_error(self):
        """测试重复消息ID错误"""
        conv = Conversation()
        message1 = Message("消息1", "发送者1", MessageType.ARGUMENT)
        message2 = Message("消息2", "发送者2", MessageType.COUNTER)
        message2.id = message1.id  # 设置相同的ID
        
        conv.add_message(message1)
        
        with pytest.raises(ValueError, match="消息ID .* 已存在"):
            conv.add_message(message2)
    
    def test_get_messages_by_sender(self):
        """测试按发送者获取消息"""
        conv = Conversation()
        
        # 添加不同发送者的消息
        msg1 = Message("消息1", "智能体A", MessageType.ARGUMENT)
        msg2 = Message("消息2", "智能体B", MessageType.COUNTER)
        msg3 = Message("消息3", "智能体A", MessageType.CLARIFICATION)
        
        for msg in [msg1, msg2, msg3]:
            conv.add_message(msg)
        
        # 测试获取智能体A的消息
        agent_a_messages = conv.get_messages_by_sender("智能体A")
        assert len(agent_a_messages) == 2
        assert agent_a_messages[0].content == "消息1"
        assert agent_a_messages[1].content == "消息3"
        
        # 测试限制数量
        limited_messages = conv.get_messages_by_sender("智能体A", limit=1)
        assert len(limited_messages) == 1
        assert limited_messages[0].content == "消息3"  # 应该是最后一条
        
        # 测试不存在的发送者
        empty_messages = conv.get_messages_by_sender("不存在的智能体")
        assert len(empty_messages) == 0
    
    def test_get_messages_by_type(self):
        """测试按类型获取消息"""
        conv = Conversation()
        
        # 添加不同类型的消息
        msg1 = Message("论证1", "智能体A", MessageType.ARGUMENT)
        msg2 = Message("反驳1", "智能体B", MessageType.COUNTER)
        msg3 = Message("论证2", "智能体A", MessageType.ARGUMENT)
        
        for msg in [msg1, msg2, msg3]:
            conv.add_message(msg)
        
        # 测试获取论证类型消息
        argument_messages = conv.get_messages_by_type(MessageType.ARGUMENT)
        assert len(argument_messages) == 2
        assert argument_messages[0].content == "论证1"
        assert argument_messages[1].content == "论证2"
        
        # 测试限制数量
        limited_messages = conv.get_messages_by_type(MessageType.ARGUMENT, limit=1)
        assert len(limited_messages) == 1
        assert limited_messages[0].content == "论证2"
    
    def test_get_recent_messages(self):
        """测试获取最近消息"""
        conv = Conversation()
        
        # 添加多条消息
        messages = []
        for i in range(5):
            msg = Message(f"消息{i+1}", "发送者", MessageType.GENERAL)
            messages.append(msg)
            conv.add_message(msg)
        
        # 测试获取最近3条消息
        recent = conv.get_recent_messages(3)
        assert len(recent) == 3
        assert recent[0].content == "消息3"
        assert recent[1].content == "消息4"
        assert recent[2].content == "消息5"
        
        # 测试获取超过总数的消息
        all_recent = conv.get_recent_messages(10)
        assert len(all_recent) == 5
    
    def test_get_messages_in_timeframe(self):
        """测试按时间范围获取消息"""
        conv = Conversation()
        base_time = datetime.now()
        
        # 创建不同时间的消息
        msg1 = Message("消息1", "发送者", MessageType.GENERAL)
        msg1.timestamp = base_time
        
        msg2 = Message("消息2", "发送者", MessageType.GENERAL)
        msg2.timestamp = base_time + timedelta(hours=1)
        
        msg3 = Message("消息3", "发送者", MessageType.GENERAL)
        msg3.timestamp = base_time + timedelta(hours=2)
        
        for msg in [msg1, msg2, msg3]:
            conv.add_message(msg)
        
        # 测试时间范围查询
        start_time = base_time + timedelta(minutes=30)
        end_time = base_time + timedelta(hours=1, minutes=30)
        
        timeframe_messages = conv.get_messages_in_timeframe(start_time, end_time)
        assert len(timeframe_messages) == 1
        assert timeframe_messages[0].content == "消息2"
    
    def test_get_messages_since(self):
        """测试获取指定时间之后的消息"""
        conv = Conversation()
        base_time = datetime.now()
        
        # 创建不同时间的消息
        msg1 = Message("旧消息", "发送者", MessageType.GENERAL)
        msg1.timestamp = base_time
        
        msg2 = Message("新消息", "发送者", MessageType.GENERAL)
        msg2.timestamp = base_time + timedelta(hours=1)
        
        for msg in [msg1, msg2]:
            conv.add_message(msg)
        
        # 测试获取指定时间后的消息
        since_time = base_time + timedelta(minutes=30)
        new_messages = conv.get_messages_since(since_time)
        
        assert len(new_messages) == 1
        assert new_messages[0].content == "新消息"
    
    def test_find_referenced_messages(self):
        """测试查找被引用的消息"""
        conv = Conversation()
        
        # 创建消息链
        original_msg = Message("原始消息", "发送者1", MessageType.ARGUMENT)
        reply_msg = Message("回复消息", "发送者2", MessageType.COUNTER)
        reply_msg.add_reference(original_msg.id)
        
        conv.add_message(original_msg)
        conv.add_message(reply_msg)
        
        # 测试查找引用
        referenced = conv.find_referenced_messages(reply_msg.id)
        assert len(referenced) == 1
        assert referenced[0].id == original_msg.id
        
        # 测试查找不存在的引用
        no_refs = conv.find_referenced_messages(original_msg.id)
        assert len(no_refs) == 0
    
    def test_find_replies_to_message(self):
        """测试查找对消息的回复"""
        conv = Conversation()
        
        # 创建消息和回复
        original_msg = Message("原始消息", "发送者1", MessageType.ARGUMENT)
        reply1 = Message("回复1", "发送者2", MessageType.COUNTER)
        reply2 = Message("回复2", "发送者3", MessageType.CLARIFICATION)
        
        reply1.add_reference(original_msg.id)
        reply2.add_reference(original_msg.id)
        
        for msg in [original_msg, reply1, reply2]:
            conv.add_message(msg)
        
        # 测试查找回复
        replies = conv.find_replies_to_message(original_msg.id)
        assert len(replies) == 2
        reply_contents = [r.content for r in replies]
        assert "回复1" in reply_contents
        assert "回复2" in reply_contents
    
    def test_get_conversation_thread(self):
        """测试获取对话线程"""
        conv = Conversation()
        
        # 创建对话线程: A -> B -> C -> D
        msg_a = Message("消息A", "发送者1", MessageType.ARGUMENT)
        msg_b = Message("消息B", "发送者2", MessageType.COUNTER)
        msg_c = Message("消息C", "发送者1", MessageType.CLARIFICATION)
        msg_d = Message("消息D", "发送者2", MessageType.SUMMARY)
        
        msg_b.add_reference(msg_a.id)
        msg_c.add_reference(msg_b.id)
        msg_d.add_reference(msg_c.id)
        
        # 调整时间戳确保顺序
        base_time = datetime.now()
        msg_a.timestamp = base_time
        msg_b.timestamp = base_time + timedelta(minutes=1)
        msg_c.timestamp = base_time + timedelta(minutes=2)
        msg_d.timestamp = base_time + timedelta(minutes=3)
        
        for msg in [msg_a, msg_b, msg_c, msg_d]:
            conv.add_message(msg)
        
        # 测试获取线程（从中间开始）
        thread = conv.get_conversation_thread(msg_b.id)
        assert len(thread) == 4
        
        # 验证顺序（应该按时间排序）
        thread_contents = [msg.content for msg in thread]
        assert thread_contents == ["消息A", "消息B", "消息C", "消息D"]
    
    def test_search_messages(self):
        """测试消息搜索"""
        conv = Conversation()
        
        msg1 = Message("这是关于人工智能的讨论", "发送者1", MessageType.ARGUMENT)
        msg2 = Message("我认为AI技术很有前景", "发送者2", MessageType.COUNTER)
        msg3 = Message("关于机器学习的问题", "发送者1", MessageType.CLARIFICATION)
        
        for msg in [msg1, msg2, msg3]:
            conv.add_message(msg)
        
        # 测试大小写不敏感搜索
        results = conv.search_messages("ai")
        assert len(results) == 1  # 只有msg2包含"AI"
        
        # 测试搜索"智能"
        ai_results = conv.search_messages("智能")
        assert len(ai_results) == 1  # msg1包含"人工智能"
        
        # 测试大小写敏感搜索
        results_sensitive = conv.search_messages("AI", case_sensitive=True)
        assert len(results_sensitive) == 1
        assert results_sensitive[0].content == "我认为AI技术很有前景"
        
        # 测试精确匹配
        results_exact = conv.search_messages("机器学习")
        assert len(results_exact) == 1
        assert results_exact[0].content == "关于机器学习的问题"
    
    def test_filter_messages(self):
        """测试消息过滤"""
        conv = Conversation()
        
        msg1 = Message("短消息", "发送者1", MessageType.ARGUMENT)
        msg2 = Message("这是一条比较长的消息，用于测试过滤功能", "发送者2", MessageType.COUNTER)
        msg3 = Message("中等长度的消息内容", "发送者1", MessageType.CLARIFICATION)
        
        for msg in [msg1, msg2, msg3]:
            conv.add_message(msg)
        
        # 过滤长消息（超过5个字符）
        long_messages = conv.filter_messages(lambda msg: len(msg.content) > 5)
        assert len(long_messages) == 2
        
        # 过滤特定发送者的消息
        sender1_messages = conv.filter_messages(lambda msg: msg.sender == "发送者1")
        assert len(sender1_messages) == 2
    
    def test_get_statistics(self):
        """测试统计信息"""
        conv = Conversation()
        
        # 添加一些测试消息
        msg1 = Message("消息1", "智能体A", MessageType.ARGUMENT)
        msg2 = Message("消息2", "智能体B", MessageType.COUNTER)
        msg3 = Message("消息3", "智能体A", MessageType.CLARIFICATION)
        msg2.add_reference(msg1.id)  # msg2引用msg1
        
        # 设置时间戳
        base_time = datetime.now()
        msg1.timestamp = base_time
        msg2.timestamp = base_time + timedelta(minutes=30)
        msg3.timestamp = base_time + timedelta(hours=1)
        
        for msg in [msg1, msg2, msg3]:
            conv.add_message(msg)
        
        stats = conv.get_statistics()
        
        assert stats["total_messages"] == 3
        assert stats["sender_statistics"]["智能体A"] == 2
        assert stats["sender_statistics"]["智能体B"] == 1
        assert stats["type_statistics"]["argument"] == 1
        assert stats["type_statistics"]["counter"] == 1
        assert stats["type_statistics"]["clarification"] == 1
        assert stats["messages_with_references"] == 1
        assert stats["reply_rate"] == 1/3
        assert stats["conversation_duration"] == 3600  # 1小时
        assert "first_message_time" in stats
        assert "last_message_time" in stats
    
    def test_export_and_import(self):
        """测试导出和导入"""
        conv = Conversation("test_conv")
        conv.metadata = {"topic": "AI辩论", "participants": ["A", "B"]}
        
        # 添加消息
        msg1 = Message("消息1", "智能体A", MessageType.ARGUMENT)
        msg2 = Message("消息2", "智能体B", MessageType.COUNTER)
        msg2.add_reference(msg1.id)
        
        conv.add_message(msg1)
        conv.add_message(msg2)
        
        # 测试字典导出/导入
        data = conv.export_to_dict()
        imported_conv = Conversation.from_dict(data)
        
        assert imported_conv.conversation_id == "test_conv"
        assert imported_conv.metadata["topic"] == "AI辩论"
        assert len(imported_conv.messages) == 2
        assert imported_conv.messages[0].content == "消息1"
        assert imported_conv.messages[1].content == "消息2"
        assert imported_conv.messages[1].has_references()
        
        # 测试JSON导出/导入
        json_str = conv.export_to_json()
        json_imported_conv = Conversation.from_json(json_str)
        
        assert json_imported_conv.conversation_id == "test_conv"
        assert len(json_imported_conv.messages) == 2
    
    def test_remove_message(self):
        """测试删除消息"""
        conv = Conversation()
        
        msg1 = Message("消息1", "发送者1", MessageType.ARGUMENT)
        msg2 = Message("消息2", "发送者2", MessageType.COUNTER)
        msg2.add_reference(msg1.id)
        
        conv.add_message(msg1)
        conv.add_message(msg2)
        
        assert len(conv) == 2
        
        # 删除消息1
        removed = conv.remove_message(msg1.id)
        assert removed is True
        assert len(conv) == 1
        assert conv.get_message_by_id(msg1.id) is None
        
        # 尝试删除不存在的消息
        not_removed = conv.remove_message("nonexistent_id")
        assert not_removed is False
    
    def test_clear_conversation(self):
        """测试清空对话"""
        conv = Conversation()
        
        # 添加消息
        for i in range(3):
            msg = Message(f"消息{i+1}", "发送者", MessageType.GENERAL)
            conv.add_message(msg)
        
        assert len(conv) == 3
        assert not conv.is_empty()
        
        # 清空对话
        conv.clear()
        
        assert len(conv) == 0
        assert conv.is_empty()
        assert conv.get_message_count() == 0
    
    def test_conversation_iteration(self):
        """测试对话迭代"""
        conv = Conversation()
        
        messages = []
        for i in range(3):
            msg = Message(f"消息{i+1}", "发送者", MessageType.GENERAL)
            messages.append(msg)
            conv.add_message(msg)
        
        # 测试迭代
        iterated_messages = list(conv)
        assert len(iterated_messages) == 3
        
        for i, msg in enumerate(conv):
            assert msg.content == f"消息{i+1}"
    
    def test_get_context_for_agent(self):
        """测试为智能体获取上下文"""
        conv = Conversation()
        
        # 创建复杂的消息场景
        msg1 = Message("系统启动", "系统", MessageType.GENERAL)
        msg2 = Message("你好智能体A", "用户", MessageType.USER_INPUT, recipient="智能体A")
        msg3 = Message("我是智能体A", "智能体A", MessageType.ARGUMENT)
        msg4 = Message("智能体A说得对", "智能体B", MessageType.COUNTER)
        msg5 = Message("继续讨论", "智能体A", MessageType.CLARIFICATION)
        
        for msg in [msg1, msg2, msg3, msg4, msg5]:
            conv.add_message(msg)
        
        # 获取智能体A的上下文
        context = conv.get_context_for_agent("智能体A", depth=10)
        
        # 应该包括：最近的消息 + 智能体A的消息 + 提到智能体A的消息
        assert len(context) >= 3  # 至少包含智能体A相关的消息
        
        # 验证上下文按时间排序
        for i in range(1, len(context)):
            assert context[i-1].timestamp <= context[i].timestamp
    
    def test_get_recent_exchanges(self):
        """测试获取最近的消息交换"""
        conv = Conversation()
        
        # 创建消息交换: A -> B1, B2; C -> D1
        msg_a = Message("消息A", "发送者1", MessageType.ARGUMENT)
        msg_b1 = Message("回复B1", "发送者2", MessageType.COUNTER)
        msg_b2 = Message("回复B2", "发送者3", MessageType.COUNTER)
        msg_c = Message("消息C", "发送者1", MessageType.ARGUMENT)
        msg_d1 = Message("回复D1", "发送者2", MessageType.COUNTER)
        
        msg_b1.add_reference(msg_a.id)
        msg_b2.add_reference(msg_a.id)
        msg_d1.add_reference(msg_c.id)
        
        # 设置时间戳
        base_time = datetime.now()
        for i, msg in enumerate([msg_a, msg_b1, msg_b2, msg_c, msg_d1]):
            msg.timestamp = base_time + timedelta(minutes=i)
            conv.add_message(msg)
        
        # 获取最近的交换
        exchanges = conv.get_recent_exchanges(count=2)
        
        assert len(exchanges) <= 2
        # 每个交换应该是 (原始消息, [回复列表])
        for original, replies in exchanges:
            assert isinstance(original, Message)
            assert isinstance(replies, list)


class TestCommunicationChannel:
    """CommunicationChannel类的单元测试"""
    
    def test_channel_creation(self):
        """测试通信通道创建"""
        participants = ["智能体A", "智能体B"]
        channel = CommunicationChannel("test_channel", participants)
        
        assert channel.channel_id == "test_channel"
        assert channel.participants == set(participants)
        assert channel.status == CommunicationStatus.ACTIVE
        assert len(channel.message_queue) == 0
        assert channel.stats["messages_sent"] == 0
    
    def test_add_remove_participant(self):
        """测试添加和移除参与者"""
        channel = CommunicationChannel("test", ["智能体A"])
        
        # 添加参与者
        channel.add_participant("智能体B")
        assert "智能体B" in channel.participants
        assert channel.is_participant("智能体B")
        
        # 移除参与者
        channel.remove_participant("智能体A")
        assert "智能体A" not in channel.participants
        assert not channel.is_participant("智能体A")
    
    def test_send_message_success(self):
        """测试成功发送消息"""
        participants = ["智能体A", "智能体B"]
        channel = CommunicationChannel("test", participants)
        
        message = Message("测试消息", "智能体A", MessageType.ARGUMENT, recipient="智能体B")
        
        result = channel.send_message(message)
        
        assert result is True
        assert len(channel.message_queue) == 1
        assert len(channel.conversation.messages) == 1
        assert channel.stats["messages_sent"] == 1
        assert channel.delivery_status[message.id] == MessageDeliveryStatus.PENDING
    
    def test_send_message_failures(self):
        """测试发送消息失败的情况"""
        participants = ["智能体A", "智能体B"]
        channel = CommunicationChannel("test", participants)
        
        # 通道非活跃状态
        channel.pause()
        message1 = Message("测试1", "智能体A", MessageType.ARGUMENT)
        assert channel.send_message(message1) is False
        
        # 恢复通道状态
        channel.resume()
        
        # 发送者不是参与者
        message2 = Message("测试2", "智能体C", MessageType.ARGUMENT)
        assert channel.send_message(message2) is False
        
        # 接收者不是参与者
        message3 = Message("测试3", "智能体A", MessageType.ARGUMENT, recipient="智能体C")
        assert channel.send_message(message3) is False
    
    def test_message_delivery_status(self):
        """测试消息投递状态管理"""
        channel = CommunicationChannel("test", ["智能体A", "智能体B"])
        message = Message("测试", "智能体A", MessageType.ARGUMENT)
        
        channel.send_message(message)
        
        # 标记已投递
        assert channel.mark_delivered(message.id) is True
        assert channel.delivery_status[message.id] == MessageDeliveryStatus.DELIVERED
        assert channel.stats["messages_delivered"] == 1
        
        # 标记已确认
        assert channel.mark_acknowledged(message.id) is True
        assert channel.delivery_status[message.id] == MessageDeliveryStatus.ACKNOWLEDGED
        assert channel.stats["messages_acknowledged"] == 1
        
        # 标记失败
        assert channel.mark_failed(message.id) is True
        assert channel.delivery_status[message.id] == MessageDeliveryStatus.FAILED
        
        # 尝试处理不存在的消息
        assert channel.mark_delivered("nonexistent") is False
    
    def test_get_pending_messages(self):
        """测试获取待处理消息"""
        channel = CommunicationChannel("test", ["智能体A", "智能体B"])
        
        msg1 = Message("消息1", "智能体A", MessageType.ARGUMENT, recipient="智能体B")
        msg2 = Message("消息2", "智能体B", MessageType.COUNTER, recipient="智能体A")
        msg3 = Message("广播消息", "智能体A", MessageType.GENERAL)
        
        channel.send_message(msg1)
        channel.send_message(msg2)
        channel.send_message(msg3)
        
        # 获取智能体B的待处理消息
        pending_for_b = channel.get_pending_messages("智能体B")
        assert len(pending_for_b) == 2  # msg1 (targeted) + msg3 (broadcast)
        
        # 获取所有待处理消息
        all_pending = channel.get_pending_messages()
        assert len(all_pending) == 3
        
        # 标记一条消息已投递
        channel.mark_delivered(msg1.id)
        pending_for_b_after = channel.get_pending_messages("智能体B")
        assert len(pending_for_b_after) == 1  # 只剩msg3
    
    @patch('builtins.print')  # Mock print to avoid output during tests
    def test_message_listeners(self, mock_print):
        """测试消息监听器"""
        channel = CommunicationChannel("test", ["智能体A"])
        
        received_messages = []
        
        def listener(message):
            received_messages.append(message)
        
        def failing_listener(message):
            raise Exception("监听器错误")
        
        # 添加监听器
        channel.add_message_listener(listener)
        channel.add_message_listener(failing_listener)
        
        message = Message("测试", "智能体A", MessageType.ARGUMENT)
        channel.send_message(message)
        
        # 验证正常监听器收到消息
        assert len(received_messages) == 1
        assert received_messages[0].content == "测试"
        
        # 验证错误监听器的异常被捕获（通过print调用）
        mock_print.assert_called()
        
        # 移除监听器
        channel.remove_message_listener(listener)
        
        message2 = Message("测试2", "智能体A", MessageType.ARGUMENT)
        channel.send_message(message2)
        
        # 验证移除后不再收到消息
        assert len(received_messages) == 1
    
    def test_channel_status_management(self):
        """测试通道状态管理"""
        channel = CommunicationChannel("test", ["智能体A"])
        
        assert channel.status == CommunicationStatus.ACTIVE
        
        # 暂停通道
        channel.pause()
        assert channel.status == CommunicationStatus.PAUSED
        
        # 恢复通道
        channel.resume()
        assert channel.status == CommunicationStatus.ACTIVE
        
        # 终止通道
        channel.terminate()
        assert channel.status == CommunicationStatus.TERMINATED
        assert len(channel.message_queue) == 0
        
        # 尝试从非暂停状态恢复（应该无效果）
        channel.resume()
        assert channel.status == CommunicationStatus.TERMINATED
    
    def test_get_conversation_history(self):
        """测试获取对话历史"""
        channel = CommunicationChannel("test", ["智能体A"])
        
        # 添加消息
        for i in range(5):
            msg = Message(f"消息{i+1}", "智能体A", MessageType.GENERAL)
            channel.send_message(msg)
        
        # 获取所有历史
        all_history = channel.get_conversation_history()
        assert len(all_history) == 5
        
        # 获取限制数量的历史
        limited_history = channel.get_conversation_history(limit=3)
        assert len(limited_history) == 3
        assert limited_history[0].content == "消息3"  # 最近的3条
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        channel = CommunicationChannel("test", ["智能体A", "智能体B"])
        
        msg1 = Message("消息1", "智能体A", MessageType.ARGUMENT)
        msg2 = Message("消息2", "智能体B", MessageType.COUNTER)
        
        channel.send_message(msg1)
        channel.send_message(msg2)
        channel.mark_delivered(msg1.id)
        
        stats = channel.get_statistics()
        
        assert stats["channel_id"] == "test"
        assert set(stats["participants"]) == {"智能体A", "智能体B"}
        assert stats["status"] == "active"
        assert stats["total_messages"] == 2
        assert stats["messages_sent"] == 2
        assert stats["messages_delivered"] == 1
        assert stats["pending_messages"] == 1  # msg2 still pending
        assert "conversation_stats" in stats


class TestCommunication:
    """Communication类的单元测试"""
    
    def test_communication_creation(self):
        """测试通信管理器创建"""
        comm = Communication()
        
        assert len(comm.channels) == 1  # 包含广播通道
        assert "broadcast" in comm.channels
        assert len(comm.agent_channels) == 0
        assert len(comm.global_listeners) == 0
    
    def test_create_and_get_channel(self):
        """测试创建和获取通道"""
        comm = Communication()
        participants = ["智能体A", "智能体B"]
        
        # 创建通道
        channel = comm.create_channel("test_channel", participants)
        
        assert channel.channel_id == "test_channel"
        assert channel.participants == set(participants)
        assert comm.get_channel("test_channel") is not None
        
        # 验证智能体通道映射更新
        assert "test_channel" in comm.agent_channels["智能体A"]
        assert "test_channel" in comm.agent_channels["智能体B"]
        
        # 尝试创建重复通道
        with pytest.raises(ValueError, match="通道 .* 已存在"):
            comm.create_channel("test_channel", ["智能体C"])
    
    def test_delete_channel(self):
        """测试删除通道"""
        comm = Communication()
        channel = comm.create_channel("test", ["智能体A", "智能体B"])
        
        assert comm.get_channel("test") is not None
        
        # 删除通道
        result = comm.delete_channel("test")
        
        assert result is True
        assert comm.get_channel("test") is None
        assert "test" not in comm.agent_channels["智能体A"]
        assert "test" not in comm.agent_channels["智能体B"]
        
        # 尝试删除不存在的通道
        result = comm.delete_channel("nonexistent")
        assert result is False
    
    def test_join_and_leave_channel(self):
        """测试加入和离开通道"""
        comm = Communication()
        comm.create_channel("test", ["智能体A"])
        
        # 智能体B加入通道
        result = comm.join_channel("test", "智能体B")
        
        assert result is True
        channel = comm.get_channel("test")
        assert "智能体B" in channel.participants
        assert "test" in comm.agent_channels["智能体B"]
        
        # 智能体B离开通道
        result = comm.leave_channel("test", "智能体B")
        
        assert result is True
        assert "智能体B" not in channel.participants
        assert "test" not in comm.agent_channels["智能体B"]
        
        # 尝试操作不存在的通道
        assert comm.join_channel("nonexistent", "智能体C") is False
        assert comm.leave_channel("nonexistent", "智能体C") is False
    
    def test_send_message_with_channel(self):
        """测试指定通道发送消息"""
        comm = Communication()
        comm.create_channel("test", ["智能体A", "智能体B"])
        
        message = Message("测试消息", "智能体A", MessageType.ARGUMENT)
        
        result = comm.send_message(message, "test")
        
        assert result is True
        channel = comm.get_channel("test")
        assert len(channel.conversation.messages) == 1
    
    def test_send_direct_message(self):
        """测试发送点对点消息"""
        comm = Communication()
        
        result = comm.send_direct_message("智能体A", "智能体B", "私聊消息", MessageType.CLARIFICATION)
        
        assert result is True
        
        # 验证创建了直接通信通道
        direct_channel_id = "direct_智能体A_智能体B"
        channel = comm.get_channel(direct_channel_id)
        assert channel is not None
        assert channel.participants == {"智能体A", "智能体B"}
        assert len(channel.conversation.messages) == 1
        
        message = channel.conversation.messages[0]
        assert message.content == "私聊消息"
        assert message.sender == "智能体A"
        assert message.recipient == "智能体B"
        assert message.message_type == MessageType.CLARIFICATION
    
    def test_broadcast_message(self):
        """测试广播消息"""
        comm = Communication()
        
        result = comm.broadcast_message("智能体A", "广播内容", MessageType.GENERAL)
        
        assert result is True
        
        broadcast_channel = comm.get_channel("broadcast")
        assert len(broadcast_channel.conversation.messages) == 1
        
        message = broadcast_channel.conversation.messages[0]
        assert message.content == "广播内容"
        assert message.sender == "智能体A"
        assert message.message_type == MessageType.GENERAL
    
    def test_get_pending_messages_for_agent(self):
        """测试获取智能体的待处理消息"""
        comm = Communication()
        
        # 创建通道并添加消息
        comm.create_channel("test", ["智能体A", "智能体B"])
        comm.send_direct_message("智能体A", "智能体B", "直接消息")
        comm.broadcast_message("智能体A", "广播消息")
        
        # 获取智能体B的待处理消息
        pending = comm.get_pending_messages_for_agent("智能体B")
        
        # 应该包含直接消息和广播消息
        assert len(pending) >= 1
        
        # 验证返回格式 (message, channel_id)
        for message, channel_id in pending:
            assert isinstance(message, Message)
            assert isinstance(channel_id, str)
            assert message.sender != "智能体B"  # 不包含自己发送的消息
    
    def test_acknowledge_message(self):
        """测试确认消息"""
        comm = Communication()
        comm.create_channel("test", ["智能体A", "智能体B"])
        
        message = Message("测试", "智能体A", MessageType.ARGUMENT)
        comm.send_message(message, "test")
        
        result = comm.acknowledge_message(message.id, "test")
        
        assert result is True
        channel = comm.get_channel("test")
        assert channel.delivery_status[message.id] == MessageDeliveryStatus.ACKNOWLEDGED
    
    def test_message_routing(self):
        """测试消息自动路由"""
        comm = Communication()
        
        # 测试点对点消息路由
        direct_message = Message("直接消息", "智能体A", MessageType.ARGUMENT, recipient="智能体B")
        result = comm.send_message(direct_message)  # 不指定通道
        
        assert result is True
        # 应该自动创建直接通道
        direct_channel = comm.get_channel("direct_智能体A_智能体B")
        assert direct_channel is not None
        
        # 测试广播消息路由
        broadcast_message = Message("广播", "智能体A", MessageType.GENERAL)  # 无recipient
        result = comm.send_message(broadcast_message)
        
        assert result is True
        broadcast_channel = comm.get_channel("broadcast")
        assert len(broadcast_channel.conversation.messages) >= 1
    
    def test_custom_routing_rules(self):
        """测试自定义路由规则"""
        comm = Communication()
        comm.create_channel("priority", ["智能体A", "智能体B"])
        
        # 添加路由规则：高优先级消息路由到priority通道
        def priority_rule(message):
            if message.get_metadata("priority") == "high":
                return "priority"
            return None
        
        comm.add_routing_rule(priority_rule)
        
        # 发送高优先级消息
        high_priority_msg = Message("重要消息", "智能体A", MessageType.ARGUMENT)
        high_priority_msg.set_metadata("priority", "high")
        
        result = comm.send_message(high_priority_msg)
        
        assert result is True
        priority_channel = comm.get_channel("priority")
        assert len(priority_channel.conversation.messages) == 1
    
    @patch('builtins.print')
    def test_global_listeners(self, mock_print):
        """测试全局消息监听器"""
        comm = Communication()
        comm.create_channel("test", ["智能体A"])
        
        received_events = []
        
        def global_listener(message, channel_id):
            received_events.append((message.content, channel_id))
        
        def failing_listener(message, channel_id):
            raise Exception("监听器失败")
        
        comm.add_global_listener(global_listener)
        comm.add_global_listener(failing_listener)
        
        message = Message("测试消息", "智能体A", MessageType.ARGUMENT)
        comm.send_message(message, "test")
        
        # 验证监听器收到事件
        assert len(received_events) == 1
        assert received_events[0] == ("测试消息", "test")
        
        # 验证失败的监听器异常被捕获
        mock_print.assert_called()
    
    def test_get_agent_channels(self):
        """测试获取智能体参与的通道"""
        comm = Communication()
        
        comm.create_channel("channel1", ["智能体A", "智能体B"])
        comm.create_channel("channel2", ["智能体A", "智能体C"])
        comm.join_channel("channel2", "智能体B")
        
        # 智能体A参与两个通道
        agent_a_channels = comm.get_agent_channels("智能体A")
        assert len(agent_a_channels) == 2
        assert "channel1" in agent_a_channels
        assert "channel2" in agent_a_channels
        
        # 智能体B参与两个通道
        agent_b_channels = comm.get_agent_channels("智能体B")
        assert len(agent_b_channels) == 2
    
    def test_get_conversation_between_agents(self):
        """测试获取两个智能体之间的对话"""
        comm = Communication()
        
        # 发送直接消息，自动创建通道
        comm.send_direct_message("智能体A", "智能体B", "消息1")
        comm.send_direct_message("智能体B", "智能体A", "回复1")
        
        # 获取对话
        conversation = comm.get_conversation_between_agents("智能体A", "智能体B")
        
        assert conversation is not None
        assert len(conversation.messages) == 2
        
        # 测试参数顺序不影响结果 
        conversation2 = comm.get_conversation_between_agents("智能体B", "智能体A")
        assert conversation2 is conversation
        
        # 测试不存在的对话
        no_conversation = comm.get_conversation_between_agents("智能体A", "智能体C")
        assert no_conversation is None
    
    def test_get_communication_statistics(self):
        """测试获取通信统计信息"""
        comm = Communication()
        
        # 创建通道和发送消息
        comm.create_channel("test1", ["智能体A", "智能体B"])
        comm.create_channel("test2", ["智能体C"])
        comm.send_direct_message("智能体A", "智能体B", "消息1")
        comm.broadcast_message("智能体A", "广播消息")
        
        stats = comm.get_communication_statistics()
        
        assert stats["total_channels"] >= 3  # test1, test2, broadcast, direct
        assert stats["active_channels"] >= 3
        assert stats["total_messages"] >= 2
        assert stats["total_agents"] >= 3
        assert "channel_statistics" in stats
    
    def test_pause_and_resume_all_communication(self):
        """测试暂停和恢复所有通信"""
        comm = Communication()
        comm.create_channel("test", ["智能体A"])
        
        # 暂停所有通信
        comm.pause_all_communication()
        
        for channel in comm.channels.values():
            assert channel.status == CommunicationStatus.PAUSED
        
        # 恢复所有通信
        comm.resume_all_communication()
        
        for channel in comm.channels.values():
            assert channel.status == CommunicationStatus.ACTIVE


class TestContextManager:
    """ContextManager类的单元测试"""
    
    def test_context_manager_creation(self):
        """测试上下文管理器创建"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv)
        
        assert ctx_mgr.conversation is conv
        assert ctx_mgr.max_tokens == 4096
        assert ctx_mgr.user_input_weight == 2.0
        assert ctx_mgr.referenced_message_weight == 1.5
        assert callable(ctx_mgr._token_estimator)
    
    def test_context_manager_with_custom_params(self):
        """测试自定义参数的上下文管理器"""
        conv = Conversation()
        ctx_mgr = ContextManager(
            conv, 
            max_tokens=2048, 
            user_input_weight=3.0, 
            referenced_message_weight=2.0
        )
        
        assert ctx_mgr.max_tokens == 2048
        assert ctx_mgr.user_input_weight == 3.0
        assert ctx_mgr.referenced_message_weight == 2.0
    
    def test_calculate_message_score(self):
        """测试消息重要性得分计算"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv)
        
        # 创建测试消息
        user_msg = Message("用户输入", "用户", MessageType.USER_INPUT)
        normal_msg = Message("普通消息", "智能体A", MessageType.ARGUMENT)
        referenced_msg = Message("被引用消息", "智能体B", MessageType.COUNTER)
        reply_msg = Message("回复消息", "智能体A", MessageType.CLARIFICATION)
        reply_msg.add_reference(referenced_msg.id)
        
        all_messages = [user_msg, normal_msg, referenced_msg, reply_msg]
        
        # 测试用户输入消息得分
        user_score = ctx_mgr._calculate_message_score(user_msg, all_messages)
        assert user_score == ctx_mgr.user_input_weight
        
        # 测试普通消息得分
        normal_score = ctx_mgr._calculate_message_score(normal_msg, all_messages)
        assert normal_score == 1.0
        
        # 测试被引用消息得分
        referenced_score = ctx_mgr._calculate_message_score(referenced_msg, all_messages)
        assert referenced_score == ctx_mgr.referenced_message_weight
        
        # 测试用户输入且被引用的消息得分
        user_referenced_msg = Message("用户被引用", "用户", MessageType.USER_INPUT)
        reply_to_user = Message("回复用户", "智能体A", MessageType.COUNTER)
        reply_to_user.add_reference(user_referenced_msg.id)
        
        all_with_user_ref = all_messages + [user_referenced_msg, reply_to_user]
        user_ref_score = ctx_mgr._calculate_message_score(user_referenced_msg, all_with_user_ref)
        expected_score = ctx_mgr.user_input_weight * ctx_mgr.referenced_message_weight
        assert user_ref_score == expected_score
    
    def test_build_context_basic(self):
        """测试基本上下文构建"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv, max_tokens=1000)
        
        # 添加测试消息
        messages = []
        for i in range(5):
            msg = Message(f"消息{i+1}", "智能体A", MessageType.GENERAL)
            messages.append(msg)
            conv.add_message(msg)
        
        # 构建上下文
        context = ctx_mgr.build_context("智能体A")
        
        # 验证返回的消息按时间排序
        assert len(context) <= 5
        for i in range(1, len(context)):
            assert context[i-1].timestamp <= context[i].timestamp
    
    def test_build_context_with_scoring(self):
        """测试带得分的上下文构建"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv, max_tokens=1000)
        
        # 创建不同重要性的消息
        normal_msg = Message("普通消息", "智能体A", MessageType.GENERAL)
        user_msg = Message("用户输入", "用户", MessageType.USER_INPUT)
        referenced_msg = Message("被引用消息", "智能体B", MessageType.ARGUMENT)
        reply_msg = Message("回复消息", "智能体A", MessageType.COUNTER)
        reply_msg.add_reference(referenced_msg.id)
        
        # 添加消息（确保时间戳不同）
        base_time = datetime.now()
        for i, msg in enumerate([normal_msg, user_msg, referenced_msg, reply_msg]):
            msg.timestamp = base_time + timedelta(seconds=i)
            conv.add_message(msg)
        
        # 构建上下文
        context = ctx_mgr.build_context("智能体A")
        
        # 验证高分消息被包含（用户输入和被引用消息应该优先）
        context_contents = [msg.content for msg in context]
        assert "用户输入" in context_contents
        assert "被引用消息" in context_contents
        
        # 验证时间排序
        for i in range(1, len(context)):
            assert context[i-1].timestamp <= context[i].timestamp
    
    def test_build_context_with_token_limit(self):
        """测试token限制的上下文构建"""
        conv = Conversation()
        # 设置较小的token限制
        ctx_mgr = ContextManager(conv, max_tokens=50)
        
        # 添加多条消息
        long_messages = []
        for i in range(10):
            # 创建较长的消息（大约20个token）
            msg = Message(f"这是一条比较长的测试消息，编号是{i+1}，用于测试token限制", 
                         "智能体A", MessageType.GENERAL)
            long_messages.append(msg)
            conv.add_message(msg)
        
        # 构建上下文
        context = ctx_mgr.build_context("智能体A")
        
        # 验证上下文受token限制
        total_estimated_tokens = sum(ctx_mgr._token_estimator(msg.content) for msg in context)
        assert total_estimated_tokens <= ctx_mgr.max_tokens
        
        # 应该选择较少的消息
        assert len(context) < len(long_messages)
    
    def test_build_context_with_max_messages(self):
        """测试消息数量限制的上下文构建"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv)
        
        # 添加多条短消息
        for i in range(10):
            msg = Message(f"短消息{i+1}", "智能体A", MessageType.GENERAL)
            conv.add_message(msg)
        
        # 限制消息数量
        context = ctx_mgr.build_context("智能体A", max_messages=3)
        
        assert len(context) <= 3
    
    def test_build_context_empty_conversation(self):
        """测试空对话的上下文构建"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv)
        
        context = ctx_mgr.build_context("智能体A")
        
        assert len(context) == 0
    
    def test_get_formatted_context(self):
        """测试获取格式化上下文"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv)
        
        # 添加测试消息
        msg1 = Message("第一条消息", "智能体A", MessageType.ARGUMENT)
        msg2 = Message("第二条消息", "智能体B", MessageType.COUNTER)
        msg3 = Message("用户消息", "用户", MessageType.USER_INPUT)
        
        for msg in [msg1, msg2, msg3]:
            conv.add_message(msg)
        
        # 获取格式化上下文
        formatted = ctx_mgr.get_formatted_context("智能体A")
        
        # 验证格式
        lines = formatted.split("\n")
        assert len(lines) >= 3
        
        # 验证每行的格式：Sender (MessageType): Content
        for line in lines:
            assert "(" in line and "):" in line
        
        # 验证包含预期内容
        assert "智能体A (argument): 第一条消息" in formatted
        assert "智能体B (counter): 第二条消息" in formatted
        assert "用户 (user_input): 用户消息" in formatted
    
    def test_get_formatted_context_with_limits(self):
        """测试限制条件下的格式化上下文"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv, max_tokens=100)
        
        # 添加多条消息
        for i in range(5):
            msg = Message(f"消息{i+1}", f"智能体{i%2}", MessageType.GENERAL)
            conv.add_message(msg)
        
        # 获取限制数量的格式化上下文
        formatted = ctx_mgr.get_formatted_context("智能体0", max_messages=2)
        
        lines = formatted.split("\n")
        assert len(lines) <= 2
    
    def test_get_formatted_context_empty(self):
        """测试空对话的格式化上下文"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv)
        
        formatted = ctx_mgr.get_formatted_context("智能体A")
        
        assert formatted == ""
    
    def test_set_max_tokens(self):
        """测试更新最大token限制"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv, max_tokens=1000)
        
        assert ctx_mgr.max_tokens == 1000
        
        # 更新限制
        ctx_mgr.set_max_tokens(2000)
        assert ctx_mgr.max_tokens == 2000
    
    def test_summarize_and_compress_not_implemented(self):
        """测试摘要压缩功能（未实现）"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv)
        
        messages = [
            Message("消息1", "智能体A", MessageType.ARGUMENT),
            Message("消息2", "智能体B", MessageType.COUNTER)
        ]
        
        # 应该抛出NotImplementedError
        with pytest.raises(NotImplementedError, match="上下文摘要功能尚未实现"):
            ctx_mgr.summarize_and_compress(messages)
    
    def test_token_estimator(self):
        """测试token估算器"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv)
        
        # 测试简单的token估算（长度/4）
        short_text = "短文本"
        long_text = "这是一段比较长的文本，用于测试token估算功能是否正常工作"
        
        short_tokens = ctx_mgr._token_estimator(short_text)
        long_tokens = ctx_mgr._token_estimator(long_text)
        
        assert short_tokens == len(short_text) // 4
        assert long_tokens == len(long_text) // 4
        assert long_tokens > short_tokens
    
    def test_context_manager_repr(self):
        """测试上下文管理器的字符串表示"""
        conv = Conversation("test_conv_123")
        ctx_mgr = ContextManager(conv, max_tokens=2048)
        
        repr_str = repr(ctx_mgr)
        
        assert "ContextManager" in repr_str
        assert "test_conv_123" in repr_str
        assert "2048" in repr_str
    
    def test_complex_scoring_scenario(self):
        """测试复杂的得分计算场景"""
        conv = Conversation()
        ctx_mgr = ContextManager(conv, max_tokens=500)
        
        # 创建复杂的消息网络
        base_msg = Message("基础消息", "智能体A", MessageType.ARGUMENT)
        user_msg = Message("用户重要问题", "用户", MessageType.USER_INPUT)
        reply1 = Message("回复用户", "智能体A", MessageType.COUNTER)
        reply2 = Message("同意观点", "智能体B", MessageType.COUNTER)
        summary = Message("总结讨论", "智能体A", MessageType.SUMMARY)
        
        # 设置引用关系
        reply1.add_reference(user_msg.id)
        reply2.add_reference(base_msg.id)
        summary.add_reference(reply1.id)
        summary.add_reference(reply2.id)
        
        # 设置时间戳（确保有序）
        base_time = datetime.now()
        messages = [base_msg, user_msg, reply1, reply2, summary]
        for i, msg in enumerate(messages):
            msg.timestamp = base_time + timedelta(seconds=i)
            conv.add_message(msg)
        
        # 构建上下文
        context = ctx_mgr.build_context("智能体A")
        
        # 验证高重要性消息被包含
        context_contents = [msg.content for msg in context]
        
        # 用户输入应该有高分
        assert "用户重要问题" in context_contents
        
        # 被多次引用的消息应该有高分
        referenced_contents = []
        for msg in context:
            if any(msg.id in other.references for other in messages):
                referenced_contents.append(msg.content)
        
        # 至少有一些被引用的消息被包含
        assert len(referenced_contents) > 0


class TestMessagingIntegration:
    """消息系统集成测试"""
    
    def test_end_to_end_messaging_flow(self):
        """测试端到端的消息流程"""
        # 创建组件
        comm = Communication()
        conv = Conversation("integration_test")
        
        # 创建通道
        channel = comm.create_channel("debate_channel", ["逻辑者", "怀疑者"])
        
        # 发送初始消息
        initial_msg = create_argument_message(
            "逻辑者", 
            "人工智能将显著改善人类生活质量", 
            "怀疑者"
        )
        comm.send_message(initial_msg, "debate_channel")
        
        # 发送反驳消息
        counter_msg = create_counter_message(
            "怀疑者",
            "人工智能也可能带来就业问题和隐私风险",
            initial_msg.id,
            "逻辑者"
        )
        comm.send_message(counter_msg, "debate_channel")
        
        # 验证消息发送成功
        debate_channel = comm.get_channel("debate_channel")
        assert len(debate_channel.conversation.messages) == 2
        
        # 验证消息引用关系
        messages = debate_channel.conversation.messages
        assert counter_msg.id in [msg.id for msg in messages]
        assert initial_msg.id in counter_msg.references
        
        # 验证对话线程
        thread = debate_channel.conversation.get_conversation_thread(counter_msg.id)
        assert len(thread) == 2
        assert thread[0].content == initial_msg.content
        assert thread[1].content == counter_msg.content
    
    def test_context_manager_with_communication(self):
        """测试上下文管理器与通信系统集成"""
        # 创建通信系统
        comm = Communication()
        channel = comm.create_channel("ai_debate", ["逻辑者", "怀疑者", "用户"])
        
        # 发送一系列消息
        messages_data = [
            ("逻辑者", "AI技术正在快速发展", MessageType.ARGUMENT),
            ("怀疑者", "但是AI发展也带来了伦理问题", MessageType.COUNTER),
            ("用户", "请详细解释AI的伦理问题", MessageType.USER_INPUT),
            ("怀疑者", "AI可能导致算法偏见和决策不透明", MessageType.CLARIFICATION),
            ("逻辑者", "这些问题可以通过技术改进解决", MessageType.COUNTER)
        ]
        
        sent_messages = []
        for sender, content, msg_type in messages_data:
            if sender == "用户":
                msg = create_user_input_message(content, sender)
            else:
                msg = Message(content, sender, msg_type)
                if sent_messages:
                    msg.add_reference(sent_messages[-1].id)
            
            comm.send_message(msg, "ai_debate")
            sent_messages.append(msg)
        
        # 使用上下文管理器
        debate_channel = comm.get_channel("ai_debate")
        ctx_mgr = ContextManager(debate_channel.conversation, max_tokens=200)
        
        # 为怀疑者构建上下文
        context = ctx_mgr.build_context("怀疑者")
        
        # 验证上下文包含相关消息
        assert len(context) > 0
        
        # 用户输入应该被优先包含
        context_contents = [msg.content for msg in context]
        assert "请详细解释AI的伦理问题" in context_contents
        
        # 获取格式化上下文
        formatted_context = ctx_mgr.get_formatted_context("怀疑者", max_messages=3)
        assert isinstance(formatted_context, str)
        assert len(formatted_context) > 0
    
    def test_multi_channel_communication(self):
        """测试多通道通信"""
        comm = Communication()
        
        # 创建多个通道
        public_channel = comm.create_channel("public_debate", ["逻辑者", "怀疑者", "观察者"])
        private_channel = comm.create_channel("private_discussion", ["逻辑者", "怀疑者"])
        
        # 在公共通道发送消息
        public_msg = Message("这是公开讨论", "逻辑者", MessageType.ARGUMENT)
        comm.send_message(public_msg, "public_debate")
        
        # 发送私聊消息
        comm.send_direct_message("逻辑者", "怀疑者", "我们私下讨论一个观点", MessageType.CLARIFICATION)
        
        # 发送广播消息
        comm.broadcast_message("观察者", "欢迎大家参与讨论", MessageType.GENERAL)
        
        # 验证各通道的消息
        assert len(public_channel.conversation.messages) == 1
        assert len(private_channel.conversation.messages) == 0  # 私聊消息在不同通道
        
        # 验证直接通道被创建
        direct_channel = comm.get_channel("direct_怀疑者_逻辑者")
        assert direct_channel is not None
        assert len(direct_channel.conversation.messages) == 1
        
        # 验证广播通道有消息
        broadcast_channel = comm.get_channel("broadcast")
        assert len(broadcast_channel.conversation.messages) == 1
    
    def test_message_delivery_and_acknowledgment(self):
        """测试消息投递和确认流程"""
        comm = Communication()
        channel = comm.create_channel("test_delivery", ["发送者", "接收者"])
        
        # 发送消息
        message = Message("测试投递", "发送者", MessageType.GENERAL, recipient="接收者")
        comm.send_message(message, "test_delivery")
        
        # 检查待处理消息
        pending = comm.get_pending_messages_for_agent("接收者")
        assert len(pending) >= 1
        
        # 找到我们的消息
        our_message_tuple = None
        for msg, channel_id in pending:
            if msg.id == message.id:
                our_message_tuple = (msg, channel_id)
                break
        
        assert our_message_tuple is not None
        found_msg, found_channel_id = our_message_tuple
        
        # 标记消息已投递
        test_channel = comm.get_channel("test_delivery")
        test_channel.mark_delivered(message.id)
        
        # 确认消息
        result = comm.acknowledge_message(message.id, "test_delivery")
        assert result is True
        
        # 验证状态
        assert test_channel.delivery_status[message.id] == MessageDeliveryStatus.ACKNOWLEDGED
    
    def test_conversation_search_and_filter_integration(self):
        """测试对话搜索和过滤集成"""
        comm = Communication()
        channel = comm.create_channel("search_test", ["智能体A", "智能体B"])
        
        # 发送不同类型的消息
        test_messages = [
            ("智能体A", "讨论机器学习算法", MessageType.ARGUMENT),
            ("智能体B", "深度学习是机器学习的一个分支", MessageType.COUNTER),
            ("智能体A", "卷积神经网络在图像识别中很有效", MessageType.CLARIFICATION),
            ("智能体B", "但是需要大量的训练数据", MessageType.COUNTER),
            ("智能体A", "数据增强技术可以解决这个问题", MessageType.SUMMARY)
        ]
        
        for sender, content, msg_type in test_messages:
            msg = Message(content, sender, msg_type)
            comm.send_message(msg, "search_test")
        
        conversation = channel.conversation
        
        # 测试搜索功能
        ml_messages = conversation.search_messages("机器学习")
        assert len(ml_messages) == 2  # 包含"机器学习"的消息
        
        # 测试过滤功能
        agent_a_messages = conversation.filter_messages(lambda msg: msg.sender == "智能体A")
        assert len(agent_a_messages) == 3
        
        # 测试按类型获取
        counter_messages = conversation.get_messages_by_type(MessageType.COUNTER)
        assert len(counter_messages) == 2
        
        # 测试统计功能
        stats = conversation.get_statistics()
        assert stats["total_messages"] == 5
        assert stats["sender_statistics"]["智能体A"] == 3
        assert stats["sender_statistics"]["智能体B"] == 2
    
    def test_routing_and_context_integration(self):
        """测试路由和上下文管理集成"""
        comm = Communication()
        
        # 添加自定义路由规则
        def priority_routing(message):
            if "紧急" in message.content:
                return "urgent_channel"
            return None
        
        comm.add_routing_rule(priority_routing)
        
        # 创建紧急通道
        urgent_channel = comm.create_channel("urgent_channel", ["智能体A", "智能体B"])
        
        # 发送紧急消息（应该被路由到紧急通道）
        urgent_msg = Message("紧急：系统出现异常", "智能体A", MessageType.ARGUMENT)
        result = comm.send_message(urgent_msg)  # 不指定通道，测试自动路由
        
        assert result is True
        assert len(urgent_channel.conversation.messages) == 1
        
        # 发送普通消息（应该广播）
        normal_msg = Message("这是普通消息", "智能体B", MessageType.GENERAL)
        comm.send_message(normal_msg)
        
        broadcast_channel = comm.get_channel("broadcast")
        assert len(broadcast_channel.conversation.messages) >= 1
        
        # 使用上下文管理器处理紧急通道
        ctx_mgr = ContextManager(urgent_channel.conversation)
        context = ctx_mgr.build_context("智能体B")
        
        assert len(context) == 1
        assert context[0].content == "紧急：系统出现异常"
    
    def test_conversation_export_import_integration(self):
        """测试对话导出导入集成"""
        # 创建原始对话
        original_comm = Communication()
        channel = original_comm.create_channel("export_test", ["智能体A", "智能体B"])
        
        # 添加消息
        msg1 = create_argument_message("智能体A", "原始论点", "智能体B")
        msg2 = create_counter_message("智能体B", "反驳观点", msg1.id, "智能体A")
        
        original_comm.send_message(msg1, "export_test")
        original_comm.send_message(msg2, "export_test")
        
        # 导出对话
        conversation = channel.conversation
        exported_data = conversation.export_to_dict()
        
        # 创建新的对话系统并导入
        new_comm = Communication()
        new_channel = new_comm.create_channel("imported_test", ["智能体A", "智能体B"])
        
        # 导入对话
        imported_conversation = Conversation.from_dict(exported_data)
        
        # 验证导入的对话
        assert len(imported_conversation.messages) == 2
        assert imported_conversation.messages[0].content == "原始论点"
        assert imported_conversation.messages[1].content == "反驳观点"
        assert imported_conversation.messages[1].has_references()
        
        # 验证引用关系
        assert imported_conversation.messages[0].id in imported_conversation.messages[1].references


if __name__ == "__main__":
    pytest.main([__file__])