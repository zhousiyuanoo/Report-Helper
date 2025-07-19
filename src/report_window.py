#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告窗口模块
提供报告生成、查看、编辑和管理功能
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QDateEdit, QListWidget, QListWidgetItem, QTabWidget,
    QSplitter, QGroupBox, QCheckBox, QSpinBox, QProgressBar,
    QMessageBox, QInputDialog, QMenu, QAction, QFrame,
    QScrollArea, QFileDialog
)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QTextCharFormat, QSyntaxHighlighter
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config_manager import ConfigManager
from report_generator import ReportGenerator
from ai_generator import AIReportGenerator


class ReportGenerationThread(QThread):
    """报告生成线程"""
    
    progress_updated = pyqtSignal(int)  # 进度更新
    status_updated = pyqtSignal(str)   # 状态更新
    generation_completed = pyqtSignal(str, str)  # 生成完成 (report_type, content)
    generation_failed = pyqtSignal(str)  # 生成失败
    
    def __init__(self, report_generator: ReportGenerator, report_type: str, 
                 start_date: str = None, end_date: str = None, use_ai: bool = True):
        super().__init__()
        self.report_generator = report_generator
        self.report_type = report_type
        self.start_date = start_date
        self.end_date = end_date
        self.use_ai = use_ai
    
    def run(self):
        """运行报告生成"""
        try:
            self.status_updated.emit("正在准备生成报告...")
            self.progress_updated.emit(10)
            
            if self.report_type == "daily":
                self.status_updated.emit("正在生成日报...")
                self.progress_updated.emit(30)
                content = self.report_generator.generate_daily_report(use_ai=self.use_ai)
            
            elif self.report_type == "weekly":
                self.status_updated.emit("正在生成周报...")
                self.progress_updated.emit(30)
                content = self.report_generator.generate_weekly_report(use_ai=self.use_ai)
            
            elif self.report_type == "monthly":
                self.status_updated.emit("正在生成月报...")
                self.progress_updated.emit(30)
                content = self.report_generator.generate_monthly_report(use_ai=self.use_ai)
            
            elif self.report_type == "custom":
                self.status_updated.emit("正在生成自定义报告...")
                self.progress_updated.emit(30)
                content = self.report_generator.generate_custom_report(
                    self.start_date, self.end_date, use_ai=self.use_ai
                )
            
            else:
                raise ValueError(f"不支持的报告类型: {self.report_type}")
            
            self.progress_updated.emit(80)
            self.status_updated.emit("正在保存报告...")
            
            if content:
                # 保存报告
                self.report_generator.save_report(content, self.report_type)
                self.progress_updated.emit(100)
                self.status_updated.emit("报告生成完成！")
                self.generation_completed.emit(self.report_type, content)
            else:
                self.generation_failed.emit("报告内容为空")
        
        except Exception as e:
            self.generation_failed.emit(str(e))


