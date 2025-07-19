#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作日志窗口模块
提供工作日志的添加、编辑、查看和管理功能
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QDateEdit, QTimeEdit, QListWidget, QListWidgetItem,
    QSplitter, QGroupBox, QCheckBox, QSpinBox,
    QMessageBox, QInputDialog, QMenu, QAction,
    QHeaderView, QAbstractItemView, QFrame, QSystemTrayIcon,
    QApplication
)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config_manager import ConfigManager


class WorkLogItem(QFrame):
    """工作日志项组件"""
    
    # 信号定义
    edit_requested = pyqtSignal(dict)  # 编辑请求
    delete_requested = pyqtSignal(dict)  # 删除请求
    
    def __init__(self, log_data: Dict, parent=None):
        super().__init__(parent)
        self.log_data = log_data
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)
        
        # 头部信息（时间、类型、优先级）
        header_layout = QHBoxLayout()
        
        # 时间标签
        time_label = QLabel(f"{self.log_data.get('time', '')}")
        time_label.setFont(QFont("Arial", 9, QFont.Bold))
        time_label.setStyleSheet("color: #666;")
        header_layout.addWidget(time_label)
        
        # 类型标签
        type_label = QLabel(f"[{self.log_data.get('type', '工作')}]")
        type_label.setFont(QFont("Arial", 8))
        type_label.setStyleSheet(self.get_type_style(self.log_data.get('type', '工作')))
        header_layout.addWidget(type_label)
        
        # 优先级标签
        priority = self.log_data.get('priority', '中')
        priority_label = QLabel(f"优先级: {priority}")
        priority_label.setFont(QFont("Arial", 8))
        priority_label.setStyleSheet(self.get_priority_style(priority))
        header_layout.addWidget(priority_label)
        
        # 状态标签
        status = self.log_data.get('status', '进行中')
        status_label = QLabel(f"状态: {status}")
        status_label.setFont(QFont("Arial", 8))
        status_label.setStyleSheet(self.get_status_style(status))
        header_layout.addWidget(status_label)
        
        header_layout.addStretch()
        
        # 操作按钮
        edit_btn = QPushButton("编辑")
        edit_btn.setFixedSize(50, 25)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.log_data))
        header_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("删除")
        delete_btn.setFixedSize(50, 25)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.log_data))
        header_layout.addWidget(delete_btn)
        
        layout.addLayout(header_layout)
        
        # 内容
        content_label = QLabel(self.log_data.get('content', ''))
        content_label.setWordWrap(True)
        content_label.setFont(QFont("Microsoft YaHei", 9))
        content_label.setStyleSheet("color: #333; padding: 5px 0;")
        layout.addWidget(content_label)
        
        # 标签
        tags = self.log_data.get('tags', [])
        if tags:
            tags_layout = QHBoxLayout()
            tags_label = QLabel("标签:")
            tags_label.setFont(QFont("Arial", 8))
            tags_label.setStyleSheet("color: #888;")
            tags_layout.addWidget(tags_label)
            
            for tag in tags:
                tag_label = QLabel(f"#{tag}")
                tag_label.setFont(QFont("Arial", 8))
                tag_label.setStyleSheet(
                    "background-color: #e3f2fd; color: #1976d2; "
                    "padding: 2px 6px; border-radius: 10px; margin-right: 5px;"
                )
                tags_layout.addWidget(tag_label)
            
            tags_layout.addStretch()
            layout.addLayout(tags_layout)
    
    def setup_style(self):
        """设置样式"""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(
            "QFrame {"
            "    background-color: #fafafa;"
            "    border: 1px solid #e0e0e0;"
            "    border-radius: 8px;"
            "    margin: 2px;"
            "}"
            "QFrame:hover {"
            "    background-color: #f5f5f5;"
            "    border-color: #bdbdbd;"
            "}"
            "QPushButton {"
            "    background-color: #2196f3;"
            "    color: white;"
            "    border: none;"
            "    border-radius: 4px;"
            "    font-size: 12px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #1976d2;"
            "}"
        )
    
    def get_type_style(self, type_name: str) -> str:
        """获取类型样式"""
        type_colors = {
            "工作": "background-color: #e8f5e8; color: #2e7d32;",
            "学习": "background-color: #e3f2fd; color: #1976d2;",
            "会议": "background-color: #fff3e0; color: #f57c00;",
            "其他": "background-color: #f3e5f5; color: #7b1fa2;"
        }
        base_style = "padding: 2px 6px; border-radius: 10px; font-weight: bold;"
        return base_style + type_colors.get(type_name, type_colors["其他"])
    
    def get_priority_style(self, priority: str) -> str:
        """获取优先级样式"""
        priority_colors = {
            "高": "color: #d32f2f; font-weight: bold;",
            "中": "color: #f57c00; font-weight: bold;",
            "低": "color: #388e3c; font-weight: bold;"
        }
        return priority_colors.get(priority, priority_colors["中"])
    
    def get_status_style(self, status: str) -> str:
        """获取状态样式"""
        status_colors = {
            "未开始": "color: #757575;",
            "进行中": "color: #1976d2; font-weight: bold;",
            "已完成": "color: #388e3c; font-weight: bold;",
            "已暂停": "color: #f57c00;",
            "已取消": "color: #d32f2f;"
        }
        return status_colors.get(status, status_colors["进行中"])


