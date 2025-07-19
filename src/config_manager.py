#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责处理应用程序的配置文件读写和数据管理
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "work_logs": [],
            "templates": {
                "daily": "今日工作总结：\n\n完成事项：\n{completed_tasks}\n\n进行中事项：\n{ongoing_tasks}\n\n明日计划：\n{tomorrow_plan}",
                "weekly": "本周工作总结：\n\n主要成果：\n{achievements}\n\n完成项目：\n{completed_projects}\n\n下周计划：\n{next_week_plan}",
                "monthly": "本月工作总结：\n\n月度成果：\n{monthly_achievements}\n\n重要里程碑：\n{milestones}\n\n下月目标：\n{next_month_goals}"
            },
            "settings": {
                "reminder_enabled": True,
                "reminder_interval": 60,  # 分钟
                "work_days": ["周一", "周二", "周三", "周四", "周五"],
                "work_start_time": "09:00",
                "work_end_time": "18:00",
                "auto_submit_time": "20:00",
                "startup_with_system": False,
                "minimize_to_tray": True,
                "show_notifications": True
            },
            "feishu_config": {
                "enabled": False,
                "app_id": "",
                "app_secret": "",
                "chat_id": "",
                "auto_report_enabled": False,
                "check_interval": 30,
                "daily_advance_hours": 2,
                "weekly_submit_time": "20:00",
                "monthly_submit_time": "20:00"
            },
            "ai_config": {
                "enabled": False,
                "provider": "DeepSeek",
                "api_key": "",
                "api_base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 1000,
                "timeout": 30,
                "retry_count": 3,
                "system_prompt": "你是一个专业的工作报告助手，请根据提供的工作日志生成简洁、专业的工作报告。"
            },
            "ai_providers_config": {
                "DeepSeek": {
                    "api_key": "",
                    "api_base_url": "https://api.deepseek.com/v1",
                    "model": "deepseek-chat"
                },
                "智谱AI": {
                    "api_key": "",
                    "api_base_url": "https://open.bigmodel.cn/api/paas/v4",
                    "model": "glm-4"
                },
                "百度文心": {
                    "api_key": "",
                    "api_base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat",
                    "model": "ernie-bot-turbo"
                },
                "阿里通义": {
                    "api_key": "",
                    "api_base_url": "https://dashscope.aliyuncs.com/api/v1",
                    "model": "qwen-turbo"
                },
                "Doubao": {
                    "api_key": "",
                    "api_base_url": "https://ark.cn-beijing.volces.com/api/v3",
                    "model": "doubao-lite-4k"
                }
            },
            "report_history": [],
            "submit_status": {
                "last_submit_date": "",
                "auto_submit_enabled": True,
                "submit_count": 0
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置，确保所有必要字段存在
                default_config = self.get_default_config()
                return self._merge_config(default_config, config)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"配置文件加载失败: {e}，使用默认配置")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """合并配置，确保所有默认字段存在"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"配置文件保存失败: {e}")
            return False
    
    def get_work_logs(self) -> List[Dict]:
        """获取工作日志"""
        return self.config.get("work_logs", [])
    
    def add_work_log(self, log_data: Dict) -> bool:
        """添加工作日志"""
        try:
            log_data["id"] = len(self.config["work_logs"]) + 1
            log_data["created_at"] = datetime.now().isoformat()
            self.config["work_logs"].append(log_data)
            return self.save_config()
        except Exception as e:
            print(f"添加工作日志失败: {e}")
            return False
    
    def update_work_log(self, log_id: int, log_data: Dict) -> bool:
        """更新工作日志"""
        try:
            for i, log in enumerate(self.config["work_logs"]):
                if log.get("id") == log_id:
                    log_data["id"] = log_id
                    log_data["updated_at"] = datetime.now().isoformat()
                    self.config["work_logs"][i] = log_data
                    return self.save_config()
            return False
        except Exception as e:
            print(f"更新工作日志失败: {e}")
            return False
    
    def delete_work_log(self, log_id: int) -> bool:
        """删除工作日志"""
        try:
            self.config["work_logs"] = [log for log in self.config["work_logs"] if log.get("id") != log_id]
            return self.save_config()
        except Exception as e:
            print(f"删除工作日志失败: {e}")
            return False
    
    def get_templates(self) -> Dict[str, str]:
        """获取报告模板"""
        return self.config.get("templates", {})
        
    def get_report_templates(self) -> Dict[str, str]:
        """获取报告模板（兼容方法）"""
        return self.get_templates()
    
    def update_template(self, template_type: str, content: str) -> bool:
        """更新报告模板"""
        try:
            self.config["templates"][template_type] = content
            return self.save_config()
        except Exception as e:
            print(f"更新模板失败: {e}")
            return False
            
    def save_report_templates(self, templates: Dict[str, str]) -> bool:
        """保存报告模板（兼容方法）"""
        try:
            self.config["templates"] = templates
            return self.save_config()
        except Exception as e:
            print(f"保存模板失败: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self.config
    
    def get_settings(self) -> Dict[str, Any]:
        """获取应用设置"""
        return self.config.get("settings", {})
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """更新应用设置"""
        try:
            self.config["settings"].update(settings)
            return self.save_config()
        except Exception as e:
            print(f"更新设置失败: {e}")
            return False
    
    def get_feishu_config(self) -> Dict[str, Any]:
        """获取飞书配置"""
        return self.config.get("feishu_config", {})
    
    def update_feishu_config(self, config: Dict[str, Any]) -> bool:
        """更新飞书配置"""
        try:
            self.config["feishu_config"].update(config)
            return self.save_config()
        except Exception as e:
            print(f"更新飞书配置失败: {e}")
            return False
    
    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI配置"""
        return self.config.get("ai_config", {})
    
    def update_ai_config(self, config: Dict[str, Any]) -> bool:
        """更新AI配置"""
        try:
            self.config["ai_config"].update(config)
            return self.save_config()
        except Exception as e:
            print(f"更新AI配置失败: {e}")
            return False
    
    def get_ai_providers_config(self) -> Dict[str, Any]:
        """获取所有AI提供商配置"""
        return self.config.get("ai_providers_config", {})
    
    def get_ai_provider_config(self, provider: str) -> Dict[str, Any]:
        """获取指定AI提供商配置"""
        providers_config = self.get_ai_providers_config()
        return providers_config.get(provider, {})
    
    def update_ai_provider_config(self, provider: str, config: Dict[str, Any]) -> bool:
        """更新指定AI提供商配置"""
        try:
            if "ai_providers_config" not in self.config:
                self.config["ai_providers_config"] = {}
            if provider not in self.config["ai_providers_config"]:
                self.config["ai_providers_config"][provider] = {}
            self.config["ai_providers_config"][provider].update(config)
            return self.save_config()
        except Exception as e:
            print(f"更新AI提供商配置失败: {e}")
            return False
    
    def get_report_history(self) -> List[Dict]:
        """获取报告历史"""
        return self.config.get("report_history", [])
    
    def add_report_history(self, report_data: Dict) -> bool:
        """添加报告历史"""
        try:
            report_data["id"] = len(self.config["report_history"]) + 1
            report_data["created_at"] = datetime.now().isoformat()
            self.config["report_history"].append(report_data)
            return self.save_config()
        except Exception as e:
            print(f"添加报告历史失败: {e}")
            return False
    
    def delete_report_history(self, report_id: int) -> bool:
        """删除报告历史"""
        try:
            self.config["report_history"] = [report for report in self.config["report_history"] if report.get("id") != report_id]
            return self.save_config()
        except Exception as e:
            print(f"删除报告历史失败: {e}")
            return False
    
    def clear_report_history(self) -> bool:
        """清空报告历史"""
        try:
            self.config["report_history"] = []
            return self.save_config()
        except Exception as e:
            print(f"清空报告历史失败: {e}")
            return False
    
    def get_submit_status(self) -> Dict[str, Any]:
        """获取提交状态"""
        return self.config.get("submit_status", {})
    
    def update_submit_status(self, status: Dict[str, Any]) -> bool:
        """更新提交状态"""
        try:
            self.config["submit_status"].update(status)
            return self.save_config()
        except Exception as e:
            print(f"更新提交状态失败: {e}")
            return False
    
    def backup_config(self, backup_path: str) -> bool:
        """备份配置文件"""
        try:
            import shutil
            shutil.copy2(self.config_file, backup_path)
            return True
        except Exception as e:
            print(f"备份配置失败: {e}")
            return False
    
    def restore_config(self, backup_path: str) -> bool:
        """恢复配置文件"""
        try:
            import shutil
            shutil.copy2(backup_path, self.config_file)
            self.config = self.load_config()
            return True
        except Exception as e:
            print(f"恢复配置失败: {e}")
            return False