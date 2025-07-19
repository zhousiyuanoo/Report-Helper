#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置窗口模块
提供应用程序的设置界面
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QCheckBox, QSpinBox, QTabWidget, QGroupBox,
    QMessageBox, QFileDialog, QProgressBar, QSlider,
    QTimeEdit, QListWidget, QListWidgetItem, QFrame,
    QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QTime, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap
from datetime import datetime
from typing import Dict, Any
from config_manager import ConfigManager


class ConnectionTestThread(QThread):
    """连接测试线程"""
    
    test_completed = pyqtSignal(bool, str)  # 测试完成 (成功, 消息)
    
    def __init__(self, test_type: str, config: Dict[str, Any]):
        super().__init__()
        self.test_type = test_type
        self.config = config
    
    def run(self):
        """运行测试"""
        try:
            if self.test_type == "feishu":
                self.test_feishu_connection()
            elif self.test_type == "ai":
                self.test_ai_connection()
            else:
                self.test_completed.emit(False, "未知的测试类型")
        except Exception as e:
            self.test_completed.emit(False, f"测试异常: {str(e)}")
    
    def test_feishu_connection(self):
        """测试飞书连接"""
        try:
            from feishu_client import test_feishu_connection
            
            app_id = self.config.get("app_id", "")
            app_secret = self.config.get("app_secret", "")
            
            if not app_id or not app_secret:
                self.test_completed.emit(False, "请先配置App ID和App Secret")
                return
            
            result = test_feishu_connection(app_id, app_secret)
            self.test_completed.emit(result["success"], result["message"])
        
        except ImportError:
            self.test_completed.emit(False, "飞书客户端模块未找到")
        except Exception as e:
            self.test_completed.emit(False, f"连接测试失败: {str(e)}")
    
    def test_ai_connection(self):
        """测试AI连接"""
        try:
            from ai_generator import AIReportGenerator
            
            ai_generator = AIReportGenerator(self.config)
            result = ai_generator.test_connection()
            self.test_completed.emit(result["success"], result["message"])
        
        except ImportError:
            self.test_completed.emit(False, "AI生成器模块未找到")
        except Exception as e:
            self.test_completed.emit(False, f"连接测试失败: {str(e)}")


