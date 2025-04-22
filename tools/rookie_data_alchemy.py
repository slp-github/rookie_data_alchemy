from collections.abc import Generator
import io
import json
from typing import Any
import re
import pandas as pd
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import File, Tool
from dify_plugin.entities.model.llm import LLMModelConfig
from dify_plugin.entities.model.message import SystemPromptMessage
from dify_plugin.interfaces import tool
from pydantic import InstanceOf
from utils.prompt_loader import PromptLoader


class RookieDataAlchemyTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        # 互斥校验
        has_data = tool_parameters['data'] != ""
        has_csv = tool_parameters['csv_data'] != ""
        
        if has_data and has_csv:
            raise ValueError("参数冲突：不能同时提供 data 和 csv_data")

        parsed_data = None
        try:
            if has_data:
                # 处理JSON数据（保持原有逻辑）
                data_input = tool_parameters["data"]
                parsed_data = self._safe_json_parse(data_input)
            elif has_csv:
                # 处理CSV文件对象
                csv_input = tool_parameters['csv_data']
                
                # 获取二进制内容并解码
                csv_bytes = io.BytesIO(csv_input.blob)
                print(csv_bytes)
                try:
                    csv_content = csv_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    # 尝试常见编码格式
                    for encoding in ['gbk', 'latin-1', 'utf-16']:
                        try:
                            csv_content = csv_bytes.decode(encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        raise ValueError("无法解码CSV文件，请确认文件编码")

                # 解析CSV内容
                
                from io import StringIO
                
                # 添加CSV格式校验
                if not csv_content.strip():
                    raise ValueError("CSV文件内容为空")
                if len(csv_content.splitlines()) < 2:
                    raise ValueError("CSV至少需要包含表头和数据行")

                df = pd.read_csv(
                    StringIO(csv_content),
                    skipinitialspace=True,
                    on_bad_lines='error'
                )
                parsed_data = df.to_json(orient='records', force_ascii=False)

            else:
                raise ValueError("必须提供 data 或 csv_data 参数")

        except pd.errors.ParserError as e:
            line_no = e.args[0].lineno if e.args else 'unknown'
            raise ValueError(f"CSV格式错误，第{line_no}行解析失败")
        except ValueError as ve:
            raise ve  # 重新抛出已处理的错误
        except Exception as e:
            raise ValueError(f"数据处理异常: {str(e)}")
        
        model_info= tool_parameters.get('model')
        # 初始化模板加载器
        prompt_loader = PromptLoader()
        # 构建模板上下文
        context = {
            'raw_data': parsed_data,
            'chart_type': self._get_chart_english(tool_parameters['chart_type']),
            'custom_requirements': tool_parameters.get('custom_requirements', '')
        }
        system_prompt = prompt_loader.get_prompt(context)
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
        json_res = self.robust_json_parser(response.message.content)
        yield self.create_text_message(self._add_echarts_code_fence(json_res))
    
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
    
    def _add_echarts_code_fence(self, data: dict) -> str:
        """
        将ECharts配置字典转换为带代码块标记的格式化字符串
        
        改进点：
        1. 输入改为接受字典类型
        2. 自动执行JSON序列化
        3. 添加格式化配置
        
        参数:
            data (dict): 解析后的ECharts配置字典
            
        返回:
            str: 带标准代码块标记的格式化JSON字符串
        """
        # 类型校验增强
        if not isinstance(data, dict):
            raise TypeError(f"需要字典类型，但收到 {type(data).__name__}")

        # 执行带格式化的JSON序列化
        formatted_json = json.dumps(
            data,
            indent=2,               # 2空格缩进
            ensure_ascii=False,     # 支持中文
            separators=(',', ': ')  # 优化分隔符排版
        )
        
        # 构造标准代码块
        return f"```echarts\n{formatted_json}\n```"
    
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
    def robust_json_parser(self, raw_str: str) -> dict:
        """
        智能解析包含或不包含代码块标记的JSON字符串
        功能特性：
        1. 自动去除```json ```代码块标记
        2. 处理首尾多余空白符
        3. 兼容单层/多层嵌套JSON
        4. 自动转义非法控制字符
        
        参数：
        raw_str : 需要解析的原始字符串
        
        返回：
        解析后的字典对象
        
        异常：
        当JSON格式错误时抛出json.JSONDecodeError
        """
        # 正则表达式匹配最外层代码块标记（兼容大小写和空白符）
        code_block_pattern = r"^\s*`{3,}json\s*?(.*?)`{3,}\s*$"
        
        # 尝试移除代码块标记
        cleaned_str = re.sub(
            pattern=code_block_pattern,
            repl=r"\1",  # 保留第一个捕获组内容
            string=str(raw_str).strip(),
            flags=re.DOTALL | re.IGNORECASE  # 跨行匹配且忽略大小写
        )
        
        try:
            # 尝试解析处理后的字符串
            return json.loads(cleaned_str)
        except json.JSONDecodeError as e:
            # 二次处理特殊字符
            sanitized_str = re.sub(
                r"[\x00-\x1F\x7F-\x9F]",  # 匹配控制字符
                lambda m: f"\\u{ord(m.group(0)):04x}",  # 转义为Unicode
                cleaned_str
            )
            return json.loads(sanitized_str)