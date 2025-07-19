#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成模块
整合工作日志并生成各类报告
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from config_manager import ConfigManager
from ai_generator import AIReportGenerator


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.ai_generator = None
        self._init_ai_generator()
    
    def _init_ai_generator(self):
        """初始化AI生成器"""
        ai_config = self.config_manager.get_ai_config()
        if ai_config.get("enabled") and ai_config.get("api_key"):
            try:
                self.ai_generator = AIReportGenerator(ai_config)
            except Exception as e:
                print(f"AI生成器初始化失败: {e}")
                self.ai_generator = None
    
    def get_logs_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """根据日期范围获取工作日志"""
        all_logs = self.config_manager.get_work_logs()
        filtered_logs = []
        
        for log in all_logs:
            log_date = log.get('date', '')
            if start_date <= log_date <= end_date:
                filtered_logs.append(log)
        
        # 按日期排序
        filtered_logs.sort(key=lambda x: x.get('date', ''))
        return filtered_logs
    
    def get_logs_by_date(self, target_date: str) -> List[Dict]:
        """获取指定日期的工作日志"""
        return self.get_logs_by_date_range(target_date, target_date)
    
    def format_logs_for_template(self, logs: List[Dict]) -> Dict[str, str]:
        """格式化日志用于模板替换"""
        if not logs:
            return {
                "completed_tasks": "暂无记录",
                "ongoing_tasks": "暂无记录",
                "tomorrow_plan": "待规划",
                "achievements": "暂无记录",
                "completed_projects": "暂无记录",
                "next_week_plan": "待规划",
                "monthly_achievements": "暂无记录",
                "milestones": "暂无记录",
                "next_month_goals": "待规划"
            }
        
        # 按优先级和类型分类
        high_priority = [log for log in logs if log.get('priority') == '高']
        completed = [log for log in logs if log.get('status') == '已完成']
        in_progress = [log for log in logs if log.get('status') == '进行中']
        
        # 按类型分类
        work_logs = [log for log in logs if log.get('type') == '工作']
        meeting_logs = [log for log in logs if log.get('type') == '会议']
        learning_logs = [log for log in logs if log.get('type') == '学习']
        
        return {
            "completed_tasks": "\n".join([f"- {log.get('content', '')}" for log in completed]) or "暂无完成事项",
            "ongoing_tasks": "\n".join([f"- {log.get('content', '')}" for log in in_progress]) or "暂无进行中事项",
            "tomorrow_plan": "根据今日进展制定明日计划",
            "achievements": "\n".join([f"- {log.get('content', '')}" for log in high_priority]) or "暂无重要成果",
            "completed_projects": "\n".join([f"- {log.get('content', '')}" for log in completed if log.get('type') == '项目']) or "暂无完成项目",
            "next_week_plan": "基于本周进展制定下周计划",
            "monthly_achievements": "\n".join([f"- {log.get('content', '')}" for log in work_logs[:5]]) or "暂无月度成果",
            "milestones": "\n".join([f"- {log.get('content', '')}" for log in high_priority[:3]]) or "暂无重要里程碑",
            "next_month_goals": "基于本月总结制定下月目标"
        }
    
    def generate_daily_report(self, target_date: str = None, use_ai: bool = False) -> Optional[str]:
        """生成日报"""
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        logs = self.get_logs_by_date(target_date)
        
        if use_ai and self.ai_generator:
            # 使用AI生成
            ai_config = self.config_manager.get_ai_config()
            system_prompt = ai_config.get("system_prompt")
            return self.ai_generator.generate_daily_report(logs, system_prompt)
        else:
            # 使用模板生成
            templates = self.config_manager.get_templates()
            template = templates.get("daily", "今日工作总结：\n\n完成事项：\n{completed_tasks}\n\n进行中事项：\n{ongoing_tasks}\n\n明日计划：\n{tomorrow_plan}")
            
            format_data = self.format_logs_for_template(logs)
            return template.format(**format_data)
    
    def generate_weekly_report(self, target_date: str = None, use_ai: bool = False) -> Optional[str]:
        """生成周报"""
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        # 计算本周的开始和结束日期
        target_dt = datetime.strptime(target_date, '%Y-%m-%d')
        start_of_week = target_dt - timedelta(days=target_dt.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        start_date = start_of_week.strftime('%Y-%m-%d')
        end_date = end_of_week.strftime('%Y-%m-%d')
        
        logs = self.get_logs_by_date_range(start_date, end_date)
        
        if use_ai and self.ai_generator:
            # 使用AI生成
            ai_config = self.config_manager.get_ai_config()
            system_prompt = ai_config.get("system_prompt")
            return self.ai_generator.generate_weekly_report(logs, system_prompt)
        else:
            # 使用模板生成
            templates = self.config_manager.get_templates()
            template = templates.get("weekly", "本周工作总结：\n\n主要成果：\n{achievements}\n\n完成项目：\n{completed_projects}\n\n下周计划：\n{next_week_plan}")
            
            format_data = self.format_logs_for_template(logs)
            return template.format(**format_data)
    
    def generate_monthly_report(self, target_date: str = None, use_ai: bool = False) -> Optional[str]:
        """生成月报"""
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        # 计算本月的开始和结束日期
        target_dt = datetime.strptime(target_date, '%Y-%m-%d')
        start_of_month = target_dt.replace(day=1)
        
        # 计算下个月第一天，然后减一天得到本月最后一天
        if target_dt.month == 12:
            end_of_month = target_dt.replace(year=target_dt.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = target_dt.replace(month=target_dt.month + 1, day=1) - timedelta(days=1)
        
        start_date = start_of_month.strftime('%Y-%m-%d')
        end_date = end_of_month.strftime('%Y-%m-%d')
        
        logs = self.get_logs_by_date_range(start_date, end_date)
        
        if use_ai and self.ai_generator:
            # 使用AI生成
            ai_config = self.config_manager.get_ai_config()
            system_prompt = ai_config.get("system_prompt")
            return self.ai_generator.generate_monthly_report(logs, system_prompt)
        else:
            # 使用模板生成
            templates = self.config_manager.get_templates()
            template = templates.get("monthly", "本月工作总结：\n\n月度成果：\n{monthly_achievements}\n\n重要里程碑：\n{milestones}\n\n下月目标：\n{next_month_goals}")
            
            format_data = self.format_logs_for_template(logs)
            return template.format(**format_data)
    
    def generate_smart_report_for_auto_submit(self, report_type: str = "daily") -> Optional[str]:
        """为自动提交生成智能报告"""
        if not self.ai_generator:
            # 如果AI不可用，使用模板生成
            if report_type == "daily":
                return self.generate_daily_report(use_ai=False)
            elif report_type == "weekly":
                return self.generate_weekly_report(use_ai=False)
            else:
                return self.generate_monthly_report(use_ai=False)
        
        # 获取相应时间范围的日志
        today = datetime.now().strftime('%Y-%m-%d')
        
        if report_type == "daily":
            logs = self.get_logs_by_date(today)
        elif report_type == "weekly":
            target_dt = datetime.now()
            start_of_week = target_dt - timedelta(days=target_dt.weekday())
            end_date = today
            start_date = start_of_week.strftime('%Y-%m-%d')
            logs = self.get_logs_by_date_range(start_date, end_date)
        else:
            target_dt = datetime.now()
            start_of_month = target_dt.replace(day=1)
            start_date = start_of_month.strftime('%Y-%m-%d')
            logs = self.get_logs_by_date_range(start_date, today)
        
        return self.ai_generator.generate_smart_report(logs, report_type)
    
    def save_report(self, report_content: str, report_type: str, target_date: str = None) -> bool:
        """保存报告到历史记录"""
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        report_data = {
            "type": report_type,
            "date": target_date,
            "content": report_content,
            "generated_at": datetime.now().isoformat(),
            "method": "ai" if self.ai_generator else "template"
        }
        
        return self.config_manager.add_report_history(report_data)
    
    def get_report_history(self, report_type: str = None, limit: int = None) -> List[Dict]:
        """获取报告历史"""
        history = self.config_manager.get_report_history()
        
        if report_type:
            history = [report for report in history if report.get("type") == report_type]
        
        # 按生成时间倒序排列
        history.sort(key=lambda x: x.get("generated_at", ""), reverse=True)
        
        if limit:
            history = history[:limit]
        
        return history
    
    def delete_report_history(self, report_id: int) -> bool:
        """删除报告历史"""
        return self.config_manager.delete_report_history(report_id)
    
    def export_report_to_file(self, report_content: str, filename: str = None) -> bool:
        """导出报告到文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            return True
        except Exception as e:
            print(f"导出报告失败: {e}")
            return False
    
    def get_report_statistics(self) -> Dict[str, Any]:
        """获取报告统计信息"""
        history = self.config_manager.get_report_history()
        
        stats = {
            "total_reports": len(history),
            "daily_reports": len([r for r in history if r.get("type") == "daily"]),
            "weekly_reports": len([r for r in history if r.get("type") == "weekly"]),
            "monthly_reports": len([r for r in history if r.get("type") == "monthly"]),
            "ai_generated": len([r for r in history if r.get("method") == "ai"]),
            "template_generated": len([r for r in history if r.get("method") == "template"])
        }
        
        # 最近生成时间
        if history:
            latest_report = max(history, key=lambda x: x.get("generated_at", ""))
            stats["latest_report_date"] = latest_report.get("generated_at", "")
        else:
            stats["latest_report_date"] = ""
        
        return stats
    
    def refresh_ai_generator(self):
        """刷新AI生成器配置"""
        self._init_ai_generator()