class SettingsWindow(QWidget):
    """设置窗口"""
    
    # 信号定义
    settings_changed = pyqtSignal()  # 设置已更改
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.test_thread = None
        
        self.setup_ui()
        self.load_settings()
        self.setup_connections()
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("调教设置")
        self.setGeometry(200, 200, 800, 600)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题
        title_label = QLabel("⚙️ 牛马助手调教设置")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setStyleSheet("color: #1976d2; padding: 10px 0;")
        main_layout.addWidget(title_label)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个设置选项卡
        self.create_basic_settings_tab()
        self.create_reminder_settings_tab()
        self.create_feishu_settings_tab()
        self.create_ai_settings_tab()
        self.create_advanced_settings_tab()
        
        # 底部按钮
        self.create_bottom_buttons(main_layout)
    
    def create_basic_settings_tab(self):
        """创建基本设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 应用设置组
        app_group = QGroupBox("牛马基础设置")
        app_layout = QGridLayout(app_group)
        
        # 启动设置
        app_layout.addWidget(QLabel("启动时偷偷躲起来:"), 0, 0)
        self.start_minimized_checkbox = QCheckBox()
        app_layout.addWidget(self.start_minimized_checkbox, 0, 1)
        
        app_layout.addWidget(QLabel("开机自动当牛马:"), 1, 0)
        self.auto_start_checkbox = QCheckBox()
        app_layout.addWidget(self.auto_start_checkbox, 1, 1)
        
        app_layout.addWidget(QLabel("关闭时继续潜伏:"), 2, 0)
        self.close_to_tray_checkbox = QCheckBox()
        app_layout.addWidget(self.close_to_tray_checkbox, 2, 1)
        
        app_layout.addWidget(QLabel("显示摸鱼快捷键:"), 3, 0)
        self.quick_add_button_checkbox = QCheckBox()
        app_layout.addWidget(self.quick_add_button_checkbox, 3, 1)
        
        # 界面设置
        app_layout.addWidget(QLabel("界面皮肤:"), 4, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["清爽白领", "深夜加班", "跟随老板心情"])
        app_layout.addWidget(self.theme_combo, 4, 1)
        
        app_layout.addWidget(QLabel("社畜语言:"), 5, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文社畜", "English Worker"])
        app_layout.addWidget(self.language_combo, 5, 1)
        
        layout.addWidget(app_group)
        
        # 数据设置组
        data_group = QGroupBox("血泪存档设置")
        data_layout = QGridLayout(data_group)
        
        data_layout.addWidget(QLabel("血泪存储路径:"), 0, 0)
        
        data_path_layout = QHBoxLayout()
        self.data_path_edit = QLineEdit()
        self.data_path_edit.setReadOnly(True)
        data_path_layout.addWidget(self.data_path_edit)
        
        self.browse_data_path_btn = QPushButton("选择藏身之处")
        self.browse_data_path_btn.clicked.connect(self.browse_data_path)
        data_path_layout.addWidget(self.browse_data_path_btn)
        
        data_layout.addLayout(data_path_layout, 0, 1)
        
        data_layout.addWidget(QLabel("自动备份间隔(天):"), 1, 0)
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(1, 30)
        self.backup_interval_spin.setValue(7)
        data_layout.addWidget(self.backup_interval_spin, 1, 1)
        
        data_layout.addWidget(QLabel("保留血泪备份数量:"), 2, 0)
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setRange(1, 50)
        self.backup_count_spin.setValue(10)
        data_layout.addWidget(self.backup_count_spin, 2, 1)
        
        layout.addWidget(data_group)
        
        # 日志设置组
        log_group = QGroupBox("日志设置")
        log_layout = QGridLayout(log_group)
        
        log_layout.addWidget(QLabel("日志级别:"), 0, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        log_layout.addWidget(self.log_level_combo, 0, 1)
        
        log_layout.addWidget(QLabel("日志文件大小限制(MB):"), 1, 0)
        self.log_size_spin = QSpinBox()
        self.log_size_spin.setRange(1, 100)
        self.log_size_spin.setValue(10)
        log_layout.addWidget(self.log_size_spin, 1, 1)
        
        log_layout.addWidget(QLabel("日志文件保留天数:"), 2, 0)
        self.log_days_spin = QSpinBox()
        self.log_days_spin.setRange(1, 365)
        self.log_days_spin.setValue(30)
        log_layout.addWidget(self.log_days_spin, 2, 1)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🏠 牛马基础")
    
    def create_reminder_settings_tab(self):
        """创建提醒设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 提醒功能组
        reminder_group = QGroupBox("催命功能")
        reminder_layout = QGridLayout(reminder_group)
        
        reminder_layout.addWidget(QLabel("启用催命功能:"), 0, 0)
        self.reminder_enabled_checkbox = QCheckBox()
        reminder_layout.addWidget(self.reminder_enabled_checkbox, 0, 1)
        
        reminder_layout.addWidget(QLabel("工作日催命:"), 1, 0)
        self.workday_reminder_checkbox = QCheckBox()
        reminder_layout.addWidget(self.workday_reminder_checkbox, 1, 1)
        
        reminder_layout.addWidget(QLabel("周末也要催:"), 2, 0)
        self.weekend_reminder_checkbox = QCheckBox()
        reminder_layout.addWidget(self.weekend_reminder_checkbox, 2, 1)
        
        layout.addWidget(reminder_group)
        
        # 工作时间组
        work_time_group = QGroupBox("受苦时间")
        work_time_layout = QGridLayout(work_time_group)
        
        work_time_layout.addWidget(QLabel("开始受苦时间:"), 0, 0)
        self.work_start_time = QTimeEdit()
        self.work_start_time.setTime(QTime(9, 0))
        work_time_layout.addWidget(self.work_start_time, 0, 1)
        
        work_time_layout.addWidget(QLabel("结束受苦时间:"), 1, 0)
        self.work_end_time = QTimeEdit()
        self.work_end_time.setTime(QTime(18, 0))
        work_time_layout.addWidget(self.work_end_time, 1, 1)
        
        work_time_layout.addWidget(QLabel("摸鱼开始时间:"), 2, 0)
        self.lunch_start_time = QTimeEdit()
        self.lunch_start_time.setTime(QTime(12, 0))
        work_time_layout.addWidget(self.lunch_start_time, 2, 1)
        
        work_time_layout.addWidget(QLabel("摸鱼结束时间:"), 3, 0)
        self.lunch_end_time = QTimeEdit()
        self.lunch_end_time.setTime(QTime(13, 0))
        work_time_layout.addWidget(self.lunch_end_time, 3, 1)
        
        layout.addWidget(work_time_group)
        
        # 间隔提醒组
        interval_group = QGroupBox("定时催命")
        interval_layout = QGridLayout(interval_group)
        
        interval_layout.addWidget(QLabel("启用定时催命:"), 0, 0)
        self.interval_reminder_checkbox = QCheckBox()
        interval_layout.addWidget(self.interval_reminder_checkbox, 0, 1)
        
        interval_layout.addWidget(QLabel("催命间隔(分钟):"), 1, 0)
        self.reminder_interval_spin = QSpinBox()
        self.reminder_interval_spin.setRange(5, 240)
        self.reminder_interval_spin.setValue(60)
        interval_layout.addWidget(self.reminder_interval_spin, 1, 1)
        
        interval_layout.addWidget(QLabel("催命消息:"), 2, 0)
        self.reminder_message_edit = QLineEdit()
        self.reminder_message_edit.setPlaceholderText("快记录你的血泪史...")
        interval_layout.addWidget(self.reminder_message_edit, 2, 1)
        
        layout.addWidget(interval_group)
        
        # 自定义提醒组
        custom_group = QGroupBox("自定义催命")
        custom_layout = QVBoxLayout(custom_group)
        
        # 提醒列表
        self.custom_reminders_list = QListWidget()
        custom_layout.addWidget(self.custom_reminders_list)
        
        # 添加提醒
        add_reminder_layout = QHBoxLayout()
        
        self.reminder_time_edit = QTimeEdit()
        self.reminder_time_edit.setTime(QTime(9, 0))
        add_reminder_layout.addWidget(QLabel("催命时间:"))
        add_reminder_layout.addWidget(self.reminder_time_edit)
        
        self.reminder_text_edit = QLineEdit()
        self.reminder_text_edit.setPlaceholderText("催命内容")
        add_reminder_layout.addWidget(QLabel("催命话术:"))
        add_reminder_layout.addWidget(self.reminder_text_edit)
        
        self.add_reminder_btn = QPushButton("添加催命")
        self.add_reminder_btn.clicked.connect(self.add_custom_reminder)
        add_reminder_layout.addWidget(self.add_reminder_btn)
        
        custom_layout.addLayout(add_reminder_layout)
        
        # 删除按钮
        self.remove_reminder_btn = QPushButton("删除催命")
        self.remove_reminder_btn.clicked.connect(self.remove_custom_reminder)
        custom_layout.addWidget(self.remove_reminder_btn)
        
        layout.addWidget(custom_group)
        
        # 自动提交组
        auto_submit_group = QGroupBox("自动甩锅")
        auto_submit_layout = QGridLayout(auto_submit_group)
        
        auto_submit_layout.addWidget(QLabel("启用自动甩锅:"), 0, 0)
        self.auto_submit_checkbox = QCheckBox()
        auto_submit_layout.addWidget(self.auto_submit_checkbox, 0, 1)
        
        auto_submit_layout.addWidget(QLabel("甩锅时间:"), 1, 0)
        self.auto_submit_time = QTimeEdit()
        self.auto_submit_time.setTime(QTime(20, 0))
        auto_submit_layout.addWidget(self.auto_submit_time, 1, 1)
        
        auto_submit_layout.addWidget(QLabel("甩锅类型:"), 2, 0)
        self.auto_submit_type_combo = QComboBox()
        self.auto_submit_type_combo.addItems(["今日血泪", "本周受苦", "本月折磨"])
        auto_submit_layout.addWidget(self.auto_submit_type_combo, 2, 1)
        
        layout.addWidget(auto_submit_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "⏰ 催命设置")
    
    def create_feishu_settings_tab(self):
        """创建飞书设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 飞书配置组
        feishu_group = QGroupBox("飞书汇报配置")
        feishu_layout = QGridLayout(feishu_group)
        
        feishu_layout.addWidget(QLabel("启用飞书汇报:"), 0, 0)
        self.feishu_enabled_checkbox = QCheckBox()
        feishu_layout.addWidget(self.feishu_enabled_checkbox, 0, 1)
        
        feishu_layout.addWidget(QLabel("App ID:"), 1, 0)
        self.feishu_app_id_edit = QLineEdit()
        self.feishu_app_id_edit.setPlaceholderText("请输入飞书应用的App ID")
        feishu_layout.addWidget(self.feishu_app_id_edit, 1, 1)
        
        feishu_layout.addWidget(QLabel("App Secret:"), 2, 0)
        self.feishu_app_secret_edit = QLineEdit()
        self.feishu_app_secret_edit.setEchoMode(QLineEdit.Password)
        self.feishu_app_secret_edit.setPlaceholderText("请输入飞书应用的App Secret")
        feishu_layout.addWidget(self.feishu_app_secret_edit, 2, 1)
        
        feishu_layout.addWidget(QLabel("群聊ID:"), 3, 0)
        self.feishu_chat_id_edit = QLineEdit()
        self.feishu_chat_id_edit.setPlaceholderText("请输入要汇报的群聊ID")
        feishu_layout.addWidget(self.feishu_chat_id_edit, 3, 1)
        
        layout.addWidget(feishu_group)
        
        # 自动汇报设置组
        auto_report_group = QGroupBox("自动血泪汇报设置")
        auto_report_layout = QGridLayout(auto_report_group)
        
        auto_report_layout.addWidget(QLabel("启用自动血泪汇报:"), 0, 0)
        self.feishu_auto_report_checkbox = QCheckBox()
        auto_report_layout.addWidget(self.feishu_auto_report_checkbox, 0, 1)
        
        auto_report_layout.addWidget(QLabel("检查间隔(分钟):"), 1, 0)
        self.feishu_check_interval_spin = QSpinBox()
        self.feishu_check_interval_spin.setRange(5, 1440)  # 5分钟到24小时
        self.feishu_check_interval_spin.setValue(30)
        auto_report_layout.addWidget(self.feishu_check_interval_spin, 1, 1)
        
        auto_report_layout.addWidget(QLabel("血泪日报提前汇报时间(小时):"), 2, 0)
        self.daily_advance_hours_spin = QSpinBox()
        self.daily_advance_hours_spin.setRange(1, 12)
        self.daily_advance_hours_spin.setValue(2)
        auto_report_layout.addWidget(self.daily_advance_hours_spin, 2, 1)
        
        auto_report_layout.addWidget(QLabel("受苦周报汇报时间:"), 3, 0)
        self.weekly_submit_time = QTimeEdit()
        self.weekly_submit_time.setTime(QTime(20, 0))
        auto_report_layout.addWidget(self.weekly_submit_time, 3, 1)
        
        auto_report_layout.addWidget(QLabel("折磨月报汇报时间:"), 4, 0)
        self.monthly_submit_time = QTimeEdit()
        self.monthly_submit_time.setTime(QTime(20, 0))
        auto_report_layout.addWidget(self.monthly_submit_time, 4, 1)
        
        layout.addWidget(auto_report_group)
        
        # 连接测试
        test_layout = QHBoxLayout()
        
        self.test_feishu_btn = QPushButton("🔗 测试汇报通道")
        self.test_feishu_btn.clicked.connect(self.test_feishu_connection)
        test_layout.addWidget(self.test_feishu_btn)
        
        self.feishu_test_progress = QProgressBar()
        self.feishu_test_progress.setVisible(False)
        test_layout.addWidget(self.feishu_test_progress)
        
        test_layout.addStretch()
        
        layout.addLayout(test_layout)
        
        # 使用说明
        help_group = QGroupBox("血泪汇报指南")
        help_layout = QVBoxLayout(help_group)
        
        help_text = QLabel(
            "1. 在飞书开放平台创建应用，获取App ID和App Secret\n"
            "2. 将汇报机器人添加到目标群聊中\n"
            "3. 获取群聊ID（可通过群聊设置查看）\n"
            "4. 配置完成后点击'测试汇报通道'验证配置\n"
            "5. 启用自动汇报后，系统会在指定时间自动发送血泪史"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #666; padding: 10px; background-color: #f5f5f5; border-radius: 5px;")
        help_layout.addWidget(help_text)
        
        layout.addWidget(help_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🚀 飞书汇报")
    
    def create_ai_settings_tab(self):
        """创建AI设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # AI配置组
        ai_group = QGroupBox("AI血泪润色配置")
        ai_layout = QGridLayout(ai_group)
        
        ai_layout.addWidget(QLabel("启用AI润色:"), 0, 0)
        self.ai_enabled_checkbox = QCheckBox()
        ai_layout.addWidget(self.ai_enabled_checkbox, 0, 1)
        
        # 大模型提供商选择
        ai_layout.addWidget(QLabel("AI血泪润色师:"), 1, 0)
        self.ai_provider_combo = QComboBox()
        self.ai_provider_combo.addItems([
            "DeepSeek",
            "智谱AI",
            "百度文心",
            "阿里通义",
            "Doubao"
        ])
        self.ai_provider_combo.currentIndexChanged.connect(self.on_ai_provider_changed)
        ai_layout.addWidget(self.ai_provider_combo, 1, 1)
        
        ai_layout.addWidget(QLabel("API密钥:"), 2, 0)
        self.ai_api_key_edit = QLineEdit()
        self.ai_api_key_edit.setEchoMode(QLineEdit.Password)
        self.ai_api_key_edit.setPlaceholderText("请输入API密钥")
        ai_layout.addWidget(self.ai_api_key_edit, 2, 1)
        
        ai_layout.addWidget(QLabel("API基础URL:"), 3, 0)
        self.ai_api_base_edit = QLineEdit()
        self.ai_api_base_edit.setPlaceholderText("默认将使用选定润色师的标准API地址")
        ai_layout.addWidget(self.ai_api_base_edit, 3, 1)
        
        ai_layout.addWidget(QLabel("润色模型:"), 4, 0)
        self.ai_model_combo = QComboBox()
        self.ai_model_combo.setEditable(True)
        # 初始加载DeepSeek模型
        self.ai_model_combo.addItems([
            "deepseek-chat",
            "deepseek-coder"
        ])
        ai_layout.addWidget(self.ai_model_combo, 4, 1)
        
        layout.addWidget(ai_group)
        
        # 生成参数组
        params_group = QGroupBox("血泪润色参数")
        params_layout = QGridLayout(params_group)
        
        params_layout.addWidget(QLabel("润色创意度:"), 0, 0)
        self.ai_temperature_slider = QSlider(Qt.Horizontal)
        self.ai_temperature_slider.setRange(0, 100)
        self.ai_temperature_slider.setValue(70)
        self.ai_temperature_slider.valueChanged.connect(self.update_temperature_label)
        params_layout.addWidget(self.ai_temperature_slider, 0, 1)
        
        self.ai_temperature_label = QLabel("0.7")
        params_layout.addWidget(self.ai_temperature_label, 0, 2)
        
        params_layout.addWidget(QLabel("最大润色字数:"), 1, 0)
        self.ai_max_tokens_spin = QSpinBox()
        self.ai_max_tokens_spin.setRange(100, 8000)
        self.ai_max_tokens_spin.setValue(2000)
        params_layout.addWidget(self.ai_max_tokens_spin, 1, 1, 1, 2)
        
        params_layout.addWidget(QLabel("润色超时时间(秒):"), 2, 0)
        self.ai_timeout_spin = QSpinBox()
        self.ai_timeout_spin.setRange(10, 300)
        self.ai_timeout_spin.setValue(60)
        params_layout.addWidget(self.ai_timeout_spin, 2, 1, 1, 2)
        
        params_layout.addWidget(QLabel("润色重试次数:"), 3, 0)
        self.ai_retry_spin = QSpinBox()
        self.ai_retry_spin.setRange(1, 10)
        self.ai_retry_spin.setValue(3)
        params_layout.addWidget(self.ai_retry_spin, 3, 1, 1, 2)
        
        layout.addWidget(params_group)
        
        # 代理设置组
        proxy_group = QGroupBox("网络代理设置")
        proxy_layout = QGridLayout(proxy_group)
        
        proxy_layout.addWidget(QLabel("使用网络代理:"), 0, 0)
        self.ai_use_proxy_checkbox = QCheckBox()
        proxy_layout.addWidget(self.ai_use_proxy_checkbox, 0, 1)
        
        proxy_layout.addWidget(QLabel("代理地址:"), 1, 0)
        self.ai_proxy_url_edit = QLineEdit()
        self.ai_proxy_url_edit.setPlaceholderText("http://127.0.0.1:7890")
        proxy_layout.addWidget(self.ai_proxy_url_edit, 1, 1)
        
        layout.addWidget(proxy_group)
        
        # 连接测试
        test_layout = QHBoxLayout()
        
        self.test_ai_btn = QPushButton("🔗 测试润色师")
        self.test_ai_btn.clicked.connect(self.test_ai_connection)
        test_layout.addWidget(self.test_ai_btn)
        
        self.ai_test_progress = QProgressBar()
        self.ai_test_progress.setVisible(False)
        test_layout.addWidget(self.ai_test_progress)
        
        test_layout.addStretch()
        
        layout.addLayout(test_layout)
        
        # 提示词设置组
        prompt_group = QGroupBox("血泪润色风格设置")
        prompt_layout = QVBoxLayout(prompt_group)
        
        prompt_layout.addWidget(QLabel("润色风格提示词:"))
        self.ai_system_prompt_edit = QTextEdit()
        self.ai_system_prompt_edit.setMaximumHeight(100)
        self.ai_system_prompt_edit.setPlaceholderText("自定义AI润色师的血泪润色风格...")
        prompt_layout.addWidget(self.ai_system_prompt_edit)
        
        layout.addWidget(prompt_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🤖 AI润色师")
    
    def create_advanced_settings_tab(self):
        """创建高级设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 性能设置组
        performance_group = QGroupBox("牛马性能优化")
        performance_layout = QGridLayout(performance_group)
        
        performance_layout.addWidget(QLabel("启用硬件加速:"), 0, 0)
        self.hardware_acceleration_checkbox = QCheckBox()
        performance_layout.addWidget(self.hardware_acceleration_checkbox, 0, 1)
        
        performance_layout.addWidget(QLabel("内存缓存大小(MB):"), 1, 0)
        self.memory_cache_spin = QSpinBox()
        self.memory_cache_spin.setRange(50, 1000)
        self.memory_cache_spin.setValue(200)
        performance_layout.addWidget(self.memory_cache_spin, 1, 1)
        
        performance_layout.addWidget(QLabel("并发处理线程数:"), 2, 0)
        self.thread_count_spin = QSpinBox()
        self.thread_count_spin.setRange(1, 16)
        self.thread_count_spin.setValue(4)
        performance_layout.addWidget(self.thread_count_spin, 2, 1)
        
        layout.addWidget(performance_group)
        
        # 安全设置组
        security_group = QGroupBox("血泪安全保护")
        security_layout = QGridLayout(security_group)
        
        security_layout.addWidget(QLabel("启用血泪加密:"), 0, 0)
        self.data_encryption_checkbox = QCheckBox()
        security_layout.addWidget(self.data_encryption_checkbox, 0, 1)
        
        security_layout.addWidget(QLabel("自动锁定时间(分钟):"), 1, 0)
        self.auto_lock_spin = QSpinBox()
        self.auto_lock_spin.setRange(0, 120)
        self.auto_lock_spin.setValue(0)  # 0表示禁用
        security_layout.addWidget(self.auto_lock_spin, 1, 1)
        
        layout.addWidget(security_group)
        
        # 网络设置组
        network_group = QGroupBox("网络连接设置")
        network_layout = QGridLayout(network_group)
        
        network_layout.addWidget(QLabel("连接超时(秒):"), 0, 0)
        self.network_timeout_spin = QSpinBox()
        self.network_timeout_spin.setRange(5, 300)
        self.network_timeout_spin.setValue(30)
        network_layout.addWidget(self.network_timeout_spin, 0, 1)
        
        network_layout.addWidget(QLabel("重试次数:"), 1, 0)
        self.network_retry_spin = QSpinBox()
        self.network_retry_spin.setRange(1, 10)
        self.network_retry_spin.setValue(3)
        network_layout.addWidget(self.network_retry_spin, 1, 1)
        
        layout.addWidget(network_group)
        
        # 维护操作组
        maintenance_group = QGroupBox("血泪维护操作")
        maintenance_layout = QVBoxLayout(maintenance_group)
        
        # 数据备份
        backup_layout = QHBoxLayout()
        self.backup_data_btn = QPushButton("📦 备份血泪史")
        self.backup_data_btn.clicked.connect(self.backup_data)
        backup_layout.addWidget(self.backup_data_btn)
        
        self.restore_data_btn = QPushButton("📥 恢复血泪史")
        self.restore_data_btn.clicked.connect(self.restore_data)
        backup_layout.addWidget(self.restore_data_btn)
        
        backup_layout.addStretch()
        maintenance_layout.addLayout(backup_layout)
        
        # 缓存清理
        cache_layout = QHBoxLayout()
        self.clear_cache_btn = QPushButton("🧹 清理缓存")
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        cache_layout.addWidget(self.clear_cache_btn)
        
        self.clear_logs_btn = QPushButton("📝 清理血泪日志")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        cache_layout.addWidget(self.clear_logs_btn)
        
        cache_layout.addStretch()
        maintenance_layout.addLayout(cache_layout)
        
        # 配置管理
        config_layout = QHBoxLayout()
        self.export_config_btn = QPushButton("📤 导出调教配置")
        self.export_config_btn.clicked.connect(self.export_config)
        config_layout.addWidget(self.export_config_btn)
        
        self.import_config_btn = QPushButton("📥 导入调教配置")
        self.import_config_btn.clicked.connect(self.import_config)
        config_layout.addWidget(self.import_config_btn)
        
        config_layout.addStretch()
        maintenance_layout.addLayout(config_layout)
        
        layout.addWidget(maintenance_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🔧 高级调教")
    
    def create_bottom_buttons(self, parent_layout):
        """创建底部按钮"""
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("✅ 应用调教")
        self.apply_btn.clicked.connect(self.apply_settings)
        self.apply_btn.setStyleSheet(
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
        button_layout.addWidget(self.apply_btn)
        
        self.save_btn = QPushButton("💾 保存调教")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet(
            "QPushButton {"
            "    background-color: #2196f3;"
            "    color: white;"
            "    border: none;"
            "    padding: 10px 20px;"
            "    border-radius: 5px;"
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #1976d2;"
            "}"
        )
        button_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("🔄 重置调教")
        self.reset_btn.clicked.connect(self.reset_settings)
        self.reset_btn.setStyleSheet(
            "QPushButton {"
            "    background-color: #ff9800;"
            "    color: white;"
            "    border: none;"
            "    padding: 10px 20px;"
            "    border-radius: 5px;"
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #f57c00;"
            "}"
        )
        button_layout.addWidget(self.reset_btn)
        
        self.cancel_btn = QPushButton("❌ 算了")
        self.cancel_btn.clicked.connect(self.close)
        self.cancel_btn.setStyleSheet(
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
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        
        parent_layout.addLayout(button_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        # 启用状态变化
        self.feishu_enabled_checkbox.toggled.connect(self.on_feishu_enabled_changed)
        self.ai_enabled_checkbox.toggled.connect(self.on_ai_enabled_changed)
        self.ai_use_proxy_checkbox.toggled.connect(self.on_proxy_enabled_changed)
    
    def load_settings(self):
        """加载设置"""
        # 加载基本设置
        settings = self.config_manager.get_settings()
        
        self.start_minimized_checkbox.setChecked(settings.get("start_minimized", False))
        self.auto_start_checkbox.setChecked(settings.get("auto_start", False))
        self.close_to_tray_checkbox.setChecked(settings.get("close_to_tray", True))
        self.quick_add_button_checkbox.setChecked(settings.get("quick_add_button", True))
        self.theme_combo.setCurrentText(settings.get("theme", "浅色"))
        self.language_combo.setCurrentText(settings.get("language", "中文"))
        
        self.data_path_edit.setText(settings.get("data_path", "./data"))
        self.backup_interval_spin.setValue(settings.get("backup_interval", 7))
        self.backup_count_spin.setValue(settings.get("backup_count", 10))
        
        self.log_level_combo.setCurrentText(settings.get("log_level", "INFO"))
        self.log_size_spin.setValue(settings.get("log_size_mb", 10))
        self.log_days_spin.setValue(settings.get("log_days", 30))
        
        # 加载提醒设置
        self.reminder_enabled_checkbox.setChecked(settings.get("reminder_enabled", True))
        self.workday_reminder_checkbox.setChecked(settings.get("workday_reminder", True))
        self.weekend_reminder_checkbox.setChecked(settings.get("weekend_reminder", False))
        
        # 工作时间
        work_start = settings.get("work_start_time", "09:00")
        work_end = settings.get("work_end_time", "18:00")
        lunch_start = settings.get("lunch_start_time", "12:00")
        lunch_end = settings.get("lunch_end_time", "13:00")
        
        self.work_start_time.setTime(QTime.fromString(work_start, "HH:mm"))
        self.work_end_time.setTime(QTime.fromString(work_end, "HH:mm"))
        self.lunch_start_time.setTime(QTime.fromString(lunch_start, "HH:mm"))
        self.lunch_end_time.setTime(QTime.fromString(lunch_end, "HH:mm"))
        
        # 间隔提醒
        self.interval_reminder_checkbox.setChecked(settings.get("interval_reminder", True))
        self.reminder_interval_spin.setValue(settings.get("reminder_interval", 60))
        self.reminder_message_edit.setText(settings.get("reminder_message", "请记录您的工作内容..."))
        
        # 自动提交
        self.auto_submit_checkbox.setChecked(settings.get("auto_submit", True))
        auto_submit_time = settings.get("auto_submit_time", "20:00")
        self.auto_submit_time.setTime(QTime.fromString(auto_submit_time, "HH:mm"))
        self.auto_submit_type_combo.setCurrentText(settings.get("auto_submit_type", "日报"))
        
        # 加载自定义提醒
        self.load_custom_reminders()
        
        # 加载飞书设置
        feishu_config = self.config_manager.get_feishu_config()
        
        self.feishu_enabled_checkbox.setChecked(feishu_config.get("enabled", False))
        self.feishu_app_id_edit.setText(feishu_config.get("app_id", ""))
        self.feishu_app_secret_edit.setText(feishu_config.get("app_secret", ""))
        self.feishu_chat_id_edit.setText(feishu_config.get("chat_id", ""))
        
        # 加载自动汇报设置
        self.feishu_auto_report_checkbox.setChecked(feishu_config.get("auto_report_enabled", False))
        self.feishu_check_interval_spin.setValue(feishu_config.get("check_interval_minutes", 30))
        self.daily_advance_hours_spin.setValue(feishu_config.get("daily_advance_hours", 2))
        
        weekly_time = feishu_config.get("weekly_submit_time", "20:00")
        self.weekly_submit_time.setTime(QTime.fromString(weekly_time, "HH:mm"))
        
        monthly_time = feishu_config.get("monthly_submit_time", "20:00")
        self.monthly_submit_time.setTime(QTime.fromString(monthly_time, "HH:mm"))
        
        # 加载AI设置
        ai_config = self.config_manager.get_ai_config()
        
        self.ai_enabled_checkbox.setChecked(ai_config.get("enabled", False))
        self.ai_api_key_edit.setText(ai_config.get("api_key", ""))
        
        # 设置提供商
        provider = ai_config.get("provider", "DeepSeek")
        provider_index = self.ai_provider_combo.findText(provider)
        if provider_index >= 0:
            self.ai_provider_combo.setCurrentIndex(provider_index)
        else:
            self.ai_provider_combo.setCurrentIndex(0)  # 默认为DeepSeek
        
        # 触发提供商变更事件，加载对应提供商的配置
        self.on_ai_provider_changed()
        
        # AI参数
        temperature = ai_config.get("temperature", 0.7)
        self.ai_temperature_slider.setValue(int(temperature * 100))
        self.update_temperature_label()
        
        self.ai_max_tokens_spin.setValue(ai_config.get("max_tokens", 2000))
        self.ai_timeout_spin.setValue(ai_config.get("timeout", 60))
        self.ai_retry_spin.setValue(ai_config.get("retry_count", 3))
        
        # 代理设置
        self.ai_use_proxy_checkbox.setChecked(ai_config.get("use_proxy", False))
        self.ai_proxy_url_edit.setText(ai_config.get("proxy_url", "http://127.0.0.1:7890"))
        
        # 系统提示词
        self.ai_system_prompt_edit.setPlainText(ai_config.get("system_prompt", ""))
        
        # 加载高级设置
        self.hardware_acceleration_checkbox.setChecked(settings.get("hardware_acceleration", True))
        self.memory_cache_spin.setValue(settings.get("memory_cache_mb", 200))
        self.thread_count_spin.setValue(settings.get("thread_count", 4))
        
        self.data_encryption_checkbox.setChecked(settings.get("data_encryption", False))
        self.auto_lock_spin.setValue(settings.get("auto_lock_minutes", 0))
        
        self.network_timeout_spin.setValue(settings.get("network_timeout", 30))
        self.network_retry_spin.setValue(settings.get("network_retry", 3))
        
        # 更新UI状态
        self.on_feishu_enabled_changed()
        self.on_ai_enabled_changed()
        self.on_proxy_enabled_changed()
    
    def load_custom_reminders(self):
        """加载自定义提醒"""
        settings = self.config_manager.get_settings()
        custom_reminders = settings.get("custom_reminders", [])
        
        self.custom_reminders_list.clear()
        for reminder in custom_reminders:
            time_str = reminder.get("time", "09:00")
            text = reminder.get("text", "")
            item_text = f"{time_str} - {text}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, reminder)
            self.custom_reminders_list.addItem(item)
    
    def add_custom_reminder(self):
        """添加自定义提醒"""
        time_str = self.reminder_time_edit.time().toString("HH:mm")
        text = self.reminder_text_edit.text().strip()
        
        if not text:
            QMessageBox.warning(self, "警告", "请输入提醒内容！")
            return
        
        reminder = {
            "time": time_str,
            "text": text
        }
        
        item_text = f"{time_str} - {text}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, reminder)
        self.custom_reminders_list.addItem(item)
        
        # 清空输入
        self.reminder_text_edit.clear()
    
    def remove_custom_reminder(self):
        """删除自定义提醒"""
        current_item = self.custom_reminders_list.currentItem()
        if current_item:
            row = self.custom_reminders_list.row(current_item)
            self.custom_reminders_list.takeItem(row)
    
    def on_feishu_enabled_changed(self):
        """飞书启用状态变化"""
        enabled = self.feishu_enabled_checkbox.isChecked()
        
        self.feishu_app_id_edit.setEnabled(enabled)
        self.feishu_app_secret_edit.setEnabled(enabled)
        self.feishu_chat_id_edit.setEnabled(enabled)
        self.test_feishu_btn.setEnabled(enabled)
        
        # 自动汇报相关控件
        self.feishu_auto_report_checkbox.setEnabled(enabled)
        self.feishu_check_interval_spin.setEnabled(enabled)
        self.daily_advance_hours_spin.setEnabled(enabled)
        self.weekly_submit_time.setEnabled(enabled)
        self.monthly_submit_time.setEnabled(enabled)
    
    def on_ai_enabled_changed(self):
        """AI启用状态变化"""
        enabled = self.ai_enabled_checkbox.isChecked()
        
        self.ai_provider_combo.setEnabled(enabled)
        self.ai_api_key_edit.setEnabled(enabled)
        self.ai_api_base_edit.setEnabled(enabled)
        self.ai_model_combo.setEnabled(enabled)
        self.ai_temperature_slider.setEnabled(enabled)
        self.ai_max_tokens_spin.setEnabled(enabled)
        self.ai_timeout_spin.setEnabled(enabled)
        self.ai_retry_spin.setEnabled(enabled)
        self.ai_use_proxy_checkbox.setEnabled(enabled)
        self.ai_system_prompt_edit.setEnabled(enabled)
        self.test_ai_btn.setEnabled(enabled)
        
        self.on_proxy_enabled_changed()
        
    def on_ai_provider_changed(self):
        """大模型提供商变更"""
        provider = self.ai_provider_combo.currentText()
        
        # 从AIReportGenerator获取提供商信息
        from ai_generator import AIReportGenerator
        provider_info = AIReportGenerator.PROVIDERS.get(provider, {})
        
        # 获取该提供商的保存配置
        provider_config = self.config_manager.get_ai_provider_config(provider)
        
        # 更新API基础URL
        saved_api_base = provider_config.get("api_base_url", "")
        default_api_base = provider_info.get("api_base", "")
        
        if saved_api_base:
            # 如果有保存的API基础URL，使用保存的
            self.ai_api_base_edit.setText(saved_api_base)
        elif default_api_base:
            # 否则使用默认的
            self.ai_api_base_edit.setText(default_api_base)
        else:
            self.ai_api_base_edit.setText("")
        
        # 设置占位符
        if default_api_base:
            self.ai_api_base_edit.setPlaceholderText(f"默认: {default_api_base}")
        else:
            self.ai_api_base_edit.setPlaceholderText("请输入API基础URL")
        
        # 更新API密钥
        saved_api_key = provider_config.get("api_key", "")
        self.ai_api_key_edit.setText(saved_api_key)
        
        # 更新模型列表
        self.ai_model_combo.clear()
        models = provider_info.get("models", [])
        if models:
            self.ai_model_combo.addItems(models)
            # 设置保存的模型或默认模型
            saved_model = provider_config.get("model", "")
            if saved_model and self.ai_model_combo.findText(saved_model) >= 0:
                self.ai_model_combo.setCurrentText(saved_model)
            else:
                self.ai_model_combo.setCurrentIndex(0)
        
        # 更新API密钥占位符
        placeholders = {
            "DeepSeek": "以sk-开头的DeepSeek API密钥",
            "智谱AI": "智谱AI API密钥",
            "百度文心": "百度文心API密钥",
            "阿里通义": "阿里通义千问API密钥",
            "Doubao": "Doubao API密钥"
        }
        self.ai_api_key_edit.setPlaceholderText(placeholders.get(provider, "请输入API密钥"))
    
    def on_proxy_enabled_changed(self):
        """代理启用状态变化"""
        ai_enabled = self.ai_enabled_checkbox.isChecked()
        proxy_enabled = self.ai_use_proxy_checkbox.isChecked()
        
        self.ai_proxy_url_edit.setEnabled(ai_enabled and proxy_enabled)
    
    def update_temperature_label(self):
        """更新温度标签"""
        value = self.ai_temperature_slider.value() / 100.0
        self.ai_temperature_label.setText(f"{value:.1f}")
    
    def test_feishu_connection(self):
        """测试飞书连接"""
        if self.test_thread and self.test_thread.isRunning():
            return
        
        feishu_config = {
            "app_id": self.feishu_app_id_edit.text().strip(),
            "app_secret": self.feishu_app_secret_edit.text().strip()
        }
        
        self.test_thread = ConnectionTestThread("feishu", feishu_config)
        self.test_thread.test_completed.connect(self.on_feishu_test_completed)
        
        self.test_feishu_btn.setEnabled(False)
        self.feishu_test_progress.setVisible(True)
        self.feishu_test_progress.setRange(0, 0)  # 无限进度条
        
        self.test_thread.start()
    
    def on_feishu_test_completed(self, success: bool, message: str):
        """飞书测试完成"""
        self.test_feishu_btn.setEnabled(True)
        self.feishu_test_progress.setVisible(False)
        
        if success:
            QMessageBox.information(self, "测试成功", f"飞书连接测试成功！\n{message}")
        else:
            QMessageBox.warning(self, "测试失败", f"飞书连接测试失败！\n{message}")
    
    def test_ai_connection(self):
        """测试AI连接"""
        if self.test_thread and self.test_thread.isRunning():
            return
        
        ai_config = {
            "provider": self.ai_provider_combo.currentText(),
            "api_key": self.ai_api_key_edit.text().strip(),
            "api_base_url": self.ai_api_base_edit.text().strip(),
            "model": self.ai_model_combo.currentText(),
            "timeout": self.ai_timeout_spin.value(),
            "use_proxy": self.ai_use_proxy_checkbox.isChecked(),
            "proxy_url": self.ai_proxy_url_edit.text().strip()
        }
        
        self.test_thread = ConnectionTestThread("ai", ai_config)
        self.test_thread.test_completed.connect(self.on_ai_test_completed)
        
        self.test_ai_btn.setEnabled(False)
        self.ai_test_progress.setVisible(True)
        self.ai_test_progress.setRange(0, 0)  # 无限进度条
        
        self.test_thread.start()
    
    def on_ai_test_completed(self, success: bool, message: str):
        """AI测试完成"""
        self.test_ai_btn.setEnabled(True)
        self.ai_test_progress.setVisible(False)
        
        if success:
            QMessageBox.information(self, "测试成功", f"AI连接测试成功！\n{message}")
        else:
            QMessageBox.warning(self, "测试失败", f"AI连接测试失败！\n{message}")
    
    def browse_data_path(self):
        """浏览数据路径"""
        current_path = self.data_path_edit.text() or "./data"
        
        path = QFileDialog.getExistingDirectory(
            self, "选择数据存储路径", current_path
        )
        
        if path:
            self.data_path_edit.setText(path)
    
    def backup_data(self):
        """备份数据"""
        try:
            backup_path = self.config_manager.backup_data()
            if backup_path:
                QMessageBox.information(
                    self, "备份成功", 
                    f"数据已备份到：{backup_path}"
                )
            else:
                QMessageBox.warning(self, "备份失败", "数据备份失败！")
        except Exception as e:
            QMessageBox.critical(self, "备份错误", f"备份过程中出现错误：{str(e)}")
    
    def restore_data(self):
        """恢复数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择备份文件", "", 
            "备份文件 (*.zip);;所有文件 (*)"
        )
        
        if file_path:
            reply = QMessageBox.question(
                self, "确认恢复", 
                "恢复数据将覆盖当前所有数据，确定要继续吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    if self.config_manager.restore_data(file_path):
                        QMessageBox.information(
                            self, "恢复成功", 
                            "数据恢复成功！请重启应用程序。"
                        )
                    else:
                        QMessageBox.warning(self, "恢复失败", "数据恢复失败！")
                except Exception as e:
                    QMessageBox.critical(self, "恢复错误", f"恢复过程中出现错误：{str(e)}")
    
    def clear_cache(self):
        """清理缓存"""
        reply = QMessageBox.question(
            self, "确认清理", 
            "确定要清理所有缓存文件吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.config_manager.clear_cache():
                    QMessageBox.information(self, "清理成功", "缓存已清理完成！")
                else:
                    QMessageBox.warning(self, "清理失败", "缓存清理失败！")
            except Exception as e:
                QMessageBox.critical(self, "清理错误", f"清理过程中出现错误：{str(e)}")
    
    def clear_logs(self):
        """清理日志"""
        reply = QMessageBox.question(
            self, "确认清理", 
            "确定要清理所有日志文件吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.config_manager.clear_logs():
                    QMessageBox.information(self, "清理成功", "日志已清理完成！")
                else:
                    QMessageBox.warning(self, "清理失败", "日志清理失败！")
            except Exception as e:
                QMessageBox.critical(self, "清理错误", f"清理过程中出现错误：{str(e)}")
    
    def export_config(self):
        """导出配置"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出配置", 
            f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            try:
                if self.config_manager.export_config(file_path):
                    QMessageBox.information(
                        self, "导出成功", 
                        f"调教配置已导出到：{file_path}"
                    )
                else:
                    QMessageBox.warning(self, "导出失败", "调教配置导出失败！")
            except Exception as e:
                QMessageBox.critical(self, "导出错误", f"导出调教配置时出现错误：{str(e)}")
    
    def import_config(self):
        """导入配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入配置", "", 
            "JSON文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            reply = QMessageBox.question(
                self, "确认导入", 
                "导入调教配置将覆盖当前设置，确定要继续吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    if self.config_manager.import_config(file_path):
                        QMessageBox.information(
                            self, "导入成功", 
                            "调教配置导入成功！请重启牛马助手。"
                        )
                        self.load_settings()  # 重新加载设置
                    else:
                        QMessageBox.warning(self, "导入失败", "调教配置导入失败！")
                except Exception as e:
                    QMessageBox.critical(self, "导入错误", f"导入调教配置时出现错误：{str(e)}")
    
    def apply_settings(self):
        """应用设置"""
        self.save_settings()
        self.settings_changed.emit()
        QMessageBox.information(self, "调教成功", "牛马调教已应用！")
    
    def save_settings(self):
        """保存设置"""
        try:
            # 保存基本设置
            settings = {
                "start_minimized": self.start_minimized_checkbox.isChecked(),
                "auto_start": self.auto_start_checkbox.isChecked(),
                "close_to_tray": self.close_to_tray_checkbox.isChecked(),
                "quick_add_button": self.quick_add_button_checkbox.isChecked(),
                "theme": self.theme_combo.currentText(),
                "language": self.language_combo.currentText(),
                "data_path": self.data_path_edit.text(),
                "backup_interval": self.backup_interval_spin.value(),
                "backup_count": self.backup_count_spin.value(),
                "log_level": self.log_level_combo.currentText(),
                "log_size_mb": self.log_size_spin.value(),
                "log_days": self.log_days_spin.value(),
                "reminder_enabled": self.reminder_enabled_checkbox.isChecked(),
                "workday_reminder": self.workday_reminder_checkbox.isChecked(),
                "weekend_reminder": self.weekend_reminder_checkbox.isChecked(),
                "work_start_time": self.work_start_time.time().toString("HH:mm"),
                "work_end_time": self.work_end_time.time().toString("HH:mm"),
                "lunch_start_time": self.lunch_start_time.time().toString("HH:mm"),
                "lunch_end_time": self.lunch_end_time.time().toString("HH:mm"),
                "interval_reminder": self.interval_reminder_checkbox.isChecked(),
                "reminder_interval": self.reminder_interval_spin.value(),
                "reminder_message": self.reminder_message_edit.text(),
                "auto_submit": self.auto_submit_checkbox.isChecked(),
                "auto_submit_time": self.auto_submit_time.time().toString("HH:mm"),
                "auto_submit_type": self.auto_submit_type_combo.currentText(),
                "hardware_acceleration": self.hardware_acceleration_checkbox.isChecked(),
                "memory_cache_mb": self.memory_cache_spin.value(),
                "thread_count": self.thread_count_spin.value(),
                "data_encryption": self.data_encryption_checkbox.isChecked(),
                "auto_lock_minutes": self.auto_lock_spin.value(),
                "network_timeout": self.network_timeout_spin.value(),
                "network_retry": self.network_retry_spin.value()
            }
            
            # 保存自定义提醒
            custom_reminders = []
            for i in range(self.custom_reminders_list.count()):
                item = self.custom_reminders_list.item(i)
                reminder_data = item.data(Qt.UserRole)
                if reminder_data:
                    custom_reminders.append(reminder_data)
            settings["custom_reminders"] = custom_reminders
            
            self.config_manager.update_settings(settings)
            
            # 保存飞书设置
            feishu_config = {
                "enabled": self.feishu_enabled_checkbox.isChecked(),
                "app_id": self.feishu_app_id_edit.text(),
                "app_secret": self.feishu_app_secret_edit.text(),
                "chat_id": self.feishu_chat_id_edit.text(),
                "auto_report_enabled": self.feishu_auto_report_checkbox.isChecked(),
                "check_interval_minutes": self.feishu_check_interval_spin.value(),
                "daily_advance_hours": self.daily_advance_hours_spin.value(),
                "weekly_submit_time": self.weekly_submit_time.time().toString("HH:mm"),
                "monthly_submit_time": self.monthly_submit_time.time().toString("HH:mm")
            }
            
            self.config_manager.update_feishu_config(feishu_config)
            
            # 验证AI设置
            ai_enabled = self.ai_enabled_checkbox.isChecked()
            current_provider = self.ai_provider_combo.currentText()
            api_key = self.ai_api_key_edit.text().strip()
            api_base = self.ai_api_base_edit.text().strip()
            
            # 如果启用AI功能，必须有API密钥
            if ai_enabled and not api_key:
                QMessageBox.warning(self, "验证失败", "启用AI血泪润色师时必须提供API密钥！")
                return
            
            # 保存当前提供商的配置
            if api_key or api_base:  # 只有在有配置时才保存
                provider_config = {
                    "api_key": api_key,
                    "api_base_url": api_base,
                    "model": self.ai_model_combo.currentText()
                }
                self.config_manager.update_ai_provider_config(current_provider, provider_config)
            
            # 保存AI设置
            ai_config = {
                "enabled": ai_enabled,
                "provider": current_provider,
                "api_key": api_key,
                "api_base_url": api_base,
                "model": self.ai_model_combo.currentText(),
                "temperature": self.ai_temperature_slider.value() / 100.0,
                "max_tokens": self.ai_max_tokens_spin.value(),
                "timeout": self.ai_timeout_spin.value(),
                "retry_count": self.ai_retry_spin.value(),
                "use_proxy": self.ai_use_proxy_checkbox.isChecked(),
                "proxy_url": self.ai_proxy_url_edit.text(),
                "system_prompt": self.ai_system_prompt_edit.toPlainText()
            }
            
            self.config_manager.update_ai_config(ai_config)
            
            QMessageBox.information(self, "保存成功", "牛马调教已保存！")
            
        except Exception as e:
            QMessageBox.critical(self, "保存错误", f"保存牛马调教时出现错误：{str(e)}")
    
    def reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要重置所有牛马调教为默认值吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.config_manager.reset_to_defaults()
                self.load_settings()
                QMessageBox.information(self, "重置成功", "牛马调教已重置为默认值！")
            except Exception as e:
                QMessageBox.critical(self, "重置错误", f"重置牛马调教时出现错误：{str(e)}")
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止测试线程
        if self.test_thread and self.test_thread.isRunning():
            self.test_thread.terminate()
            self.test_thread.wait()
        
        event.accept()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 创建设置窗口
    window = SettingsWindow(config_manager)
    window.show()
    
    sys.exit(app.exec_())