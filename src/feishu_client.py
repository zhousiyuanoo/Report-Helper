#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书API客户端模块
负责与飞书开放平台的交互
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging


class FeishuClient:
    """飞书API客户端"""
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.tenant_access_token = None
        self.token_expire_time = 0
    
    def get_tenant_access_token(self) -> Optional[str]:
        """获取tenant_access_token"""
        # 检查token是否过期
        if self.tenant_access_token and time.time() < self.token_expire_time:
            return self.tenant_access_token
        
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                self.tenant_access_token = result["tenant_access_token"]
                # 设置过期时间（提前5分钟刷新）
                self.token_expire_time = time.time() + result["expire"] - 300
                return self.tenant_access_token
            else:
                print(f"获取token失败: {result.get('msg')}")
                return None
        except Exception as e:
            print(f"获取token异常: {e}")
            return None
    
    def get_chat_info(self, chat_id: str) -> Optional[Dict]:
        """获取群聊信息"""
        token = self.get_tenant_access_token()
        if not token:
            return None
        
        url = f"{self.base_url}/im/v1/chats/{chat_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                return result["data"]
            else:
                print(f"获取群聊信息失败: {result.get('msg')}")
                return None
        except Exception as e:
            print(f"获取群聊信息异常: {e}")
            return None
    
    def send_message(self, chat_id: str, message_type: str, content: Dict) -> bool:
        """发送消息到群聊"""
        token = self.get_tenant_access_token()
        if not token:
            return False
        
        url = f"{self.base_url}/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        data = {
            "receive_id": chat_id,
            "receive_id_type": "chat_id",
            "msg_type": message_type,
            "content": json.dumps(content, ensure_ascii=False)
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                return True
            else:
                print(f"发送消息失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"发送消息异常: {e}")
            return False
    
    def create_report_card(self, report_content: str, report_type: str = "日报") -> Dict:
        """创建报告卡片消息"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        card_content = {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": f"📋 **{report_type}** - {current_time}",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "content": report_content,
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "content": "🤖 *由牛马日报助手自动生成*",
                        "tag": "lark_md"
                    }
                }
            ],
            "header": {
                "template": "blue",
                "title": {
                    "content": f"📊 工作{report_type}",
                    "tag": "plain_text"
                }
            }
        }
        
        return card_content
    
    def send_report(self, chat_id: str, report_content: str, 
                   message_format: str = "card", report_type: str = "日报") -> bool:
        """发送报告到飞书群聊"""
        if message_format == "text":
            # 纯文本格式
            content = {"text": f"📋 工作{report_type}\n\n{report_content}\n\n🤖 由牛马日报助手自动生成"}
            return self.send_message(chat_id, "text", content)
        
        elif message_format == "markdown":
            # Markdown格式
            md_content = f"📋 **工作{report_type}**\n\n{report_content}\n\n🤖 *由牛马日报助手自动生成*"
            content = {"content": md_content}
            return self.send_message(chat_id, "post", content)
        
        else:
            # 卡片格式（默认）
            card_content = self.create_report_card(report_content, report_type)
            return self.send_message(chat_id, "interactive", card_content)
    
    def test_connection(self) -> Dict[str, Any]:
        """测试飞书连接"""
        result = {
            "success": False,
            "message": "",
            "details": {}
        }
        
        # 测试获取token
        token = self.get_tenant_access_token()
        if not token:
            result["message"] = "获取访问令牌失败，请检查App ID和App Secret"
            return result
        
        result["details"]["token_status"] = "✅ 访问令牌获取成功"
        
        # 测试API调用
        try:
            url = f"{self.base_url}/im/v1/chats"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            response = requests.get(url, headers=headers, timeout=10, params={"page_size": 1})
            response.raise_for_status()
            
            api_result = response.json()
            if api_result.get("code") == 0:
                result["details"]["api_status"] = "✅ API调用成功"
                result["success"] = True
                result["message"] = "飞书连接测试成功"
            else:
                result["details"]["api_status"] = f"❌ API调用失败: {api_result.get('msg')}"
                result["message"] = "API调用失败，请检查应用权限配置"
        
        except Exception as e:
            result["details"]["api_status"] = f"❌ API调用异常: {str(e)}"
            result["message"] = "网络连接失败或API异常"
        
        return result
    
    def query_report_rules(self, rule_name: str = None, include_deleted: int = 0, 
                          user_id_type: str = "open_id") -> Optional[Dict]:
        """查询汇报规则
        
        Args:
            rule_name: 规则名称，如"工作日报"、"工作周报"、"工作月报"
            include_deleted: 是否包括已删除，0-不包括，1-包括
            user_id_type: 用户ID类型，默认为open_id
            
        Returns:
            查询结果字典或None
        """
        token = self.get_tenant_access_token()
        if not token:
            return None
        
        url = f"{self.base_url}/report/v1/rules/query"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        params = {
            "include_deleted": include_deleted,
            "user_id_type": user_id_type
        }
        
        if rule_name:
            params["rule_name"] = rule_name
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                return result.get("data")
            else:
                logging.error(f"查询汇报规则失败: {result.get('msg')}")
                return None
        except Exception as e:
            logging.error(f"查询汇报规则异常: {e}")
            return None
    
    def check_report_submission_status(self, rule_name: str, 
                                     start_date: str = None, 
                                     end_date: str = None) -> Dict[str, Any]:
        """检查汇报提交状态
        
        Args:
            rule_name: 规则名称
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            
        Returns:
            包含提交状态信息的字典
        """
        result = {
            "success": False,
            "submitted": False,
            "deadline": None,
            "message": "",
            "rule_info": None
        }
        
        # 查询汇报规则
        rules_data = self.query_report_rules(rule_name)
        if not rules_data:
            result["message"] = f"未找到汇报规则: {rule_name}"
            return result
        
        result["success"] = True
        result["rule_info"] = rules_data
        
        # 这里可以根据实际API扩展检查具体的提交状态
        # 由于飞书API文档中没有直接的提交状态查询接口，
        # 我们可以通过其他方式来判断，比如查询消息记录等
        
        return result
    
    def get_report_deadlines(self, report_type: str = "daily") -> Dict[str, Any]:
        """获取汇报截止时间
        
        Args:
            report_type: 汇报类型，daily/weekly/monthly
            
        Returns:
            包含截止时间信息的字典
        """
        now = datetime.now()
        result = {
            "report_type": report_type,
            "current_time": now,
            "deadline": None,
            "submit_time": None,
            "should_submit": False
        }
        
        if report_type == "daily":
            # 日报：当天截止时间前2小时提交
            deadline = now.replace(hour=18, minute=0, second=0, microsecond=0)
            submit_time = deadline - timedelta(hours=2)  # 16:00提交
            result["deadline"] = deadline
            result["submit_time"] = submit_time
            result["should_submit"] = now >= submit_time and now <= deadline
            
        elif report_type == "weekly":
            # 周报：周五晚上8点提交
            days_until_friday = (4 - now.weekday()) % 7
            if days_until_friday == 0 and now.weekday() == 4:  # 今天是周五
                deadline = now.replace(hour=23, minute=59, second=59, microsecond=0)
                submit_time = now.replace(hour=20, minute=0, second=0, microsecond=0)
            else:
                friday = now + timedelta(days=days_until_friday)
                deadline = friday.replace(hour=23, minute=59, second=59, microsecond=0)
                submit_time = friday.replace(hour=20, minute=0, second=0, microsecond=0)
            
            result["deadline"] = deadline
            result["submit_time"] = submit_time
            result["should_submit"] = (now.weekday() == 4 and 
                                     now >= submit_time and 
                                     now <= deadline)
            
        elif report_type == "monthly":
            # 月报：月末最后一天晚上8点提交
            next_month = now.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)
            deadline = last_day.replace(hour=23, minute=59, second=59, microsecond=0)
            submit_time = last_day.replace(hour=20, minute=0, second=0, microsecond=0)
            
            result["deadline"] = deadline
            result["submit_time"] = submit_time
            result["should_submit"] = (now.date() == last_day.date() and 
                                     now >= submit_time and 
                                     now <= deadline)
        
        return result
    
    def auto_submit_report(self, chat_id: str, report_content: str, 
                          report_type: str = "日报") -> Dict[str, Any]:
        """自动提交汇报
        
        Args:
            chat_id: 群聊ID
            report_content: 汇报内容
            report_type: 汇报类型
            message_format: 消息格式
            
        Returns:
            提交结果字典
        """
        result = {
            "success": False,
            "message": "",
            "submitted_at": None
        }
        
        # 检查是否应该提交
        type_mapping = {"日报": "daily", "周报": "weekly", "月报": "monthly"}
        deadline_info = self.get_report_deadlines(type_mapping.get(report_type, "daily"))
        
        if not deadline_info["should_submit"]:
            result["message"] = f"当前时间不在{report_type}提交时间范围内"
            return result
        
        # 发送汇报
        if self.send_report(chat_id, report_content, "card", report_type):
            result["success"] = True
            result["message"] = f"{report_type}自动提交成功"
            result["submitted_at"] = datetime.now()
        else:
            result["message"] = f"{report_type}自动提交失败"
        
        return result
    
    def check_and_auto_submit(self, chat_id: str, report_generator_func, 
                             config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查并自动提交所有类型的汇报
        
        Args:
            chat_id: 群聊ID
            report_generator_func: 报告生成函数
            config: 配置信息
            
        Returns:
            提交结果列表
        """
        results = []
        
        # 检查日报
        daily_deadline = self.get_report_deadlines("daily")
        if daily_deadline["should_submit"]:
            try:
                daily_content = report_generator_func("daily")
                if daily_content:
                    submit_result = self.auto_submit_report(
                        chat_id, daily_content, "日报"
                    )
                    submit_result["type"] = "日报"
                    results.append(submit_result)
            except Exception as e:
                results.append({
                    "type": "日报",
                    "success": False,
                    "message": f"日报生成失败: {str(e)}"
                })
        
        # 检查周报
        weekly_deadline = self.get_report_deadlines("weekly")
        if weekly_deadline["should_submit"]:
            try:
                weekly_content = report_generator_func("weekly")
                if weekly_content:
                    submit_result = self.auto_submit_report(
                        chat_id, weekly_content, "周报"
                    )
                    submit_result["type"] = "周报"
                    results.append(submit_result)
            except Exception as e:
                results.append({
                    "type": "周报",
                    "success": False,
                    "message": f"周报生成失败: {str(e)}"
                })
        
        # 检查月报
        monthly_deadline = self.get_report_deadlines("monthly")
        if monthly_deadline["should_submit"]:
            try:
                monthly_content = report_generator_func("monthly")
                if monthly_content:
                    submit_result = self.auto_submit_report(
                        chat_id, monthly_content, "月报"
                    )
                    submit_result["type"] = "月报"
                    results.append(submit_result)
            except Exception as e:
                results.append({
                    "type": "月报",
                    "success": False,
                    "message": f"月报生成失败: {str(e)}"
                })
        
        return results


def test_feishu_connection(app_id: str, app_secret: str) -> Dict[str, Any]:
    """测试飞书连接的便捷函数"""
    if not app_id or not app_secret:
        return {
            "success": False,
            "message": "请先配置飞书App ID和App Secret",
            "details": {}
        }
    
    client = FeishuClient(app_id, app_secret)
    return client.test_connection()


def submit_to_feishu(app_id: str, app_secret: str, chat_id: str, 
                    report_content: str, message_format: str = "card", 
                    report_type: str = "日报") -> Dict[str, Any]:
    """提交报告到飞书的便捷函数"""
    result = {
        "success": False,
        "message": ""
    }
    
    if not all([app_id, app_secret, chat_id, report_content]):
        result["message"] = "缺少必要的配置参数"
        return result
    
    try:
        client = FeishuClient(app_id, app_secret)
        
        # 测试连接
        test_result = client.test_connection()
        if not test_result["success"]:
            result["message"] = f"连接测试失败: {test_result['message']}"
            return result
        
        # 发送报告
        if client.send_report(chat_id, report_content, message_format, report_type):
            result["success"] = True
            result["message"] = "报告提交成功"
        else:
            result["message"] = "报告发送失败，请检查群聊ID是否正确"
    
    except Exception as e:
        result["message"] = f"提交异常: {str(e)}"
    
    return result