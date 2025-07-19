#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统托盘模块
提供系统托盘图标和菜单功能
"""

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication, QMessageBox, QInputDialog
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor
from typing import Optional, Callable
from datetime import datetime
from config_manager import ConfigManager
from timer_manager import TimerManager


class SystemTray(QObject):
    """系统托盘管理器"""
    
    # 信号定义
    show_work_log = pyqtSignal()  # 显示工作日志窗口
    show_report_window = pyqtSignal()  # 显示报告窗口
    show_settings = pyqtSignal()  # 显示设置窗口
    exit_requested = pyqtSignal()  # 退出应用
    
    def __init__(self, config_manager: ConfigManager, timer_manager: TimerManager):
        super().__init__()
        self.config_manager = config_manager
        self.timer_manager = timer_manager
        
        # 窗口引用
        self.work_log_window = None
        self.report_window = None
        self.settings_window = None
        
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(self.create_icon())
        self.tray_icon.setToolTip("牛马日报助手")
        
        # 创建托盘菜单
        self.create_tray_menu()
        
        # 连接信号
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # 连接定时器信号
        if self.timer_manager:
            self.timer_manager.reminder_triggered.connect(self.show_reminder_message)
            self.timer_manager.auto_submit_triggered.connect(self.show_auto_submit_message)
        
        # 状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(60000)  # 每分钟更新一次状态
        
    def connect_windows(self, work_log_window, report_window, settings_window):
        """连接窗口"""
        self.work_log_window = work_log_window
        self.report_window = report_window
        self.settings_window = settings_window
        
        # 连接信号
        self.show_work_log.connect(lambda: self.work_log_window.show() if self.work_log_window else None)
        self.show_report_window.connect(lambda: self.report_window.show() if self.report_window else None)
        self.show_settings.connect(lambda: self.settings_window.show() if self.settings_window else None)
    
    def create_icon(self) -> QIcon:
        """创建托盘图标"""
        # 创建一个简单的图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # 透明背景
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆形背景
        painter.setBrush(QBrush(QColor(74, 144, 226)))  # 蓝色背景
        painter.drawEllipse(2, 2, 28, 28)
        
        # 绘制文档图标
        painter.setBrush(QBrush(QColor(255, 255, 255)))  # 白色
        painter.drawRect(8, 6, 16, 20)
        
        # 绘制文档线条
        painter.setPen(QColor(74, 144, 226))
        painter.drawLine(10, 10, 22, 10)
        painter.drawLine(10, 13, 20, 13)
        painter.drawLine(10, 16, 21, 16)
        painter.drawLine(10, 19, 19, 19)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def create_tray_menu(self):
        """创建托盘菜单"""
        menu = QMenu()
        
        # 工作日志
        work_log_action = QAction("🐴 牛马流水账", self)
        work_log_action.triggered.connect(self.show_work_log.emit)
        menu.addAction(work_log_action)
        
        # 报告生成
        report_action = QAction("📊 血泪总结", self)
        report_action.triggered.connect(self.show_report_window.emit)
        menu.addAction(report_action)
        
        menu.addSeparator()
        
        # 设置
        settings_action = QAction("⚙️ 调教设置", self)
        settings_action.triggered.connect(self.show_settings.emit)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # 状态信息
        status_action = QAction("📈 社畜状态", self)
        status_action.triggered.connect(self.show_status_info)
        menu.addAction(status_action)
        
        # 快捷操作菜单
        quick_menu = menu.addMenu("⚡ 摸鱼神器")
        
        # 快速生成今日报告
        quick_report_action = QAction("今日血泪总结", self)
        quick_report_action.triggered.connect(self.quick_generate_report)
        quick_menu.addAction(quick_report_action)
        
        # 手动触发自动提交
        manual_submit_action = QAction("一键甩锅", self)
        manual_submit_action.triggered.connect(self.manual_trigger_submit)
        quick_menu.addAction(manual_submit_action)
        
        menu.addSeparator()
        
        # 关于
        about_action = QAction("ℹ️ 关于牛马助手", self)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)
        
        # 退出
        quit_action = QAction("🚪 下班跑路", self)
        quit_action.triggered.connect(self.exit_requested.emit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
    
    def on_tray_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            # 双击显示工作日志窗口
            self.show_work_log.emit()
        elif reason == QSystemTrayIcon.Trigger:
            # 单击显示状态信息
            self.show_status_info()
    
    def show_reminder_message(self, message: str):
        """显示提醒消息"""
        if self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(
                "工作提醒",
                message,
                QSystemTrayIcon.Information,
                5000  # 5秒
            )
    
    def show_auto_submit_message(self, report_type: str, content: str):
        """显示自动提交消息"""
        if self.tray_icon.supportsMessages():
            message = f"📋 {report_type}已自动生成，请手动查看和提交"
            
            self.tray_icon.showMessage(
                "自动提交通知",
                message,
                QSystemTrayIcon.Information,
                8000  # 8秒
            )
    
    def show_status_info(self):
        """显示状态信息"""
        try:
            # 获取各种状态信息
            settings = self.config_manager.get_settings()
            auto_submit_status = self.timer_manager.get_auto_submit_status() if self.timer_manager else {}
            
            # 构建状态消息
            status_lines = [
                "🐴 社畜状态报告",
                "",
                f"📅 当前受苦时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"💼 工作日: {'是' if auto_submit_status.get('is_work_day', False) else '否'}",
                f"⏰ 工作时间: {'是' if auto_submit_status.get('is_work_time', False) else '否'}",
                "",
                f"🔔 提醒功能: {'启用' if settings.get('reminder_enabled', True) else '禁用'}",
                f"🚀 自动甩锅: {'启用' if auto_submit_status.get('enabled', True) else '禁用'}",
                f"📤 甩锅时间: {auto_submit_status.get('submit_time', '20:00')}",
                f"📊 甩锅次数: {auto_submit_status.get('submit_count', 0)}",
                "",
                f"🕒 下次甩锅: {auto_submit_status.get('next_submit_in', '未知')}"
            ]
            
            # 获取工作日志统计
            work_logs = self.config_manager.get_work_logs()
            today = datetime.now().strftime('%Y-%m-%d')
            today_logs = [log for log in work_logs if log.get('date') == today]
            
            status_lines.extend([
                "",
                f"📝 今日血泪: {len(today_logs)} 条",
                f"📚 血泪存档: {len(work_logs)} 条"
            ])
            
            status_message = "\n".join(status_lines)
            
            if self.tray_icon.supportsMessages():
                self.tray_icon.showMessage(
                    "社畜状态",
                    status_message,
                    QSystemTrayIcon.Information,
                    10000  # 10秒
                )
        
        except Exception as e:
            print(f"显示社畜状态失败: {e}")
    
    def quick_add_log(self):
        """快速添加日志"""
        text, ok = QInputDialog.getText(
            None,
            "快速添加日志",
            "请输入工作内容:",
        )
        
        if ok and text.strip():
            log_data = {
                "content": text.strip(),
                "date": datetime.now().strftime('%Y-%m-%d'),
                "time": datetime.now().strftime('%H:%M'),
                "type": "工作",
                "priority": "中",
                "status": "进行中",
                "tags": []
            }
            
            if self.config_manager.add_work_log(log_data):
                self.tray_icon.showMessage(
                    "记录成功",
                    f"已记录血泪史: {text[:30]}...",
                    QSystemTrayIcon.Information,
                    3000
                )
            else:
                self.tray_icon.showMessage(
                    "记录失败",
                    "血泪史记录失败，请重试",
                    QSystemTrayIcon.Warning,
                    3000
                )
    
    def quick_generate_report(self):
        """快速生成今日报告"""
        try:
            from report_generator import ReportGenerator
            
            report_gen = ReportGenerator(self.config_manager)
            report_content = report_gen.generate_daily_report()
            
            if report_content:
                # 保存报告
                report_gen.save_report(report_content, "daily")
                
                self.tray_icon.showMessage(
                    "血泪总结完成",
                    "今日血泪总结已生成，请在报告窗口查看",
                    QSystemTrayIcon.Information,
                    5000
                )
                
                # 显示报告窗口
                self.show_report_window.emit()
            else:
                self.tray_icon.showMessage(
                    "总结失败",
                    "血泪总结生成失败，请检查日志内容",
                    QSystemTrayIcon.Warning,
                    3000
                )
        
        except Exception as e:
            print(f"快速生成报告失败: {e}")
            self.tray_icon.showMessage(
                "总结异常",
                f"血泪总结异常: {str(e)}",
                QSystemTrayIcon.Critical,
                3000
            )
    
    def manual_trigger_submit(self):
        """手动触发自动提交"""
        if self.timer_manager:
            if self.timer_manager.manual_trigger_auto_submit():
                self.tray_icon.showMessage(
                    "甩锅成功",
                    "已手动触发一键甩锅流程，老板再也不会发现了",
                    QSystemTrayIcon.Information,
                    3000
                )
            else:
                self.tray_icon.showMessage(
                    "甩锅失败",
                    "手动甩锅失败，社畜命苦啊",
                    QSystemTrayIcon.Warning,
                    3000
                )
    
    def show_about(self):
        """显示关于信息"""
        about_text = (
            "🤖 牛马血泪助手 v1.0\n\n"
            "一个专为社畜打造的血泪史管理神器\n\n"
            "主要功能:\n"
            "• 📝 血泪日志记录\n"
            "• 🤖 AI智能甩锅生成\n"
            "• ⏰ 定时摸鱼提醒\n"
            "• 🚀 飞书一键甩锅\n"
            "• 🎯 后台偷偷运行\n\n"
            "让社畜生活变得轻松一点！"
        )
        
        if self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(
                "关于牛马血泪助手",
                about_text,
                QSystemTrayIcon.Information,
                8000
            )
    
    def update_status(self):
        """更新状态（定期调用）"""
        # 更新托盘图标提示文本
        try:
            current_time = datetime.now().strftime('%H:%M')
            settings = self.config_manager.get_settings()
            
            tooltip_lines = [
                "牛马血泪助手",
                f"当前受苦时间: {current_time}"
            ]
            
            # 添加提醒状态
            if settings.get("reminder_enabled", True):
                tooltip_lines.append("🔔 摸鱼提醒已启用")
            
            # 添加自动提交状态
            if self.timer_manager:
                auto_status = self.timer_manager.get_auto_submit_status()
                if auto_status.get("enabled", True):
                    tooltip_lines.append(f"🚀 自动甩锅: {auto_status.get('submit_time', '20:00')}")
            
            self.tray_icon.setToolTip("\n".join(tooltip_lines))
        
        except Exception as e:
            print(f"更新状态失败: {e}")
    
    def show(self):
        """显示托盘图标"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()
            return True
        else:
            print("系统不支持托盘图标")
            return False
    
    def hide(self):
        """隐藏托盘图标"""
        self.tray_icon.hide()
    
    def is_visible(self) -> bool:
        """检查托盘图标是否可见"""
        return self.tray_icon.isVisible()