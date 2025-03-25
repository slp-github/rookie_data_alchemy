from collections.abc import Generator
import json
from typing import Any
import re
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from dify_plugin.entities.model.llm import LLMModelConfig
from dify_plugin.entities.model.message import SystemPromptMessage
from dify_plugin.interfaces import tool

from utils.prompt_loader import PromptLoader

class RookieDataAlchemyTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        print(f"RookieDataAlchemyTool: {tool_parameters}")
        # 格式化用户输入
        data = self._safe_json_parse(tool_parameters["data"])
        
        model_info= tool_parameters.get('model')

        # 初始化模板加载器
        prompt_loader = PromptLoader()
        # 构建模板上下文
        context = {
            'raw_data': data,
            'chart_type': tool_parameters.get('chart_type','line'),
        }

        system_prompt = prompt_loader.get_prompt(context)
        print(system_prompt)
        response = self.session.model.llm.invoke(
            model_config=LLMModelConfig(
                provider=model_info.get('provider'),
                model=model_info.get('model'),
                mode=model_info.get('mode'),
                completion_params=model_info.get('completion_params')
            ),
            prompt_messages=[
                SystemPromptMessage(content=system_prompt),
            ],
            stream=False
        )
        print(response.message.content)
        yield self.create_text_message(self._add_echarts_code_fence(response.message.content))
    
    def _safe_json_parse(self, input_str):
        # 预处理：替换单引号为双引号，移除尾部逗号
        input_str = re.sub(
            r"'([^']+)'",  # 匹配单引号字符串
            r'"\1"', 
            input_str
        )
        input_str = re.sub(
            r',\s*}(\s*)$',  # 移除对象尾部逗号
            r'\1}', 
            input_str
        )
        input_str = re.sub(
            r',\s*](\s*)$',  # 移除数组尾部逗号
            r'\1]', 
            input_str
        )
        return json.loads(input_str)
    
    def _add_echarts_code_fence(self, text: str) -> str:
        """
        为文本添加ECharts代码块标记
        
        参数:
            text (str): 需要包装的原始文本
            
        返回:
            str: 添加了```echarts和```标记的文本
            
        异常:
            TypeError: 当输入不是字符串时抛出
        """
        # 类型安全检查
        if not isinstance(text, str):
            raise TypeError(f"预期字符串类型，但收到 {type(text).__name__}")
        
        # 处理空字符串的特殊情况
        if not text.strip():
            return "```echarts\n\n```"
        
        # 自动格式化换行
        formatted_text = text.strip('\n')  # 去除首尾空行
        return f"```echarts\n{formatted_text}\n```"