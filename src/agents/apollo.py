"""
Apollo角色实现
专注于逻辑论证和支持观点的AI智能体
"""

from typing import Optional
from src.agents.base_agent import BaseAgent
from src.core.ai_client import AIClient
from src.core.message import MessageType
from src.config.prompts import get_apollo_prompt


class Apollo(BaseAgent):
    """
    Apollo角色
    专注于逻辑论证和支持观点，倾向于寻找证据和理性分析
    """
    
    role_name = "Apollo"
    display_name = "Apollo"
    description = "Logic and reason focused AI agent"
    
    def __init__(self, name: str = "Apollo", ai_client: Optional[AIClient] = None):
        """
        初始化Apollo
        
        Args:
            name: 智能体名称
            ai_client: AI客户端实例
        """
        if ai_client is None:
            ai_client = AIClient()
        
        super().__init__(
            name=name,
            role_prompt=get_apollo_prompt(),
            ai_client=ai_client
        )
        
        # Apollo特有的元数据
        self.metadata.update({
            "role": "apollo",
            "focus": "logical_reasoning",
            "approach": "supportive_argumentation"
        })
    
    def generate_response(self, context: str = "", temperature: float = 0.7) -> str:
        """
        生成逻辑性回应
        
        Args:
            context: 上下文信息
            temperature: 生成温度参数（Apollo使用较低温度保持理性）
            
        Returns:
            生成的回应内容
        """
        # Apollo使用较低的温度以保持理性和一致性
        logical_temperature = min(temperature, 0.6)
        
        prompt = self._build_prompt(context)
        
        response = self.ai_client.generate_response(
            prompt=prompt,
            temperature=logical_temperature,
            max_tokens=1024
        )
        
        if response:
            # 创建并发送回应消息
            self.send_message(
                content=response,
                message_type=MessageType.ARGUMENT
            )
            return response
        else:
            fallback_response = "抱歉，我现在无法生成回应。让我重新组织思路。"
            self.send_message(
                content=fallback_response,
                message_type=MessageType.SYSTEM
            )
            return fallback_response
    
    def analyze_argument(self, argument: str) -> str:
        """
        分析论证结构
        
        Args:
            argument: 要分析的论证
            
        Returns:
            分析结果
        """
        analysis_prompt = f"""
        作为Apollo，请分析以下论证的逻辑结构：

        论证内容：{argument}

        请从以下角度进行分析：
        1. 主要论点是什么？
        2. 支撑证据有哪些？
        3. 逻辑链条是否完整？
        4. 有哪些可以进一步加强的地方？
        """
        
        response = self.ai_client.generate_response(
            prompt=analysis_prompt,
            temperature=0.5
        )
        
        return response or "无法完成论证分析"
    
    def build_supporting_argument(self, topic: str, position: str) -> str:
        """
        构建支持性论证
        
        Args:
            topic: 讨论话题
            position: 要支持的立场
            
        Returns:
            支持性论证
        """
        support_prompt = f"""
        作为Apollo，请为以下立场构建一个有力的支持性论证：

        话题：{topic}
        立场：{position}

        请提供：
        1. 清晰的论点声明
        2. 3-4个具体的支撑论据
        3. 逻辑连接和推理过程
        4. 可能的反驳预防
        """
        
        response = self.ai_client.generate_response(
            prompt=support_prompt,
            temperature=0.6
        )
        
        if response:
            self.send_message(
                content=response,
                message_type=MessageType.ARGUMENT
            )
        
        return response or "无法构建支持性论证"
    
    def refine_logic(self, rough_argument: str) -> str:
        """
        优化论证的逻辑性
        
        Args:
            rough_argument: 初步的论证
            
        Returns:
            优化后的论证
        """
        refine_prompt = f"""
        作为Apollo，请优化以下论证的逻辑性和说服力：

        原始论证：{rough_argument}

        请改进：
        1. 论证结构的清晰度
        2. 逻辑连接的严密性
        3. 证据的有效性
        4. 表达的准确性
        """
        
        response = self.ai_client.generate_response(
            prompt=refine_prompt,
            temperature=0.5
        )
        
        return response or rough_argument
    
    def respond_to_skepticism(self, skeptical_challenge: str) -> str:
        """
        回应怀疑者的质疑
        
        Args:
            skeptical_challenge: 怀疑者的质疑
            
        Returns:
            回应内容
        """
        response_context = f"""
        Muses提出了以下质疑：{skeptical_challenge}
        
        请以Apollo的身份，理性地回应这个质疑。保持开放心态，但也要为你的观点提供有力的辩护。
        """
        
        return self.generate_response(context=response_context, temperature=0.6)