class MarkdownHighlighter(QSyntaxHighlighter):
    """Markdown语法高亮"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self):
        """设置高亮规则"""
        self.highlighting_rules = []
        
        # 标题格式
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#1976d2"))
        header_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'^#{1,6}\s.*$', header_format))
        
        # 粗体
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'\*\*.*?\*\*', bold_format))
        
        # 斜体
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((r'\*.*?\*', italic_format))
        
        # 代码
        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#d32f2f"))
        code_format.setBackground(QColor("#f5f5f5"))
        self.highlighting_rules.append((r'`.*?`', code_format))
        
        # 链接
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#1976d2"))
        link_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        self.highlighting_rules.append((r'\[.*?\]\(.*?\)', link_format))
    
    def highlightBlock(self, text):
        """高亮文本块"""
        import re
        
        for pattern, format in self.highlighting_rules:
            for match in re.finditer(pattern, text, re.MULTILINE):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


class ReportPreviewWidget(QFrame):
    """报告预览组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        self.title_label = QLabel("血泪预览")
        self.title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: #1976d2; padding: 10px 0;")
        layout.addWidget(self.title_label)
        
        # 报告信息
        info_layout = QHBoxLayout()
        
        self.type_label = QLabel("类型: -")
        self.type_label.setFont(QFont("Arial", 9))
        info_layout.addWidget(self.type_label)
        
        self.date_label = QLabel("日期: -")
        self.date_label.setFont(QFont("Arial", 9))
        info_layout.addWidget(self.date_label)
        
        self.word_count_label = QLabel("字数: 0")
        self.word_count_label.setFont(QFont("Arial", 9))
        info_layout.addWidget(self.word_count_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # 内容预览
        self.content_edit = QTextEdit()
        self.content_edit.setReadOnly(True)
        self.content_edit.setFont(QFont("Microsoft YaHei", 10))
        
        # 添加Markdown高亮
        self.highlighter = MarkdownHighlighter(self.content_edit.document())
        
        layout.addWidget(self.content_edit)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("✏️ 修改血泪")
        self.edit_btn.clicked.connect(self.enable_editing)
        button_layout.addWidget(self.edit_btn)
        
        self.save_btn = QPushButton("💾 存档")
        self.save_btn.clicked.connect(self.save_content)
        self.save_btn.setVisible(False)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("❌ 算了")
        self.cancel_btn.clicked.connect(self.cancel_editing)
        self.cancel_btn.setVisible(False)
        button_layout.addWidget(self.cancel_btn)
        
        self.copy_btn = QPushButton("📋 复制血泪")
        self.copy_btn.clicked.connect(self.copy_content)
        button_layout.addWidget(self.copy_btn)
        
        self.export_btn = QPushButton("📤 导出血泪史")
        self.export_btn.clicked.connect(self.export_content)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.original_content = ""
    
    def setup_style(self):
        """设置样式"""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(
            "QFrame {"
            "    background-color: #fafafa;"
            "    border: 1px solid #e0e0e0;"
            "    border-radius: 8px;"
            "}"
            "QTextEdit {"
            "    background-color: white;"
            "    border: 1px solid #ddd;"
            "    border-radius: 4px;"
            "    padding: 10px;"
            "}"
            "QPushButton {"
            "    background-color: #2196f3;"
            "    color: white;"
            "    border: none;"
            "    padding: 8px 15px;"
            "    border-radius: 4px;"
            "    font-size: 12px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #1976d2;"
            "}"
        )
    
    def set_report(self, report_type: str, content: str, date_range: str = ""):
        """设置报告内容"""
        self.report_type = report_type
        self.original_content = content
        
        # 更新信息
        type_names = {
            "daily": "今日血泪",
            "weekly": "本周受苦", 
            "monthly": "本月折磨",
            "custom": "自定义痛苦"
        }
        self.type_label.setText(f"类型: {type_names.get(report_type, report_type)}")
        self.date_label.setText(f"日期: {date_range or datetime.now().strftime('%Y-%m-%d')}")
        self.word_count_label.setText(f"字数: {len(content)}")
        
        # 设置内容
        self.content_edit.setPlainText(content)
        self.content_edit.setReadOnly(True)
        
        # 重置按钮状态
        self.edit_btn.setVisible(True)
        self.save_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
    
    def enable_editing(self):
        """启用编辑模式"""
        self.content_edit.setReadOnly(False)
        self.content_edit.setFocus()
        
        self.edit_btn.setVisible(False)
        self.save_btn.setVisible(True)
        self.cancel_btn.setVisible(True)
    
    def save_content(self):
        """保存内容"""
        new_content = self.content_edit.toPlainText()
        self.original_content = new_content
        
        # 更新字数
        self.word_count_label.setText(f"字数: {len(new_content)}")
        
        self.content_edit.setReadOnly(True)
        self.edit_btn.setVisible(True)
        self.save_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
        
        QMessageBox.information(self, "成功", "报告内容已保存！")
    
    def cancel_editing(self):
        """取消编辑"""
        self.content_edit.setPlainText(self.original_content)
        self.content_edit.setReadOnly(True)
        
        self.edit_btn.setVisible(True)
        self.save_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
    
    def copy_content(self):
        """复制内容"""
        from PyQt5.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.content_edit.toPlainText())
        QMessageBox.information(self, "成功", "报告内容已复制到剪贴板！")
    
    def export_content(self):
        """导出内容"""
        content = self.content_edit.toPlainText()
        if not content:
            QMessageBox.warning(self, "警告", "没有可导出的内容！")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出报告", 
            f"{self.report_type}_report_{datetime.now().strftime('%Y%m%d')}.md",
            "Markdown文件 (*.md);;文本文件 (*.txt);;所有文件 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "成功", f"报告已导出到：{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败：{str(e)}")
    
    def get_content(self) -> str:
        """获取当前内容"""
        return self.content_edit.toPlainText()


class ReportWindow(QWidget):
    """报告窗口"""
    
    def __init__(self, config_manager: ConfigManager, report_generator: ReportGenerator = None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.report_generator = report_generator if report_generator else ReportGenerator(config_manager)
        
        # AI生成器（可选）
        ai_config = config_manager.get_ai_config()
        if ai_config.get("enabled", False):
            self.ai_generator = AIReportGenerator(ai_config)
        else:
            self.ai_generator = None
        
        self.generation_thread = None
        
        self.setup_ui()
        self.setup_connections()
        self.load_report_history()
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("血泪总结与管理")
        self.setGeometry(100, 100, 1200, 800)
        
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧：生成控制区域
        self.create_control_area(splitter)
        
        # 右侧：预览和历史区域
        self.create_preview_area(splitter)
        
        # 设置分割器比例
        splitter.setSizes([400, 800])
    
    def create_control_area(self, parent):
        """创建控制区域"""
        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)
        
        # 标题
        title_label = QLabel("📊 血泪总结")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_label.setStyleSheet("color: #1976d2; padding: 10px 0;")
        layout.addWidget(title_label)
        
        # 报告类型选择
        type_group = QGroupBox("血泪类型")
        type_layout = QVBoxLayout(type_group)
        
        self.daily_radio = QCheckBox("📅 今日血泪")
        self.daily_radio.setChecked(True)
        type_layout.addWidget(self.daily_radio)
        
        self.weekly_radio = QCheckBox("📊 本周受苦")
        type_layout.addWidget(self.weekly_radio)
        
        self.monthly_radio = QCheckBox("📈 本月折磨")
        type_layout.addWidget(self.monthly_radio)
        
        self.custom_radio = QCheckBox("🎯 自定义痛苦")
        type_layout.addWidget(self.custom_radio)
        
        # 设置单选行为
        self.report_type_checkboxes = [
            self.daily_radio, self.weekly_radio, 
            self.monthly_radio, self.custom_radio
        ]
        
        for checkbox in self.report_type_checkboxes:
            checkbox.toggled.connect(self.on_report_type_changed)
        
        layout.addWidget(type_group)
        
        # 日期范围（自定义报告用）
        self.date_range_group = QGroupBox("日期范围")
        date_layout = QGridLayout(self.date_range_group)
        
        date_layout.addWidget(QLabel("开始日期:"), 0, 0)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        self.start_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.start_date_edit, 0, 1)
        
        date_layout.addWidget(QLabel("结束日期:"), 1, 0)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.end_date_edit, 1, 1)
        
        self.date_range_group.setVisible(False)
        layout.addWidget(self.date_range_group)
        
        # 生成选项
        options_group = QGroupBox("生成选项")
        options_layout = QVBoxLayout(options_group)
        
        self.use_ai_checkbox = QCheckBox("🤖 使用AI生成")
        self.use_ai_checkbox.setChecked(True)
        self.use_ai_checkbox.setEnabled(self.ai_generator is not None)
        if not self.ai_generator:
            self.use_ai_checkbox.setText("🤖 使用AI生成 (未配置)")
        options_layout.addWidget(self.use_ai_checkbox)
        
        self.include_stats_checkbox = QCheckBox("📊 包含统计信息")
        self.include_stats_checkbox.setChecked(True)
        options_layout.addWidget(self.include_stats_checkbox)
        
        self.include_charts_checkbox = QCheckBox("📈 包含图表")
        options_layout.addWidget(self.include_charts_checkbox)
        
        layout.addWidget(options_group)
        
        # 生成按钮
        self.generate_btn = QPushButton("🚀 生成血泪史")
        self.generate_btn.setStyleSheet(
            "QPushButton {"
            "    background-color: #4caf50;"
            "    color: white;"
            "    border: none;"
            "    padding: 15px 20px;"
            "    border-radius: 8px;"
            "    font-weight: bold;"
            "    font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #45a049;"
            "}"
            "QPushButton:disabled {"
            "    background-color: #cccccc;"
            "}"
        )
        layout.addWidget(self.generate_btn)
        
        # 进度显示
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # AI增强功能
        if self.ai_generator:
            ai_group = QGroupBox("🤖 AI增强功能")
            ai_layout = QVBoxLayout(ai_group)
            
            self.enhance_btn = QPushButton("✨ 润色血泪")
            self.enhance_btn.clicked.connect(self.enhance_report)
            ai_layout.addWidget(self.enhance_btn)
            
            self.expand_btn = QPushButton("📝 扩展痛苦")
            self.expand_btn.clicked.connect(self.expand_report)
            ai_layout.addWidget(self.expand_btn)
            
            self.summarize_btn = QPushButton("📋 精简血泪")
            self.summarize_btn.clicked.connect(self.summarize_report)
            ai_layout.addWidget(self.summarize_btn)
            
            layout.addWidget(ai_group)
        
        # 模板管理
        template_group = QGroupBox("📄 血泪模板")
        template_layout = QVBoxLayout(template_group)
        
        template_select_layout = QHBoxLayout()
        template_select_layout.addWidget(QLabel("血泪模板:"))
        
        self.template_combo = QComboBox()
        self.load_templates()
        template_select_layout.addWidget(self.template_combo)
        
        template_layout.addLayout(template_select_layout)
        
        template_btn_layout = QHBoxLayout()
        
        self.apply_template_btn = QPushButton("套用模板")
        self.apply_template_btn.clicked.connect(self.apply_template)
        template_btn_layout.addWidget(self.apply_template_btn)
        
        self.save_template_btn = QPushButton("保存模板")
        self.save_template_btn.clicked.connect(self.save_template)
        template_btn_layout.addWidget(self.save_template_btn)
        
        template_layout.addLayout(template_btn_layout)
        
        layout.addWidget(template_group)
        
        layout.addStretch()
        
        parent.addWidget(control_widget)
    
    def create_preview_area(self, parent):
        """创建预览区域"""
        preview_widget = QWidget()
        layout = QVBoxLayout(preview_widget)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 预览选项卡
        self.preview_tab = ReportPreviewWidget()
        self.tab_widget.addTab(self.preview_tab, "📄 报告预览")
        
        # 历史选项卡
        self.create_history_tab()
        
        layout.addWidget(self.tab_widget)
        
        parent.addWidget(preview_widget)
    
    def create_history_tab(self):
        """创建历史选项卡"""
        history_widget = QWidget()
        layout = QVBoxLayout(history_widget)
        
        # 标题和操作
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📚 血泪历史")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_label.setStyleSheet("color: #1976d2; padding: 10px 0;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.refresh_history_btn = QPushButton("🔄 刷新血泪史")
        self.refresh_history_btn.clicked.connect(self.load_report_history)
        header_layout.addWidget(self.refresh_history_btn)
        
        self.clear_history_btn = QPushButton("🗑️ 清空黑历史")
        self.clear_history_btn.clicked.connect(self.clear_report_history)
        header_layout.addWidget(self.clear_history_btn)
        
        layout.addLayout(header_layout)
        
        # 历史列表
        self.history_list = QListWidget()
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_history_context_menu)
        self.history_list.itemDoubleClicked.connect(self.load_history_report)
        layout.addWidget(self.history_list)
        
        self.tab_widget.addTab(history_widget, "📚 历史记录")
    
    def setup_connections(self):
        """设置信号连接"""
        self.generate_btn.clicked.connect(self.generate_report)
    
    def on_report_type_changed(self):
        """报告类型变化处理"""
        sender = self.sender()
        
        if sender.isChecked():
            # 取消其他选项
            for checkbox in self.report_type_checkboxes:
                if checkbox != sender:
                    checkbox.setChecked(False)
            
            # 显示/隐藏日期范围
            self.date_range_group.setVisible(sender == self.custom_radio)
    
    def get_selected_report_type(self) -> str:
        """获取选中的报告类型"""
        if self.daily_radio.isChecked():
            return "daily"
        elif self.weekly_radio.isChecked():
            return "weekly"
        elif self.monthly_radio.isChecked():
            return "monthly"
        elif self.custom_radio.isChecked():
            return "custom"
        else:
            return "daily"  # 默认
    
    def generate_report(self):
        """生成报告"""
        if self.generation_thread and self.generation_thread.isRunning():
            QMessageBox.warning(self, "警告", "血泪史正在生成中，请稍候...")
            return
        
        report_type = self.get_selected_report_type()
        use_ai = self.use_ai_checkbox.isChecked() and self.ai_generator is not None
        
        # 获取日期范围（自定义报告）
        start_date = None
        end_date = None
        if report_type == "custom":
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        # 创建生成线程
        self.generation_thread = ReportGenerationThread(
            self.report_generator, report_type, start_date, end_date, use_ai
        )
        
        # 连接信号
        self.generation_thread.progress_updated.connect(self.update_progress)
        self.generation_thread.status_updated.connect(self.update_status)
        self.generation_thread.generation_completed.connect(self.on_generation_completed)
        self.generation_thread.generation_failed.connect(self.on_generation_failed)
        
        # 更新UI状态
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        
        # 启动线程
        self.generation_thread.start()
    
    def update_progress(self, value: int):
        """更新进度"""
        self.progress_bar.setValue(value)
    
    def update_status(self, message: str):
        """更新状态"""
        self.status_label.setText(message)
    
    def on_generation_completed(self, report_type: str, content: str):
        """生成完成处理"""
        # 更新UI状态
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        
        # 显示报告
        date_range = ""
        if report_type == "custom":
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            date_range = f"{start_date} 至 {end_date}"
        
        self.preview_tab.set_report(report_type, content, date_range)
        self.tab_widget.setCurrentIndex(0)  # 切换到预览选项卡
        
        # 刷新历史
        self.load_report_history()
        
        QMessageBox.information(self, "成功", "血泪史生成完成！")
    
    def on_generation_failed(self, error_message: str):
        """生成失败处理"""
        # 更新UI状态
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        
        QMessageBox.critical(self, "生成失败", f"血泪史生成失败：{error_message}")
    
    def enhance_report(self):
        """润色报告"""
        if not self.ai_generator:
            QMessageBox.warning(self, "警告", "AI润色师未配置！")
            return
        
        current_content = self.preview_tab.get_content()
        if not current_content:
            QMessageBox.warning(self, "警告", "没有可润色的血泪内容！")
            return
        
        try:
            enhanced_content = self.ai_generator.enhance_report(current_content)
            if enhanced_content:
                self.preview_tab.set_report("enhanced", enhanced_content)
                QMessageBox.information(self, "成功", "血泪润色完成！")
            else:
                QMessageBox.warning(self, "失败", "血泪润色失败！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"润色过程中出现错误：{str(e)}")
    
    def expand_report(self):
        """扩展报告"""
        if not self.ai_generator:
            QMessageBox.warning(self, "警告", "AI润色师未配置！")
            return
        
        current_content = self.preview_tab.get_content()
        if not current_content:
            QMessageBox.warning(self, "警告", "没有可扩展的痛苦内容！")
            return
        
        try:
            expanded_content = self.ai_generator.expand_report(current_content)
            if expanded_content:
                self.preview_tab.set_report("expanded", expanded_content)
                QMessageBox.information(self, "成功", "痛苦扩展完成！")
            else:
                QMessageBox.warning(self, "失败", "痛苦扩展失败！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"扩展过程中出现错误：{str(e)}")
    
    def summarize_report(self):
        """精简报告"""
        if not self.ai_generator:
            QMessageBox.warning(self, "警告", "AI润色师未配置！")
            return
        
        current_content = self.preview_tab.get_content()
        if not current_content:
            QMessageBox.warning(self, "警告", "没有可精简的血泪内容！")
            return
        
        try:
            summarized_content = self.ai_generator.summarize_report(current_content)
            if summarized_content:
                self.preview_tab.set_report("summarized", summarized_content)
                QMessageBox.information(self, "成功", "血泪精简完成！")
            else:
                QMessageBox.warning(self, "失败", "血泪精简失败！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"精简过程中出现错误：{str(e)}")
    
    def load_templates(self):
        """加载模板"""
        templates = self.config_manager.get_report_templates()
        self.template_combo.clear()
        self.template_combo.addItem("选择血泪模板...")
        
        for template_name in templates.keys():
            self.template_combo.addItem(template_name)
    
    def apply_template(self):
        """应用模板"""
        template_name = self.template_combo.currentText()
        if template_name == "选择血泪模板...":
            return
        
        templates = self.config_manager.get_report_templates()
        template_content = templates.get(template_name, "")
        
        if template_content:
            self.preview_tab.set_report("template", template_content)
            QMessageBox.information(self, "成功", f"已套用血泪模板：{template_name}")
    
    def save_template(self):
        """保存模板"""
        current_content = self.preview_tab.get_content()
        if not current_content:
            QMessageBox.warning(self, "警告", "没有可保存的血泪内容！")
            return
        
        template_name, ok = QInputDialog.getText(
            self, "保存血泪模板", "请输入血泪模板名称:"
        )
        
        if ok and template_name.strip():
            templates = self.config_manager.get_report_templates()
            templates[template_name.strip()] = current_content
            
            if self.config_manager.save_report_templates(templates):
                self.load_templates()
                QMessageBox.information(self, "成功", f"血泪模板已保存：{template_name}")
            else:
                QMessageBox.critical(self, "错误", "血泪模板保存失败！")
    
    def load_report_history(self):
        """加载报告历史"""
        history = self.config_manager.get_report_history()
        self.history_list.clear()
        
        # 按时间倒序排列（优先使用generated_at，其次使用created_at）
        sorted_history = sorted(history, key=lambda x: x.get('generated_at', x.get('created_at', '')), reverse=True)
        
        for report in sorted_history:
            # 获取时间戳（优先使用generated_at，其次使用created_at）
            timestamp = report.get('generated_at', report.get('created_at', ''))
            if timestamp:
                # 如果是ISO格式的时间戳，转换为更友好的格式
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime('%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    pass
            else:
                timestamp = '未知时间'
                
            item_text = f"{report.get('type', '未知')} - {timestamp}"
            if report.get('title'):
                item_text = f"{report.get('title')} ({item_text})"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, report)
            self.history_list.addItem(item)
    
    def load_history_report(self, item: QListWidgetItem):
        """加载历史报告"""
        report_data = item.data(Qt.UserRole)
        if report_data:
            content = report_data.get('content', '')
            report_type = report_data.get('type', 'unknown')
            
            # 获取时间戳（优先使用generated_at，其次使用created_at）
            timestamp = report_data.get('generated_at', report_data.get('created_at', ''))
            if timestamp:
                # 如果是ISO格式的时间戳，转换为更友好的格式
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime('%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    pass
            
            self.preview_tab.set_report(report_type, content, timestamp)
            self.tab_widget.setCurrentIndex(0)  # 切换到预览选项卡
    
    def show_history_context_menu(self, position):
        """显示历史右键菜单"""
        item = self.history_list.itemAt(position)
        if item is None:
            return
        
        menu = QMenu(self)
        
        load_action = QAction("加载血泪史", self)
        load_action.triggered.connect(lambda: self.load_history_report(item))
        menu.addAction(load_action)
        
        delete_action = QAction("删除黑历史", self)
        delete_action.triggered.connect(lambda: self.delete_history_report(item))
        menu.addAction(delete_action)
        
        menu.exec_(self.history_list.mapToGlobal(position))
    
    def delete_history_report(self, item: QListWidgetItem):
        """删除历史报告"""
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这个血泪史吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            report_data = item.data(Qt.UserRole)
            if self.config_manager.delete_report_history(report_data):
                self.load_report_history()
                QMessageBox.information(self, "成功", "血泪史已删除！")
            else:
                QMessageBox.critical(self, "错误", "删除失败！")
    
    def clear_report_history(self):
        """清空报告历史"""
        reply = QMessageBox.question(
            self, "确认清空", "确定要清空所有血泪黑历史吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.config_manager.clear_report_history():
                self.load_report_history()
                QMessageBox.information(self, "成功", "血泪黑历史已清空！")
            else:
                QMessageBox.critical(self, "错误", "清空失败！")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止生成线程
        if self.generation_thread and self.generation_thread.isRunning():
            self.generation_thread.terminate()
            self.generation_thread.wait()
        
        event.accept()