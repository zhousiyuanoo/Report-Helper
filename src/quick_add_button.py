#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速添加日志按钮模块
提供一个悬浮在所有窗口顶层的按钮，用于快速添加工作日志
"""

from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QDialog, QTextEdit, QLabel, QComboBox, QApplication)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QCursor
import os
from datetime import datetime


class QuickAddButton(QWidget):
    """快速添加日志按钮"""
    
    # 定义信号
    add_work_log_signal = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置无边框窗口
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool
        )
        
        # 设置背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 初始化UI
        self.init_ui()
        
        # 拖动相关变量
        self.dragging = False
        self.drag_position = QPoint()
        self.click_start_pos = QPoint()
        
        # 加载上次位置
        self.load_position()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建按钮
        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(50, 50)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        # 设置图标（如果有）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(project_root, "resources", "icon1.svg")
        if os.path.exists(icon_path):
            self.add_button.setIcon(QIcon(icon_path))
            self.add_button.setText("")
            self.add_button.setIconSize(self.add_button.size() * 1.2)
        else:
            # 如果没有图标，显示可爱的emoji
            self.add_button.setText("🐎")
            self.add_button.setStyleSheet(self.add_button.styleSheet() + """
                font-size: 24px;
            """)
        
        # 连接按钮的点击事件
        self.add_button.clicked.connect(self.show_add_dialog)
        
        layout.addWidget(self.add_button)
        
        # 设置窗口大小
        self.setFixedSize(50, 50)
    
    def show_add_dialog(self):
        """显示添加日志对话框"""
        dialog = QuickAddDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 获取日志内容和类型
            content = dialog.content_edit.toPlainText()
            log_type = dialog.type_combo.currentText()
            
            # 发送信号
            if content.strip():
                self.add_work_log_signal.emit(content, log_type)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.click_start_pos = event.globalPos()
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.dragging = False  # 重置拖动状态
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.LeftButton:
            # 检查是否开始拖动（移动距离超过阈值）
            if not self.dragging:
                move_distance = (event.globalPos() - self.click_start_pos).manhattanLength()
                if move_distance > 5:  # 拖动阈值
                    self.dragging = True
            
            if self.dragging:
                # 计算新位置
                new_pos = event.globalPos() - self.drag_position
                
                # 获取屏幕尺寸
                screen_rect = QApplication.desktop().availableGeometry(self)
                
                # 确保不超出屏幕边界
                new_x = max(0, min(new_pos.x(), screen_rect.width() - self.width()))
                new_y = max(0, min(new_pos.y(), screen_rect.height() - self.height()))
                
                self.move(new_x, new_y)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            was_dragging = self.dragging
            self.dragging = False  # 重置拖动状态
            
            if was_dragging:
                # 保存位置
                self.save_position()
            else:
                # 如果没有拖动，则是点击事件，显示对话框
                self.show_add_dialog()
            event.accept()
    
    def save_position(self):
        """保存按钮位置"""
        # 尝试从应用程序获取ConfigManager
        config_manager = QApplication.instance().property("config_manager")
        if config_manager:
            pos = self.pos()
            settings = config_manager.get_settings()
            settings["quick_add_button_x"] = pos.x()
            settings["quick_add_button_y"] = pos.y()
            config_manager.update_settings(settings)
    
    def load_position(self):
        """加载按钮位置"""
        # 尝试从应用程序获取ConfigManager
        config_manager = QApplication.instance().property("config_manager")
        if config_manager:
            settings = config_manager.get_settings()
            x = settings.get("quick_add_button_x", None)
            y = settings.get("quick_add_button_y", None)
            
            if x is not None and y is not None:
                x = int(x)
                y = int(y)
                self.move(x, y)
            else:
                # 默认位置：屏幕右下角
                screen_rect = QApplication.desktop().availableGeometry(self)
                self.move(screen_rect.width() - self.width() - 20, 
                          screen_rect.height() - self.height() - 20)
        else:
            # 默认位置：屏幕右下角
            screen_rect = QApplication.desktop().availableGeometry(self)
            self.move(screen_rect.width() - self.width() - 20, 
                      screen_rect.height() - self.height() - 20)


class QuickAddDialog(QDialog):
    """快速添加日志对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("牛马快速记录")
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.resize(400, 300)  # 增加高度以容纳新按钮
        
        # 获取配置管理器和AI生成器
        self.config_manager = QApplication.instance().property("config_manager")
        self.ai_generator = None
        if self.config_manager:
            ai_config = self.config_manager.get_ai_config()
            if ai_config.get("enabled", False):
                from ai_generator import AIReportGenerator
                try:
                    # 传递完整的配置字典而不是单独的参数
                    self.ai_generator = AIReportGenerator(ai_config)
                except Exception as e:
                    print(f"初始化AI生成器失败: {e}")
        
        # 初始化UI
        self.init_ui()
        
        # 移动到鼠标位置附近，确保不超出屏幕边界
        cursor_pos = QCursor.pos()
        screen_rect = QApplication.desktop().availableGeometry(self)
        
        # 计算对话框位置，确保完全在屏幕内
        x = cursor_pos.x() - self.width() // 2
        y = cursor_pos.y() - self.height() // 2
        
        # 确保对话框不超出屏幕左边界和右边界
        x = max(0, min(x, screen_rect.width() - self.width()))
        # 确保对话框不超出屏幕上边界和下边界
        y = max(0, min(y, screen_rect.height() - self.height()))
        
        self.move(x, y)
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 顶部布局：类型选择和模板选择
        top_layout = QHBoxLayout()
        
        # 日志类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("社畜分拣:"))
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["搬砖", "充电", "开会", "摸鱼"])
        type_layout.addWidget(self.type_combo)
        
        top_layout.addLayout(type_layout)
        
        # 模板选择
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("偷懒模板:"))
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("选择偷懒模板...")
        self.template_combo.addItems(["开始搬砖", "完成任务", "参加会议", "被迫学习", 
                                    "解决问题", "码代码", "写文档", "调试Bug"])
        template_layout.addWidget(self.template_combo)
        
        apply_template_btn = QPushButton("一键偷懒")
        apply_template_btn.clicked.connect(self.apply_template)
        template_layout.addWidget(apply_template_btn)
        
        top_layout.addLayout(template_layout)
        layout.addLayout(top_layout)
        
        # 日志内容输入
        layout.addWidget(QLabel("血泪内容:"))
        
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("今天又被压榨了什么...")
        layout.addWidget(self.content_edit)
        
        # 功能按钮布局
        function_layout = QHBoxLayout()
        
        # 生成今日工作日志按钮
        self.generate_daily_btn = QPushButton("生成今日血泪史")
        self.generate_daily_btn.clicked.connect(self.generate_daily_report)
        function_layout.addWidget(self.generate_daily_btn)
        
        # AI优化按钮
        self.optimize_btn = QPushButton("预览血泪")
        self.optimize_btn.clicked.connect(self.optimize_content)
        self.optimize_btn.setEnabled(self.ai_generator is not None)
        function_layout.addWidget(self.optimize_btn)
        
        layout.addLayout(function_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("存档血泪")
        self.save_button.clicked.connect(self.save_log)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("算了")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("记录血泪")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
    def apply_template(self):
        """应用模板"""
        template = self.template_combo.currentText()
        if template == "选择偷懒模板...":
            return
        
        templates = {
            "开始搬砖": "今天又开始搬砖了，准备被压榨的任务：\n1. \n2. \n3. ",
            "完成任务": "终于完成了一个任务：\n- 任务名称：\n- 完成时间：\n- 踩过的坑：\n- 血泪教训：",
            "参加会议": "又被拉去开会：\n- 会议主题：\n- 受害人员：\n- 会议要点：\n- 后续被安排的活：",
            "被迫学习": "被迫充电学习：\n- 学习内容：\n- 熬夜时长：\n- 痛苦收获：\n- 能否活用：",
            "解决问题": "又踩坑了：\n- 问题描述：\n- 折腾过程：\n- 最终解决方案：\n- 是否真的解决了：",
            "码代码": "码农日常：\n- 功能模块：\n- 进度情况：\n- 技术难点：\n- Bug情况：",
            "写文档": "被迫写文档：\n- 文档类型：\n- 编写进度：\n- 主要内容：\n- 有人看吗：",
            "调试Bug": "Debug血泪史：\n- 测试范围：\n- 发现的Bug：\n- 修复情况：\n- 还有多少坑："
        }
        
        content = templates.get(template, "")
        if content:
            self.content_edit.setPlainText(content)
    
    def generate_daily_report(self):
        """生成今日工作日志"""
        try:
            from report_generator import ReportGenerator
            
            if self.config_manager:
                report_gen = ReportGenerator(self.config_manager)
                # 获取今日日期
                today = datetime.now().strftime('%Y-%m-%d')
                # 使用AI生成（如果可用）
                use_ai = self.ai_generator is not None
                report_content = report_gen.generate_daily_report(today, use_ai)
                
                if report_content:
                    # 显示在内容编辑框中
                    self.content_edit.setPlainText(f"今日工作总结：\n\n{report_content}")
                else:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "警告", "生成今日工作日志失败，可能没有足够的日志记录！")
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "警告", "配置管理器未初始化！")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"生成今日工作日志时出错：{str(e)}")
    
    def optimize_content(self):
        """AI优化日志内容"""
        if not self.ai_generator:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "警告", "AI功能未配置！")
            return
        
        current_content = self.content_edit.toPlainText()
        if not current_content:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "警告", "没有可优化的内容！")
            return
        
        try:
            # 使用enhance_report方法的polish选项来优化内容
            optimized_content = self.ai_generator.enhance_report(current_content, "polish")
            if optimized_content:
                self.content_edit.setPlainText(optimized_content)
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "成功", "内容优化完成！")
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "失败", "内容优化失败！")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"优化过程中出现错误：{str(e)}")
    
    def save_log(self):
        """保存工作日志"""
        try:
            content = self.content_edit.toPlainText().strip()
            if not content:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "警告", "请输入日志内容！")
                return
            
            if not self.config_manager:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "警告", "配置管理器未初始化！")
                return
            
            # 创建日志数据
            now = datetime.now()
            log_data = {
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "type": self.type_combo.currentText(),
                "content": content,
                "timestamp": now.isoformat()
            }
            
            # 保存日志
            self.config_manager.add_work_log(log_data)
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "成功", "工作日志保存成功！")
            
            # 清空输入框
            self.content_edit.clear()
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"保存日志时出错：{str(e)}")


if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    button = QuickAddButton()
    button.show()
    
    sys.exit(app.exec_())