class WorkLogWindow(QWidget):
    """工作日志窗口"""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.current_logs = []
        self.filtered_logs = []
        
        self.setup_ui()
        self.setup_connections()
        self.load_logs()
        
        # 自动保存定时器
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # 30秒自动保存
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("牛马流水账管理")
        self.setGeometry(100, 100, 1000, 700)
        
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧：日志输入区域
        self.create_input_area(splitter)
        
        # 右侧：日志列表区域
        self.create_list_area(splitter)
        
        # 设置分割器比例
        splitter.setSizes([400, 600])
    
    def create_input_area(self, parent):
        """创建输入区域"""
        input_widget = QWidget()
        layout = QVBoxLayout(input_widget)
        
        # 标题
        title_label = QLabel("🐴 牛马流水账")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_label.setStyleSheet("color: #1976d2; padding: 10px 0;")
        layout.addWidget(title_label)
        
        # 输入表单
        form_group = QGroupBox("牛马记事簿")
        form_layout = QGridLayout(form_group)
        
        # 日期
        form_layout.addWidget(QLabel("日期:"), 0, 0)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addWidget(self.date_edit, 0, 1)
        
        # 时间
        form_layout.addWidget(QLabel("时间:"), 1, 0)
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        form_layout.addWidget(self.time_edit, 1, 1)
        
        # 类型
        form_layout.addWidget(QLabel("社畜分拣:"), 2, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["搬砖", "充电", "开会", "摸鱼"])
        form_layout.addWidget(self.type_combo, 2, 1)
        
        # 优先级
        form_layout.addWidget(QLabel("优先级:"), 3, 0)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["高", "中", "低"])
        self.priority_combo.setCurrentText("中")
        form_layout.addWidget(self.priority_combo, 3, 1)
        
        # 状态
        form_layout.addWidget(QLabel("状态:"), 4, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["未开始", "进行中", "已完成", "已暂停", "已取消"])
        self.status_combo.setCurrentText("进行中")
        form_layout.addWidget(self.status_combo, 4, 1)
        
        # 标签
        form_layout.addWidget(QLabel("标签:"), 5, 0)
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("用逗号分隔多个标签")
        form_layout.addWidget(self.tags_edit, 5, 1)
        
        layout.addWidget(form_group)
        
        # 内容输入
        content_group = QGroupBox("今日血泪史")
        content_layout = QVBoxLayout(content_group)
        
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("记录一下今天又被怎么折磨的...")
        self.content_edit.setMaximumHeight(150)
        content_layout.addWidget(self.content_edit)
        
        layout.addWidget(content_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 存档血泪")
        self.save_btn.setStyleSheet(
            "QPushButton {"
            "    background-color: #4caf50;"
            "    color: white;"
            "    border: none;"
            "    padding: 10px 20px;"
            "    border-radius: 5px;"
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #45a049;"
            "}"
        )
        button_layout.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton("🗑️ 重新做牛")
        self.clear_btn.setStyleSheet(
            "QPushButton {"
            "    background-color: #f44336;"
            "    color: white;"
            "    border: none;"
            "    padding: 10px 20px;"
            "    border-radius: 5px;"
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #da190b;"
            "}"
        )
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # 快捷操作
        quick_group = QGroupBox("摸鱼神器")
        quick_layout = QVBoxLayout(quick_group)
        
        # 快捷模板
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("偷懒模板:"))
        
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "选择模板...",
            "开始搬砖",
            "完成任务",
            "参加会议",
            "学习充电",
            "解决问题",
            "代码搬砖",
            "文档编写",
            "测试调试"
        ])
        template_layout.addWidget(self.template_combo)
        
        apply_template_btn = QPushButton("一键偷懒")
        apply_template_btn.clicked.connect(self.apply_template)
        template_layout.addWidget(apply_template_btn)
        
        quick_layout.addLayout(template_layout)
        
        # 时间跟踪
        time_track_layout = QHBoxLayout()
        
        self.start_time_btn = QPushButton("⏰ 开始受苦")
        self.start_time_btn.clicked.connect(self.start_time_tracking)
        time_track_layout.addWidget(self.start_time_btn)
        
        self.stop_time_btn = QPushButton("⏹️ 停止受苦")
        self.stop_time_btn.clicked.connect(self.stop_time_tracking)
        self.stop_time_btn.setEnabled(False)
        time_track_layout.addWidget(self.stop_time_btn)
        
        self.time_display = QLabel("00:00:00")
        self.time_display.setFont(QFont("Arial", 10, QFont.Bold))
        self.time_display.setStyleSheet("color: #1976d2; padding: 5px;")
        time_track_layout.addWidget(self.time_display)
        
        quick_layout.addLayout(time_track_layout)
        
        layout.addWidget(quick_group)
        
        layout.addStretch()
        
        parent.addWidget(input_widget)
        
        # 时间跟踪定时器
        self.tracking_timer = QTimer()
        self.tracking_timer.timeout.connect(self.update_time_display)
        self.tracking_start_time = None
        self.tracking_elapsed = 0
    
    def create_list_area(self, parent):
        """创建列表区域"""
        list_widget = QWidget()
        layout = QVBoxLayout(list_widget)
        
        # 标题和统计
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📋 牛马血泪史")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_label.setStyleSheet("color: #1976d2; padding: 10px 0;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.stats_label = QLabel("总计: 0 条")
        self.stats_label.setFont(QFont("Arial", 10))
        self.stats_label.setStyleSheet("color: #666; padding: 10px 0;")
        header_layout.addWidget(self.stats_label)
        
        layout.addLayout(header_layout)
        
        # 过滤和搜索
        filter_group = QGroupBox("血泪查找器")
        filter_layout = QGridLayout(filter_group)
        
        # 日期范围
        filter_layout.addWidget(QLabel("受苦时间:"), 0, 0)
        
        date_range_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        self.start_date_edit.setCalendarPopup(True)
        date_range_layout.addWidget(self.start_date_edit)
        
        date_range_layout.addWidget(QLabel("至"))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        date_range_layout.addWidget(self.end_date_edit)
        
        filter_layout.addLayout(date_range_layout, 0, 1)
        
        # 类型过滤
        filter_layout.addWidget(QLabel("社畜分类:"), 1, 0)
        self.filter_type_combo = QComboBox()
        self.filter_type_combo.addItems(["全部血泪", "搬砖", "充电", "开会", "摸鱼"])
        filter_layout.addWidget(self.filter_type_combo, 1, 1)
        
        # 状态过滤
        filter_layout.addWidget(QLabel("痛苦状态:"), 2, 0)
        self.filter_status_combo = QComboBox()
        self.filter_status_combo.addItems(["全部状态", "未开始", "进行中", "已完成", "已暂停", "已取消"])
        filter_layout.addWidget(self.filter_status_combo, 2, 1)
        
        # 搜索
        filter_layout.addWidget(QLabel("血泪搜索:"), 3, 0)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索血泪史内容...")
        filter_layout.addWidget(self.search_edit, 3, 1)
        
        # 过滤按钮
        filter_btn_layout = QHBoxLayout()
        
        self.apply_filter_btn = QPushButton("🔍 筛选血泪")
        self.apply_filter_btn.clicked.connect(self.apply_filters)
        filter_btn_layout.addWidget(self.apply_filter_btn)
        
        self.reset_filter_btn = QPushButton("🔄 重新受苦")
        self.reset_filter_btn.clicked.connect(self.reset_filters)
        filter_btn_layout.addWidget(self.reset_filter_btn)
        
        filter_layout.addLayout(filter_btn_layout, 4, 0, 1, 2)
        
        layout.addWidget(filter_group)
        
        # 日志列表
        self.log_list_widget = QListWidget()
        self.log_list_widget.setAlternatingRowColors(True)
        self.log_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.log_list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.log_list_widget)
        
        # 批量操作
        batch_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("全选血泪")
        self.select_all_btn.clicked.connect(self.select_all_logs)
        batch_layout.addWidget(self.select_all_btn)
        
        self.delete_selected_btn = QPushButton("删除黑历史")
        self.delete_selected_btn.clicked.connect(self.delete_selected_logs)
        batch_layout.addWidget(self.delete_selected_btn)
        
        self.export_btn = QPushButton("📤 导出血泪史")
        self.export_btn.clicked.connect(self.export_logs)
        batch_layout.addWidget(self.export_btn)
        
        batch_layout.addStretch()
        
        layout.addLayout(batch_layout)
        
        parent.addWidget(list_widget)
    
    def setup_connections(self):
        """设置信号连接"""
        self.save_btn.clicked.connect(self.save_log)
        self.clear_btn.clicked.connect(self.clear_form)
        
        # 实时搜索
        self.search_edit.textChanged.connect(self.apply_filters)
        
        # 过滤器变化
        self.filter_type_combo.currentTextChanged.connect(self.apply_filters)
        self.filter_status_combo.currentTextChanged.connect(self.apply_filters)
        self.start_date_edit.dateChanged.connect(self.apply_filters)
        self.end_date_edit.dateChanged.connect(self.apply_filters)
    
    def save_log(self):
        """保存日志"""
        content = self.content_edit.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "警告", "请输入工作内容！")
            return
        
        # 处理标签
        tags_text = self.tags_edit.text().strip()
        tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()] if tags_text else []
        
        log_data = {
            "content": content,
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "time": self.time_edit.time().toString("HH:mm"),
            "type": self.type_combo.currentText(),
            "priority": self.priority_combo.currentText(),
            "status": self.status_combo.currentText(),
            "tags": tags
        }
        
        # 添加时间跟踪信息
        if hasattr(self, 'tracking_elapsed') and self.tracking_elapsed > 0:
            log_data["duration"] = self.tracking_elapsed
        
        if self.config_manager.add_work_log(log_data):
            QMessageBox.information(self, "成功", "工作日志保存成功！")
            self.clear_form()
            self.load_logs()
        else:
            QMessageBox.critical(self, "错误", "工作日志保存失败！")
    
    def add_quick_log(self, content, log_type="搬砖"):
        """快速添加日志
        
        Args:
            content: 日志内容
            log_type: 日志类型，默认为'搬砖'
        """
        if not content.strip():
            return
        
        # 创建日志数据
        now = datetime.now()
        log_data = {
            "content": content,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "type": log_type,
            "priority": "中",
            "status": "进行中",
            "tags": []
        }
        
        # 保存日志
        if self.config_manager.add_work_log(log_data):
            # 显示通知
            self.show_notification("快速日志已添加", f"已添加[{log_type}]类型的工作日志")
            # 刷新日志列表
            self.load_logs()
            # 如果窗口可见，则更新表单
            if self.isVisible():
                self.clear_form()
                # 将内容设置到编辑框中，方便用户进一步编辑
                self.content_edit.setText(content)
                self.type_combo.setCurrentText(log_type)
    
    def clear_form(self):
        """清空表单"""
        self.content_edit.clear()
        self.tags_edit.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())
        self.type_combo.setCurrentText("搬砖")
        self.priority_combo.setCurrentText("中")
        self.status_combo.setCurrentText("进行中")
        
        # 重置时间跟踪
        if self.tracking_timer.isActive():
            self.stop_time_tracking()
    
    def load_logs(self):
        """加载日志列表"""
        self.current_logs = self.config_manager.get_work_logs()
        self.apply_filters()
    
    def apply_filters(self):
        """应用过滤器"""
        filtered_logs = self.current_logs.copy()
        
        # 日期范围过滤
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        filtered_logs = [log for log in filtered_logs 
                        if start_date <= log.get('date', '') <= end_date]
        
        # 类型过滤
        filter_type = self.filter_type_combo.currentText()
        if filter_type != "全部":
            filtered_logs = [log for log in filtered_logs 
                           if log.get('type', '') == filter_type]
        
        # 状态过滤
        filter_status = self.filter_status_combo.currentText()
        if filter_status != "全部":
            filtered_logs = [log for log in filtered_logs 
                           if log.get('status', '') == filter_status]
        
        # 搜索过滤
        search_text = self.search_edit.text().strip().lower()
        if search_text:
            filtered_logs = [log for log in filtered_logs 
                           if search_text in log.get('content', '').lower() or
                              search_text in ' '.join(log.get('tags', [])).lower()]
        
        self.filtered_logs = filtered_logs
        self.update_log_list()
    
    def show_notification(self, title, message):
        """显示系统通知
        
        Args:
            title: 通知标题
            message: 通知内容
        """
        # 检查是否有系统托盘图标
        if hasattr(QApplication.instance(), "system_tray") and QApplication.instance().system_tray:
            QApplication.instance().system_tray.showMessage(title, message, QSystemTrayIcon.Information, 3000)
        else:
            # 如果没有系统托盘，则创建一个临时的通知图标
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.svg")
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
            else:
                icon = QApplication.style().standardIcon(QApplication.style().SP_MessageBoxInformation)
                
            tray_icon = QSystemTrayIcon(icon)
            tray_icon.show()
            tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 3000)
            # 3秒后自动销毁
            QTimer.singleShot(3000, tray_icon.hide)
    
    def update_log_list(self):
        """更新日志列表显示"""
        self.log_list_widget.clear()
        
        # 按日期和时间排序（最新的在前）
        sorted_logs = sorted(self.filtered_logs, 
                           key=lambda x: f"{x.get('date', '')} {x.get('time', '')}", 
                           reverse=True)
        
        for log_data in sorted_logs:
            # 创建日志项
            log_item = WorkLogItem(log_data)
            log_item.edit_requested.connect(self.edit_log)
            log_item.delete_requested.connect(self.delete_log)
            
            # 添加到列表
            list_item = QListWidgetItem()
            list_item.setSizeHint(log_item.sizeHint())
            self.log_list_widget.addItem(list_item)
            self.log_list_widget.setItemWidget(list_item, log_item)
        
        # 更新统计信息
        self.update_stats()
    
    def update_stats(self):
        """更新统计信息"""
        total_count = len(self.filtered_logs)
        
        # 按状态统计
        status_counts = {}
        for log in self.filtered_logs:
            status = log.get('status', '进行中')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        stats_text = f"总计: {total_count} 条"
        if status_counts:
            status_parts = [f"{status}: {count}" for status, count in status_counts.items()]
            stats_text += f" ({', '.join(status_parts)})"
        
        self.stats_label.setText(stats_text)
    
    def edit_log(self, log_data: Dict):
        """编辑日志"""
        # 填充表单
        self.content_edit.setPlainText(log_data.get('content', ''))
        self.tags_edit.setText(', '.join(log_data.get('tags', [])))
        
        # 解析日期和时间
        date_str = log_data.get('date', '')
        time_str = log_data.get('time', '')
        
        if date_str:
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            self.date_edit.setDate(date)
        
        if time_str:
            time = QTime.fromString(time_str, "HH:mm")
            self.time_edit.setTime(time)
        
        # 设置其他字段
        self.type_combo.setCurrentText(log_data.get('type', '工作'))
        self.priority_combo.setCurrentText(log_data.get('priority', '中'))
        self.status_combo.setCurrentText(log_data.get('status', '进行中'))
        
        # 删除原日志（编辑模式）
        self.config_manager.delete_work_log(log_data)
        self.load_logs()
    
    def delete_log(self, log_data: Dict):
        """删除日志"""
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除这条日志吗？\n\n{log_data.get('content', '')[:50]}...",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.config_manager.delete_work_log(log_data):
                QMessageBox.information(self, "成功", "日志删除成功！")
                self.load_logs()
            else:
                QMessageBox.critical(self, "错误", "日志删除失败！")
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.log_list_widget.itemAt(position)
        if item is None:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(lambda: self.edit_selected_log())
        menu.addAction(edit_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.delete_selected_log())
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        copy_action = QAction("复制内容", self)
        copy_action.triggered.connect(lambda: self.copy_selected_log())
        menu.addAction(copy_action)
        
        menu.exec_(self.log_list_widget.mapToGlobal(position))
    
    def apply_template(self):
        """应用模板"""
        template = self.template_combo.currentText()
        if template == "选择模板...":
            return
        
        templates = {
            "开始搬砖": "今日份的搬砖工作正式开始，准备接受各种折磨",
            "完成任务": "终于完成了这个要命的任务，可以喘口气了",
            "参加会议": "又被拉去开会了，听了一堆废话但还得装作很认真",
            "学习充电": "被迫学习新技能，不学就要被淘汰的焦虑感",
            "解决问题": "又踩坑了，花了半天时间才爬出来",
            "代码搬砖": "继续敲代码，手指都快敲断了",
            "文档编写": "写文档比写代码还痛苦，但是不写又不行",
            "测试调试": "bug满天飞，调试到怀疑人生"
        }
        
        content = templates.get(template, "")
        if content:
            self.content_edit.setPlainText(content)
    
    def start_time_tracking(self):
        """开始时间跟踪"""
        self.tracking_start_time = datetime.now()
        self.tracking_timer.start(1000)  # 每秒更新
        self.start_time_btn.setEnabled(False)
        self.stop_time_btn.setEnabled(True)
    
    def stop_time_tracking(self):
        """停止时间跟踪"""
        if self.tracking_timer.isActive():
            self.tracking_timer.stop()
            if self.tracking_start_time:
                elapsed = datetime.now() - self.tracking_start_time
                self.tracking_elapsed = int(elapsed.total_seconds())
        
        self.start_time_btn.setEnabled(True)
        self.stop_time_btn.setEnabled(False)
    
    def update_time_display(self):
        """更新时间显示"""
        if self.tracking_start_time:
            elapsed = datetime.now() - self.tracking_start_time
            total_seconds = int(elapsed.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.time_display.setText(time_str)
    
    def reset_filters(self):
        """重置过滤器"""
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        self.end_date_edit.setDate(QDate.currentDate())
        self.filter_type_combo.setCurrentText("全部血泪")
        self.filter_status_combo.setCurrentText("全部状态")
        self.search_edit.clear()
        self.apply_filters()
    
    def select_all_logs(self):
        """全选日志"""
        for i in range(self.log_list_widget.count()):
            item = self.log_list_widget.item(i)
            item.setSelected(True)
    
    def delete_selected_logs(self):
        """删除选中的日志"""
        selected_items = self.log_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "提示", "请先选择要删除的日志！")
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除选中的 {len(selected_items)} 条日志吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 获取要删除的日志数据
            logs_to_delete = []
            for item in selected_items:
                widget = self.log_list_widget.itemWidget(item)
                if isinstance(widget, WorkLogItem):
                    logs_to_delete.append(widget.log_data)
            
            # 批量删除
            success_count = 0
            for log_data in logs_to_delete:
                if self.config_manager.delete_work_log(log_data):
                    success_count += 1
            
            QMessageBox.information(
                self, "删除完成", 
                f"成功删除 {success_count} 条日志！"
            )
            self.load_logs()
    
    def export_logs(self):
        """导出日志"""
        if not self.filtered_logs:
            QMessageBox.information(self, "提示", "没有可导出的日志！")
            return
        
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出日志", 
            f"工作日志_{datetime.now().strftime('%Y%m%d')}.txt",
            "文本文件 (*.txt);;CSV文件 (*.csv)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.export_to_csv(file_path)
                else:
                    self.export_to_txt(file_path)
                
                QMessageBox.information(self, "成功", f"日志已导出到：{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败：{str(e)}")
    
    def export_to_txt(self, file_path: str):
        """导出为文本文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("工作日志导出\n")
            f.write(f"导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总计：{len(self.filtered_logs)} 条\n")
            f.write("=" * 50 + "\n\n")
            
            for log in sorted(self.filtered_logs, 
                            key=lambda x: f"{x.get('date', '')} {x.get('time', '')}"):
                f.write(f"日期：{log.get('date', '')}\n")
                f.write(f"时间：{log.get('time', '')}\n")
                f.write(f"类型：{log.get('type', '')}\n")
                f.write(f"优先级：{log.get('priority', '')}\n")
                f.write(f"状态：{log.get('status', '')}\n")
                f.write(f"标签：{', '.join(log.get('tags', []))}\n")
                f.write(f"内容：{log.get('content', '')}\n")
                f.write("-" * 30 + "\n\n")
    
    def export_to_csv(self, file_path: str):
        """导出为CSV文件"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow(['日期', '时间', '类型', '优先级', '状态', '标签', '内容'])
            
            # 写入数据行
            for log in sorted(self.filtered_logs, 
                            key=lambda x: f"{x.get('date', '')} {x.get('time', '')}"):
                writer.writerow([
                    log.get('date', ''),
                    log.get('time', ''),
                    log.get('type', ''),
                    log.get('priority', ''),
                    log.get('status', ''),
                    ', '.join(log.get('tags', [])),
                    log.get('content', '')
                ])
    
    def auto_save(self):
        """自动保存（定期调用）"""
        # 这里可以实现自动保存草稿等功能
        pass
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止时间跟踪
        if self.tracking_timer.isActive():
            self.stop_time_tracking()
        
        # 停止自动保存定时器
        if self.auto_save_timer.isActive():
            self.auto_save_timer.stop()
        
        event.accept()