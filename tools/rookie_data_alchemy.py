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
            'chart_type': self._get_chart_english(tool_parameters['chart_type'])
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
    
    def _get_chart_english(self, chinese_name):
        """
        根据用户输入的中文图表名称，返回对应的英文值。
        如果无法匹配，则返回默认值 'line'。
        
        Args:
            chinese_name (str): 用户输入的中文图表名称
        
        Returns:
            str: 对应的英文类型（未找到则返回 'line'）
        """
        chart_mapping = {
            "柱状图": "bar",
            "折线图": "line",
            "饼图": "pie",
            "散点图": "scatter",
            "带有涟漪特效动画的散点（气泡）图": "effectScatter",
            "K线图": "candlestick",
            "雷达图": "radar",
            "热力图": "heatmap",
            "树图": "tree",
            "矩形树图": "treemap",
            "旭日图": "sunburst",
            "地图": "map",
            "路径图": "lines",  # 注意与 'line' 的区别
        }
        return chart_mapping.get(chinese_name, 'line')  # 未找到则返回默认 'line'