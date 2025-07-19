#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI报告生成模块
集成多种大模型API进行智能报告生成，支持OpenAI、DeepSeek、智谱AI、百度文心一言、阿里通义千问等
"""

import openai
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import time
import re
import requests


class AIReportGenerator:
    """AI报告生成器"""
    
    # 支持的大模型提供商（仅国内服务商）
    PROVIDERS = {
        "DeepSeek": {
            "api_base": "https://api.deepseek.com/v1",
            "models": ["deepseek-chat", "deepseek-coder"]
        },
        "智谱AI": {
            "api_base": "https://open.bigmodel.cn/api/paas/v4",
            "models": ["glm-4", "glm-3-turbo", "cogview-3"]
        },
        "百度文心": {
            "api_base": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxin/chat",
            "models": ["ERNIE-Bot-4", "ERNIE-Bot-turbo"]
        },
        "阿里通义": {
            "api_base": "https://dashscope.aliyuncs.com/api/v1",
            "models": ["qwen-turbo", "qwen-plus", "qwen-max"]
        },
        "Doubao": {
            "api_base": "https://ark.cn-beijing.volces.com/api/v3",
            "models": ["doubao-lite-4k", "doubao-pro-4k", "doubao-pro-32k"]
        }
    }
    
    def __init__(self, api_config: Union[Dict[str, Any], str], 
                 api_base: str = None, model: str = None, 
                 temperature: float = 0.7, max_tokens: int = 1000, 
                 timeout: int = 30, retry_count: int = 3):
        
        # 处理不同的初始化方式
        if isinstance(api_config, dict):
            # 从配置字典初始化
            self.api_key = api_config.get("api_key", "")
            self.provider = api_config.get("provider", "DeepSeek")
            
            # 获取API基础URL，优先使用配置中的值，如果为空则使用默认值
            config_api_base = api_config.get("api_base_url", "").strip()
            if config_api_base:
                self.api_base = config_api_base
            else:
                # 如果配置中没有或为空，则使用提供商的默认API基础URL
                self.api_base = self.PROVIDERS.get(self.provider, {}).get("api_base", "")
            
            self.model = api_config.get("model") or self._get_default_model(self.provider)
            self.temperature = api_config.get("temperature", temperature)
            self.max_tokens = api_config.get("max_tokens", max_tokens)
            self.timeout = api_config.get("timeout", timeout)
            self.retry_count = api_config.get("retry_count", retry_count)
            self.system_prompt = api_config.get("system_prompt", "")
        else:
            # 从参数初始化
            self.api_key = api_config  # api_config作为api_key
            self.provider = self._detect_provider(api_base) if api_base else "DeepSeek"
            self.api_base = api_base or self.PROVIDERS.get(self.provider, {}).get("api_base")
            self.model = model or self._get_default_model(self.provider)
            self.temperature = temperature
            self.max_tokens = max_tokens
            self.timeout = timeout
            self.retry_count = retry_count
            self.system_prompt = ""
        
        # 配置OpenAI客户端（用于OpenAI和兼容OpenAI API的模型）
        if self._is_openai_compatible():
            # 使用新版OpenAI客户端
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base if self.api_base and self.api_base != "https://api.openai.com/v1" else None
            )
    
    def _detect_provider(self, api_base: str) -> str:
        """根据API基础URL检测提供商"""
        if not api_base:
            return "DeepSeek"
            
        api_base_lower = api_base.lower()
        
        # 精确匹配各个提供商的特征域名
        if "deepseek.com" in api_base_lower:
            return "DeepSeek"
        elif "bigmodel.cn" in api_base_lower:
            return "智谱AI"
        elif "baidubce.com" in api_base_lower or "baidu" in api_base_lower:
            return "百度文心"
        elif "aliyuncs.com" in api_base_lower or "dashscope" in api_base_lower:
            return "阿里通义"
        elif "volces.com" in api_base_lower or "doubao" in api_base_lower:
            return "Doubao"
        
        return "DeepSeek"  # 默认为DeepSeek
    
    def _get_default_model(self, provider: str) -> str:
        """获取提供商的默认模型"""
        provider_info = self.PROVIDERS.get(provider, {})
        models = provider_info.get("models", [])
        return models[0] if models else "deepseek-chat"
    
    def _is_openai_compatible(self) -> bool:
        """检查是否使用OpenAI兼容的API"""
        return self.provider in ["DeepSeek", "Doubao"]
    
    def _call_openai_api(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """调用大模型API"""
        for attempt in range(self.retry_count):
            try:
                # 根据提供商选择不同的调用方式
                if self._is_openai_compatible():
                    # 使用OpenAI兼容的API调用（新版客户端）
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        timeout=self.timeout
                    )
                    return response.choices[0].message.content.strip()
                
                elif self.provider == "智谱AI":
                    # 智谱AI API调用
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    payload = {
                        "model": self.model,
                        "messages": messages,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens
                    }
                    response = requests.post(self.api_base, headers=headers, json=payload, timeout=self.timeout)
                    response.raise_for_status()
                    return response.json()["choices"][0]["message"]["content"]
                
                elif self.provider == "百度文心":
                    # 百度文心API调用
                    headers = {"Content-Type": "application/json"}
                    payload = {
                        "messages": messages,
                        "temperature": self.temperature,
                        "token_limit": self.max_tokens
                    }
                    url = f"{self.api_base}/{self.model}?access_token={self.api_key}"
                    response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
                    response.raise_for_status()
                    return response.json()["result"]
                
                elif self.provider == "阿里通义":
                    # 阿里通义千问API调用
                    headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                    payload = {
                        "model": self.model,
                        "input": {"messages": messages},
                        "parameters": {
                            "temperature": self.temperature,
                            "max_tokens": self.max_tokens
                        }
                    }
                    response = requests.post(f"{self.api_base}/generation", headers=headers, json=payload, timeout=self.timeout)
                    response.raise_for_status()
                    return response.json()["output"]["text"]
                
                elif self.provider == "讯飞星火":
                    # 讯飞星火API调用
                    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
                    payload = {
                        "header": {"app_id": self.api_key.split(".")[0]},
                        "parameter": {
                            "chat": {
                                "domain": self.model,
                                "temperature": self.temperature,
                                "max_tokens": self.max_tokens
                            }
                        },
                        "payload": {"message": {"text": messages}}
                    }
                    response = requests.post(self.api_base, headers=headers, json=payload, timeout=self.timeout)
                    response.raise_for_status()
                    return response.json()["payload"]["text"]["content"]
                
                else:
                    # 默认使用OpenAI兼容的API调用（新版客户端）
                    # 确保客户端已初始化
                    if not hasattr(self, 'client'):
                        self.client = openai.OpenAI(
                            api_key=self.api_key,
                            base_url=self.api_base
                        )
                    
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        timeout=self.timeout
                    )
                    return response.choices[0].message.content.strip()
            
            except Exception as e:
                 # 处理不同类型的错误
                 if "rate limit" in str(e).lower():
                     # 处理频率限制错误
                     if attempt < self.retry_count - 1:
                         wait_time = (2 ** attempt) * 2  # 指数退避
                         print(f"API调用频率限制，等待{wait_time}秒后重试...")
                         time.sleep(wait_time)
                     else:
                         print("API调用频率限制，已达到最大重试次数")
                         return None
                 elif "api" in str(e).lower() and "error" in str(e).lower():
                     # 处理API错误
                     print(f"API错误: {e}")
                     if attempt < self.retry_count - 1:
                         time.sleep(1)
                     else:
                         return None
                 else:
                     # 处理其他异常
                     print(f"API调用异常: {e}")
                     if attempt < self.retry_count - 1:
                         time.sleep(1)
                     else:
                         return None
        
        return None
    
    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        try:
            # 简单的测试消息
            messages = [
                {"role": "system", "content": "你是一个助手。"},
                {"role": "user", "content": "请回复'连接测试成功'"}
            ]
            
            # 调用API
            response = self._call_openai_api(messages)
            
            if response:
                return {
                    "success": True,
                    "message": f"{self.provider} API连接成功！模型: {self.model}",
                    "provider": self.provider,
                    "model": self.model,
                    "response": response[:50] + "..." if len(response) > 50 else response
                }
            else:
                return {
                    "success": False,
                    "message": f"{self.provider} API连接失败，请检查API密钥和网络连接。",
                    "provider": self.provider,
                    "model": self.model
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"{self.provider} API连接测试异常: {str(e)}",
                "provider": self.provider,
                "model": self.model
            }
    
    def generate_daily_report(self, work_logs: List[Dict], system_prompt: str = None) -> Optional[str]:
        """生成日报"""
        if not work_logs:
            return None
        
        # 默认系统提示词
        if not system_prompt:
            system_prompt = (
                "你是一个专业的工作报告助手。请根据提供的工作日志生成简洁、专业的日报。"
                "报告应包含：1. 今日完成的主要工作；2. 遇到的问题和解决方案；3. 明日工作计划。"
                "语言要简洁明了，突出重点，避免冗余。"
            )
        
        # 整理工作日志
        log_content = "\n".join([
            f"- {log.get('content', '')} (类型: {log.get('type', '工作')}, 优先级: {log.get('priority', '中')}, 标签: {log.get('tags', [])})"
            for log in work_logs
        ])
        
        user_prompt = f"请根据以下工作日志生成今日工作日报：\n\n{log_content}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call_openai_api(messages)
    
    def generate_weekly_report(self, work_logs: List[Dict], system_prompt: str = None) -> Optional[str]:
        """生成周报"""
        if not work_logs:
            return None
        
        if not system_prompt:
            system_prompt = (
                "你是一个专业的工作报告助手。请根据提供的一周工作日志生成专业的周报。"
                "报告应包含：1. 本周主要成果和完成的项目；2. 重要进展和里程碑；3. 遇到的挑战和解决方案；4. 下周工作重点。"
                "请按重要性排序，突出关键成果。"
            )
        
        # 按日期分组整理日志
        logs_by_date = {}
        for log in work_logs:
            date = log.get('date', datetime.now().strftime('%Y-%m-%d'))
            if date not in logs_by_date:
                logs_by_date[date] = []
            logs_by_date[date].append(log)
        
        log_content = ""
        for date, daily_logs in sorted(logs_by_date.items()):
            log_content += f"\n{date}:\n"
            for log in daily_logs:
                log_content += f"  - {log.get('content', '')} (类型: {log.get('type', '工作')}, 优先级: {log.get('priority', '中')})\n"
        
        user_prompt = f"请根据以下一周的工作日志生成周报：\n{log_content}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call_openai_api(messages)
    
    def generate_monthly_report(self, work_logs: List[Dict], system_prompt: str = None) -> Optional[str]:
        """生成月报"""
        if not work_logs:
            return None
        
        if not system_prompt:
            system_prompt = (
                "你是一个专业的工作报告助手。请根据提供的一个月工作日志生成全面的月报。"
                "报告应包含：1. 月度主要成果和完成的重要项目；2. 关键指标和数据；3. 重要里程碑和突破；"
                "4. 遇到的主要挑战和解决方案；5. 经验总结和改进建议；6. 下月工作目标和计划。"
                "请突出重点成果，提供数据支撑，体现工作价值。"
            )
        
        # 按周分组整理日志
        logs_by_week = {}
        for log in work_logs:
            date_str = log.get('date', datetime.now().strftime('%Y-%m-%d'))
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                week_num = date_obj.isocalendar()[1]
                week_key = f"第{week_num}周"
                if week_key not in logs_by_week:
                    logs_by_week[week_key] = []
                logs_by_week[week_key].append(log)
            except:
                # 如果日期解析失败，放入其他分类
                if "其他" not in logs_by_week:
                    logs_by_week["其他"] = []
                logs_by_week["其他"].append(log)
        
        log_content = ""
        for week, weekly_logs in logs_by_week.items():
            log_content += f"\n{week}：\n"
            for log in weekly_logs:
                log_content += f"  - {log.get('content', '')} (类型: {log.get('type', '工作')}, 优先级: {log.get('priority', '中')})\n"
        
        user_prompt = f"请根据以下一个月的工作日志生成月报：\n{log_content}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call_openai_api(messages)
    
    def generate_custom_report(self, work_logs: List[Dict], custom_prompt: str, 
                             system_prompt: str = None) -> Optional[str]:
        """生成自定义报告"""
        if not work_logs or not custom_prompt:
            return None
        
        if not system_prompt:
            system_prompt = (
                "你是一个专业的工作报告助手。请根据用户的具体要求和提供的工作日志生成报告。"
                "确保报告内容准确、专业、符合用户需求。"
            )
        
        # 整理工作日志
        log_content = "\n".join([
            f"- {log.get('content', '')} (日期: {log.get('date', '')}, 类型: {log.get('type', '工作')}, 优先级: {log.get('priority', '中')})"
            for log in work_logs
        ])
        
        user_prompt = f"{custom_prompt}\n\n工作日志：\n{log_content}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call_openai_api(messages)
    
    def generate_smart_report(self, work_logs: List[Dict], report_type: str = "daily") -> Optional[str]:
        """智能补报 - 自动生成报告"""
        if not work_logs:
            # 如果没有日志，生成一个简单的报告
            if report_type == "daily":
                return "今日暂无具体工作记录，主要进行了日常工作和任务处理。明日将继续推进相关项目进展。"
            elif report_type == "weekly":
                return "本周主要进行了日常工作和项目推进，具体工作内容待补充记录。下周将加强工作日志记录，提高工作效率。"
            else:
                return "本期间主要进行了日常工作，具体内容待补充。后续将完善工作记录机制。"
        
        # 根据报告类型选择生成方法
        if report_type == "daily":
            return self.generate_daily_report(work_logs)
        elif report_type == "weekly":
            return self.generate_weekly_report(work_logs)
        elif report_type == "monthly":
            return self.generate_monthly_report(work_logs)
        else:
            return self.generate_daily_report(work_logs)
    
    def enhance_report(self, original_report: str, enhancement_type: str = "polish") -> Optional[str]:
        """报告增强和润色"""
        if not original_report:
            return None
        
        enhancement_prompts = {
            "polish": "请对以下工作报告进行润色，使其更加专业、简洁、有条理：",
            "expand": "请对以下工作报告进行扩展，增加更多细节和分析：",
            "summarize": "请对以下工作报告进行精简，提取核心要点：",
            "format": "请对以下工作报告进行格式优化，使其结构更清晰："
        }
        
        system_prompt = "你是一个专业的文档编辑助手，擅长优化和改进工作报告的质量。"
        user_prompt = f"{enhancement_prompts.get(enhancement_type, enhancement_prompts['polish'])}\n\n{original_report}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call_openai_api(messages)
    
    def test_connection(self) -> Dict[str, Any]:
        """测试AI服务连接"""
        result = {
            "success": False,
            "message": "",
            "details": {}
        }
        
        try:
            # 发送一个简单的测试请求
            messages = [
                {"role": "system", "content": "你是一个测试助手。"},
                {"role": "user", "content": "请回复'连接测试成功'"}
            ]
            
            response = self._call_openai_api(messages)
            
            if response:
                result["success"] = True
                result["message"] = "AI服务连接测试成功"
                result["details"]["model"] = self.model
                result["details"]["response"] = response[:50] + "..." if len(response) > 50 else response
            else:
                result["message"] = "AI服务连接失败，请检查API配置"
        
        except Exception as e:
            result["message"] = f"连接测试异常: {str(e)}"
        
        return result


def test_ai_connection(api_key: str, api_base: str = "https://api.deepseek.com/v1", 
                      model: str = "deepseek-chat") -> Dict[str, Any]:
    """测试AI连接的便捷函数"""
    if not api_key:
        return {
            "success": False,
            "message": "请先配置AI API Key",
            "details": {}
        }
    
    try:
        generator = AIReportGenerator(api_key, api_base, model)
        return generator.test_connection()
    except Exception as e:
        return {
            "success": False,
            "message": f"初始化AI生成器失败: {str(e)}",
            "details": {}
        }