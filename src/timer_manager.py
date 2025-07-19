#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时管理模块
负责定时提醒和自动提交功能
"""

from PyQt5.QtCore import QTimer, QObject, pyqtSignal, QTime, QDate
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, time
from config_manager import ConfigManager
from report_generator import ReportGenerator


class TimerManager(QObject):
    """定时管理器"""
    
    # 信号定义
    reminder_triggered = pyqtSignal(str)  # 提醒触发信号
    auto_submit_triggered = pyqtSignal(str, str)  # 自动提交触发信号 (report_type, content)
    
    def __init__(self, config_manager: ConfigManager, report_generator: ReportGenerator):
        super().__init__()
        self.config_manager = config_manager
        self.report_generator = report_generator
        
        # 定时器
        self.reminder_timer = QTimer()
        self.auto_submit_timer = QTimer()
        
        # 连接信号
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.auto_submit_timer.timeout.connect(self.check_auto_submit)
        
        # 初始化定时器
        self.setup_timers()
    
    def setup_timers(self):
        """设置定时器"""
        settings = self.config_manager.get_settings()
        
        # 初始化定时器，但不启动
        self.reminder_interval = 60000  # 60秒
        self.auto_submit_interval = 60000  # 60秒
    
    def start_all_timers(self):
        """启动所有定时器"""
        settings = self.config_manager.get_settings()
        
        if settings.get("reminder_enabled", True):
            # 提醒定时器，每分钟检查一次
            self.reminder_timer.start(self.reminder_interval)
        
        # 自动提交定时器，每分钟检查一次
        self.auto_submit_timer.start(self.auto_submit_interval)
    
    def stop_all_timers(self):
        """停止所有定时器"""
        if self.reminder_timer.isActive():
            self.reminder_timer.stop()
        
        if self.auto_submit_timer.isActive():
            self.auto_submit_timer.stop()
    
    def update_settings(self):
        """更新定时器设置"""
        # 停止当前定时器
        self.stop_all_timers()
        
        # 重新设置定时器
        self.setup_timers()
        
        # 重新启动定时器
        self.start_all_timers()
    
    def check_reminders(self):
        """检查是否需要提醒"""
        settings = self.config_manager.get_settings()
        
        if not settings.get("reminder_enabled", True):
            return
        
        current_time = datetime.now()
        current_time_str = current_time.strftime("%H:%M")
        current_weekday = current_time.strftime("%A")
        
        # 转换英文星期到中文
        weekday_map = {
            "Monday": "周一",
            "Tuesday": "周二", 
            "Wednesday": "周三",
            "Thursday": "周四",
            "Friday": "周五",
            "Saturday": "周六",
            "Sunday": "周日"
        }
        current_weekday_cn = weekday_map.get(current_weekday, current_weekday)
        
        # 检查是否在工作时间
        work_days = settings.get("work_days", ["周一", "周二", "周三", "周四", "周五"])
        work_start = settings.get("work_start_time", "09:00")
        work_end = settings.get("work_end_time", "18:00")
        
        if current_weekday_cn not in work_days:
            return
        
        if not (work_start <= current_time_str <= work_end):
            return
        
        # 检查自定义提醒
        custom_reminders = settings.get("custom_reminders", [])
        for reminder in custom_reminders:
            if (reminder.get("enabled", True) and 
                reminder.get("time") == current_time_str):
                message = reminder.get("message", "工作提醒")
                self.reminder_triggered.emit(message)
        
        # 检查间隔提醒
        interval = settings.get("reminder_interval", 60)  # 分钟
        if interval > 0:
            # 简单的间隔检查（可以优化为更精确的逻辑）
            if current_time.minute % interval == 0:
                self.reminder_triggered.emit("记录工作日志提醒")
    
    def check_auto_submit(self):
        """检查是否需要自动提交"""
        settings = self.config_manager.get_settings()
        submit_status = self.config_manager.get_submit_status()
        
        if not submit_status.get("auto_submit_enabled", True):
            return
        
        current_time = datetime.now()
        current_time_str = current_time.strftime("%H:%M")
        current_date = current_time.strftime("%Y-%m-%d")
        current_weekday = current_time.strftime("%A")
        
        # 转换英文星期到中文
        weekday_map = {
            "Monday": "周一",
            "Tuesday": "周二", 
            "Wednesday": "周三",
            "Thursday": "周四",
            "Friday": "周五",
            "Saturday": "周六",
            "Sunday": "周日"
        }
        current_weekday_cn = weekday_map.get(current_weekday, current_weekday)
        
        # 检查是否在工作日
        work_days = settings.get("work_days", ["周一", "周二", "周三", "周四", "周五"])
        if current_weekday_cn not in work_days:
            return
        
        # 检查是否到了自动提交时间
        auto_submit_time = settings.get("auto_submit_time", "20:00")
        if current_time_str != auto_submit_time:
            return
        
        # 检查今天是否已经提交过
        last_submit_date = submit_status.get("last_submit_date", "")
        if last_submit_date == current_date:
            return
        
        # 触发自动提交
        self.trigger_auto_submit()
    
    def trigger_auto_submit(self):
        """触发自动提交"""
        try:
            # 生成智能报告
            report_content = self.report_generator.generate_smart_report_for_auto_submit("daily")
            
            if report_content:
                # 保存报告
                self.report_generator.save_report(report_content, "daily")
                
                # 更新提交状态
                current_date = datetime.now().strftime("%Y-%m-%d")
                submit_status = self.config_manager.get_submit_status()
                submit_status["last_submit_date"] = current_date
                submit_status["submit_count"] = submit_status.get("submit_count", 0) + 1
                self.config_manager.update_submit_status(submit_status)
                
                # 发送信号
                self.auto_submit_triggered.emit("daily", report_content)
            else:
                print("自动生成报告失败")
        
        except Exception as e:
            print(f"自动提交异常: {e}")
    
    def is_work_day(self, date_str: str = None) -> bool:
        """判断是否为工作日"""
        if not date_str:
            target_date = datetime.now()
        else:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        weekday = target_date.strftime("%A")
        weekday_map = {
            "Monday": "周一",
            "Tuesday": "周二", 
            "Wednesday": "周三",
            "Thursday": "周四",
            "Friday": "周五",
            "Saturday": "周六",
            "Sunday": "周日"
        }
        weekday_cn = weekday_map.get(weekday, weekday)
        
        settings = self.config_manager.get_settings()
        work_days = settings.get("work_days", ["周一", "周二", "周三", "周四", "周五"])
        
        return weekday_cn in work_days
    
    def is_work_time(self) -> bool:
        """判断当前是否为工作时间"""
        settings = self.config_manager.get_settings()
        work_start = settings.get("work_start_time", "09:00")
        work_end = settings.get("work_end_time", "18:00")
        
        current_time = datetime.now().strftime("%H:%M")
        return work_start <= current_time <= work_end
    
    def update_reminder_settings(self, new_settings: Dict[str, Any]):
        """更新提醒设置"""
        current_settings = self.config_manager.get_settings()
        current_settings.update(new_settings)
        
        if self.config_manager.update_settings(current_settings):
            # 重新设置定时器
            self.setup_timers()
            return True
        return False
    
    def add_custom_reminder(self, time_str: str, message: str, enabled: bool = True) -> bool:
        """添加自定义提醒"""
        settings = self.config_manager.get_settings()
        custom_reminders = settings.get("custom_reminders", [])
        
        # 检查时间格式
        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            return False
        
        # 添加新提醒
        new_reminder = {
            "time": time_str,
            "message": message,
            "enabled": enabled
        }
        
        custom_reminders.append(new_reminder)
        settings["custom_reminders"] = custom_reminders
        
        return self.config_manager.update_settings(settings)
    
    def remove_custom_reminder(self, time_str: str) -> bool:
        """移除自定义提醒"""
        settings = self.config_manager.get_settings()
        custom_reminders = settings.get("custom_reminders", [])
        
        # 移除指定时间的提醒
        updated_reminders = [r for r in custom_reminders if r.get("time") != time_str]
        settings["custom_reminders"] = updated_reminders
        
        return self.config_manager.update_settings(settings)
    
    def get_next_reminder_time(self) -> Optional[str]:
        """获取下一个提醒时间"""
        settings = self.config_manager.get_settings()
        custom_reminders = settings.get("custom_reminders", [])
        
        if not custom_reminders:
            return None
        
        current_time = datetime.now().time()
        today_reminders = []
        
        for reminder in custom_reminders:
            if reminder.get("enabled", True):
                try:
                    reminder_time = datetime.strptime(reminder["time"], "%H:%M").time()
                    if reminder_time > current_time:
                        today_reminders.append(reminder_time)
                except ValueError:
                    continue
        
        if today_reminders:
            next_time = min(today_reminders)
            return next_time.strftime("%H:%M")
        
        return None
    
    def get_auto_submit_status(self) -> Dict[str, Any]:
        """获取自动提交状态"""
        submit_status = self.config_manager.get_submit_status()
        settings = self.config_manager.get_settings()
        
        status = {
            "enabled": submit_status.get("auto_submit_enabled", True),
            "submit_time": settings.get("auto_submit_time", "20:00"),
            "last_submit_date": submit_status.get("last_submit_date", ""),
            "submit_count": submit_status.get("submit_count", 0),
            "is_work_day": self.is_work_day(),
            "is_work_time": self.is_work_time()
        }
        
        # 计算距离下次自动提交的时间
        if status["enabled"] and status["is_work_day"]:
            try:
                submit_time = datetime.strptime(status["submit_time"], "%H:%M").time()
                current_time = datetime.now().time()
                
                if current_time < submit_time:
                    # 今天还没到提交时间
                    today = datetime.now().date()
                    submit_datetime = datetime.combine(today, submit_time)
                    time_diff = submit_datetime - datetime.now()
                    status["next_submit_in"] = str(time_diff).split('.')[0]  # 去掉微秒
                else:
                    # 今天已过提交时间，计算明天的
                    status["next_submit_in"] = "明日 " + status["submit_time"]
            except ValueError:
                status["next_submit_in"] = "时间格式错误"
        else:
            status["next_submit_in"] = "未启用或非工作日"
        
        return status
    
    def manual_trigger_auto_submit(self) -> bool:
        """手动触发自动提交"""
        try:
            self.trigger_auto_submit()
            return True
        except Exception as e:
            print(f"手动触发自动提交失败: {e}")
            return False
    
    def stop_all_timers(self):
        """停止所有定时器"""
        self.reminder_timer.stop()
        self.auto_submit_timer.stop()
    
    def restart_all_timers(self):
        """重启所有定时器"""
        self.stop_all_timers()
        self.setup_timers()
    
    def get_reminder_statistics(self) -> Dict[str, Any]:
        """获取提醒统计信息"""
        settings = self.config_manager.get_settings()
        submit_status = self.config_manager.get_submit_status()
        
        stats = {
            "reminder_enabled": settings.get("reminder_enabled", True),
            "reminder_interval": settings.get("reminder_interval", 60),
            "custom_reminders_count": len(settings.get("custom_reminders", [])),
            "auto_submit_enabled": submit_status.get("auto_submit_enabled", True),
            "total_auto_submits": submit_status.get("submit_count", 0),
            "last_submit_date": submit_status.get("last_submit_date", ""),
            "work_days_count": len(settings.get("work_days", [])),
            "is_current_work_day": self.is_work_day(),
            "is_current_work_time": self.is_work_time()
        }
        
        return stats