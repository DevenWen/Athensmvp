"""
怀疑者角色实现
专注于批判思维和质疑反驳的AI智能体
"""

from typing import Optional, List
from src.agents.base_agent import BaseAgent
from src.core.ai_client import AIClient
from src.core.message import MessageType
from src.config.prompts import get_skeptic_prompt


class Skeptic(BaseAgent):
    """
    怀疑者角色
    专注于批判思维和质疑反驳，寻找论证中的漏洞和问题
    """
    
    def __init__(self, name: str = "怀疑者", ai_client: Optional[AIClient] = None):
        """
        初始化怀疑者
        
        Args:
            name: 智能体名称
            ai_client: AI客户端实例
        """
        if ai_client is None:
            ai_client = AIClient()
        
        super().__init__(
            name=name,
            role_prompt=get_skeptic_prompt(),
            ai_client=ai_client
        )
        
        # 怀疑者特有的元数据
        self.metadata.update({
            "role": "skeptic",
            "focus": "critical_thinking",
            "approach": "questioning_challenging"
        })
    
    def generate_response(self, context: str = "", temperature: float = 0.7) -> str:
        """
        生成质疑性回应
        
        Args:
            context: 上下文信息
            temperature: 生成温度参数（怀疑者使用适中温度保持创造性质疑）
            
        Returns:
            生成的回应内容
        """
        # 怀疑者使用适中温度以保持创造性和敏锐性
        skeptical_temperature = min(max(temperature, 0.6), 0.8)
        
        prompt = self._build_prompt(context)
        
        response = self.ai_client.generate_response(
            prompt=prompt,
            temperature=skeptical_temperature,
            max_tokens=1024
        )
        
        if response:
            # 创建并发送回应消息
            self.send_message(
                content=response,
                message_type=MessageType.COUNTER
            )
            return response
        else:
            fallback_response = "让我重新审视这个问题，可能还有我们没有考虑到的角度。"
            self.send_message(
                content=fallback_response,
                message_type=MessageType.SYSTEM
            )
            return fallback_response
    
    def challenge_argument(self, argument: str) -> str:
        """
        质疑论证
        
        Args:
            argument: 要质疑的论证
            
        Returns:
            质疑内容
        """
        challenge_prompt = f"""
        作为怀疑者，请对以下论证进行深入质疑：

        论证内容：{argument}

        请从以下角度进行质疑：
        1. 论证中的假设是否成立？
        2. 证据是否充分和可靠？
        3. 逻辑推理是否存在漏洞？
        4. 是否存在反例？
        5. 有哪些替代解释？
        
        保持建设性的质疑，提出有价值的问题。
        """
        
        response = self.ai_client.generate_response(
            prompt=challenge_prompt,
            temperature=0.7
        )
        
        if response:
            self.send_message(
                content=response,
                message_type=MessageType.COUNTER
            )
        
        return response or "无法完成论证质疑"
    
    def find_contradictions(self, statements: List[str]) -> str:
        """
        寻找陈述中的矛盾
        
        Args:
            statements: 陈述列表
            
        Returns:
            发现的矛盾分析
        """
        statements_text = "\n".join([f"{i+1}. {stmt}" for i, stmt in enumerate(statements)])
        
        contradiction_prompt = f"""
        作为怀疑者，请分析以下陈述中是否存在矛盾：

        陈述：
        {statements_text}

        请指出：
        1. 是否存在逻辑矛盾？
        2. 矛盾出现在哪些陈述之间？
        3. 矛盾的性质是什么？
        4. 如何解决这些矛盾？
        """
        
        response = self.ai_client.generate_response(
            prompt=contradiction_prompt,
            temperature=0.6
        )
        
        return response or "无法完成矛盾分析"
    
    def propose_counterexamples(self, general_claim: str) -> str:
        """
        提出反例
        
        Args:
            general_claim: 一般性声明
            
        Returns:
            反例和分析
        """
        counterexample_prompt = f"""
        作为怀疑者，请为以下一般性声明寻找反例：

        声明：{general_claim}

        请提供：
        1. 具体的反例案例
        2. 反例如何挑战原声明
        3. 反例的可信度分析
        4. 对原声明的修正建议
        """
        
        response = self.ai_client.generate_response(
            prompt=counterexample_prompt,
            temperature=0.7
        )
        
        if response:
            self.send_message(
                content=response,
                message_type=MessageType.COUNTER
            )
        
        return response or "无法提出有效反例"
    
    def question_assumptions(self, argument: str) -> str:
        """
        质疑论证中的假设
        
        Args:
            argument: 包含假设的论证
            
        Returns:
            对假设的质疑
        """
        assumption_prompt = f"""
        作为怀疑者，请识别并质疑以下论证中的假设：

        论证：{argument}

        请分析：
        1. 论证基于哪些假设？
        2. 这些假设是否合理？
        3. 假设是否得到了证实？
        4. 如果假设不成立会如何？
        
        保持学术诚意，提出有根据的质疑。
        """
        
        response = self.ai_client.generate_response(
            prompt=assumption_prompt,
            temperature=0.7
        )
        
        return response or "无法完成假设质疑"
    
    def explore_alternatives(self, explanation: str) -> str:
        """
        探索替代解释
        
        Args:
            explanation: 当前解释
            
        Returns:
            替代解释和分析
        """
        alternative_prompt = f"""
        作为怀疑者，请为以下解释提出替代的可能性：

        当前解释：{explanation}

        请考虑：
        1. 还有哪些可能的解释？
        2. 这些替代解释的合理性如何？
        3. 如何验证不同解释的有效性？
        4. 哪些因素可能被忽略了？
        """
        
        response = self.ai_client.generate_response(
            prompt=alternative_prompt,
            temperature=0.8
        )
        
        return response or "无法提出替代解释"
    
    def respond_to_logic(self, logical_argument: str) -> str:
        """
        回应逻辑者的论证
        
        Args:
            logical_argument: 逻辑者的论证
            
        Returns:
            质疑性回应
        """
        response_context = f"""
        逻辑者提出了以下论证：{logical_argument}
        
        请以怀疑者的身份，从批判性思维的角度回应这个论证。寻找可能的漏洞、质疑假设、提出反例。
        """
        
        return self.generate_response(context=response_context, temperature=0.7)