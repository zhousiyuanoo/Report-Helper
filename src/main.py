#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
牛马日报助手 - 主程序
一个智能的工作日报管理工具
"""

import sys
import os
import logging
import tempfile
import psutil
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入项目模块
from .config_manager import ConfigManager
from .work_log_window import WorkLogWindow
from .report_window import ReportWindow
from .settings_window import SettingsWindow
from .system_tray import SystemTray
from .timer_manager import TimerManager
from .report_generator import ReportGenerator
from .quick_add_button import QuickAddButton
from .feishu_scheduler import FeishuScheduler


class SingleInstance:
    """单实例检查类"""
    
    def __init__(self, app_name="ReportHelper"):
        self.app_name = app_name
        self.lock_file = None
        self.is_locked = False
        
        # 创建锁文件路径
        temp_dir = tempfile.gettempdir()
        self.lock_file_path = os.path.join(temp_dir, f"{app_name}.lock")
    
    def is_another_instance_running(self):
        """检查是否有其他实例正在运行"""
        try:
            # 检查锁文件是否存在
            if os.path.exists(self.lock_file_path):
                # 读取PID
                with open(self.lock_file_path, 'r') as f:
                    pid = int(f.read().strip())
                
                # 检查进程是否还在运行
                if psutil.pid_exists(pid):
                    try:
                        process = psutil.Process(pid)
                        # 检查进程名称是否匹配
                        if "python" in process.name().lower() or "reporthelper" in process.name().lower():
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # 如果进程不存在，删除锁文件
                os.remove(self.lock_file_path)
            
            return False
            
        except Exception as e:
            logging.warning(f"检查实例状态时出错: {e}")
            return False
    
    def create_lock(self):
        """创建锁文件"""
        try:
            with open(self.lock_file_path, 'w') as f:
                f.write(str(os.getpid()))
            self.is_locked = True
            return True
        except Exception as e:
            logging.error(f"创建锁文件失败: {e}")
            return False
    
    def release_lock(self):
        """释放锁文件"""
        try:
            if self.is_locked and os.path.exists(self.lock_file_path):
                os.remove(self.lock_file_path)
                self.is_locked = False
        except Exception as e:
            logging.warning(f"释放锁文件时出错: {e}")
    
    def kill_existing_instance(self):
        """终止现有实例"""
        try:
            if os.path.exists(self.lock_file_path):
                with open(self.lock_file_path, 'r') as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    try:
                        process = psutil.Process(pid)
                        process.terminate()
                        # 等待进程结束
                        process.wait(timeout=5)
                        logging.info(f"已终止现有实例 (PID: {pid})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        pass
                
                # 删除锁文件
                os.remove(self.lock_file_path)
                return True
        except Exception as e:
            logging.error(f"终止现有实例失败: {e}")
            return False


class ApplicationManager:
    """应用程序管理器"""
    
    def __init__(self):
        self.app = None
        self.config_manager = None
        self.work_log_window = None
        self.report_window = None
        self.settings_window = None
        self.system_tray = None
        self.timer_manager = None
        self.report_generator = None
        self.quick_add_button = None
        self.feishu_scheduler = None
        self.single_instance = None
        
        # 初始化日志
        self.setup_logging()
        
        # 检查单实例
        self.setup_single_instance()
        
        # 初始化应用程序
        self.setup_application()
        
        # 初始化组件
        self.setup_components()
        
        # 设置信号连接
        self.setup_connections()
        
        logging.info("应用程序初始化完成")
    
    def setup_logging(self):
        """设置日志"""
        # 确保日志目录存在
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 配置日志
        log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # 设置第三方库日志级别
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
    
    def setup_single_instance(self):
        """设置单实例检查"""
        try:
            self.single_instance = SingleInstance("ReportHelper")
            
            # 检查是否有其他实例正在运行
            if self.single_instance.is_another_instance_running():
                print("检测到应用程序已在运行，正在关闭之前的实例...")
                
                # 尝试终止现有实例
                if self.single_instance.kill_existing_instance():
                    print("已成功关闭之前的实例")
                    import time
                    time.sleep(1)  # 等待一秒确保进程完全结束
                else:
                    print("无法关闭之前的实例，程序将退出")
                    sys.exit(1)
            
            # 创建锁文件
            if not self.single_instance.create_lock():
                print("无法创建锁文件，程序将退出")
                sys.exit(1)
            
            print("单实例检查通过")
            
        except Exception as e:
            print(f"单实例检查失败: {e}")
            sys.exit(1)
    
    def setup_application(self):
        """设置应用程序"""
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # 关闭窗口时不退出应用
        
        # 设置应用程序信息
        self.app.setApplicationName("牛马血泪助手")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Report Helper")
        
        # 设置应用程序图标
        icon_path = os.path.join(project_root, "resources", "niuma.svg")
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))
    
    def setup_components(self):
        """设置组件"""
        try:
            # 初始化配置管理器
            self.config_manager = ConfigManager()
            
            # 将ConfigManager设置为应用程序的属性，以便QuickAddButton可以访问
            self.app.setProperty("config_manager", self.config_manager)
            
            # 初始化报告生成器
            self.report_generator = ReportGenerator(self.config_manager)
            
            # 初始化定时管理器
            self.timer_manager = TimerManager(self.config_manager, self.report_generator)
            
            # 初始化窗口
            self.work_log_window = WorkLogWindow(self.config_manager)
            self.report_window = ReportWindow(self.config_manager, self.report_generator)
            self.settings_window = SettingsWindow(self.config_manager)
            
            # 初始化系统托盘
            self.system_tray = SystemTray(
                self.config_manager,
                self.timer_manager
            )
            
            # 连接窗口
            self.system_tray.connect_windows(
                self.work_log_window,
                self.report_window,
                self.settings_window
            )
            
            # 初始化快速添加按钮
            self.quick_add_button = QuickAddButton()
            # 连接信号
            self.quick_add_button.add_work_log_signal.connect(self.work_log_window.add_quick_log)
            
            # 初始化飞书调度器
            self.feishu_scheduler = FeishuScheduler(
                self.config_manager, 
                self._generate_report_for_scheduler
            )
            
            logging.info("所有组件初始化完成")
            
        except Exception as e:
            logging.error(f"组件初始化失败: {str(e)}")
            QMessageBox.critical(
                None, "初始化错误", 
                f"应用程序初始化失败：{str(e)}\n\n请检查配置文件和依赖项。"
            )
            sys.exit(1)
    
    def setup_connections(self):
        """设置信号连接"""
        try:
            # 设置窗口信号连接
            if self.settings_window:
                self.settings_window.settings_changed.connect(self.on_settings_changed)
            
            # 设置定时器信号连接
            if self.timer_manager:
                self.timer_manager.reminder_triggered.connect(self.on_reminder_triggered)
                self.timer_manager.auto_submit_triggered.connect(self.on_auto_submit_triggered)
            
            # 设置系统托盘信号连接
            if self.system_tray:
                self.system_tray.exit_requested.connect(self.quit_application)
            
            logging.info("信号连接设置完成")
            
        except Exception as e:
            logging.error(f"信号连接设置失败: {str(e)}")
    
    def on_settings_changed(self):
        """设置更改处理"""
        try:
            logging.info("设置已更改，重新加载配置")
            
            # 重新加载定时器设置
            if self.timer_manager:
                self.timer_manager.update_settings()
            
            # 更新系统托盘状态
            if self.system_tray:
                self.system_tray.update_status()
            
            # 更新快速添加按钮状态
            if self.quick_add_button:
                settings = self.config_manager.get_settings()
                quick_add_button_enabled = settings.get("quick_add_button", True)
                if quick_add_button_enabled:
                    self.quick_add_button.show()
                else:
                    self.quick_add_button.hide()
            
            # 重启飞书调度器
            if self.feishu_scheduler:
                self.feishu_scheduler.stop()
                if self.feishu_scheduler.start():
                    logging.info("飞书调度器已重启")
                else:
                    logging.warning("飞书调度器重启失败")
            
        except Exception as e:
            logging.error(f"设置更改处理失败: {str(e)}")
    
    def on_reminder_triggered(self, reminder_type: str, message: str):
        """提醒触发处理"""
        try:
            logging.info(f"提醒触发: {reminder_type} - {message}")
            
            if self.system_tray:
                self.system_tray.show_reminder(reminder_type, message)
            
        except Exception as e:
            logging.error(f"提醒处理失败: {str(e)}")
    
    def _generate_report_for_scheduler(self, report_type: str) -> str:
        """为调度器生成报告
        
        Args:
            report_type: 报告类型 (daily/weekly/monthly)
            
        Returns:
            生成的报告内容
        """
        try:
            if not self.report_generator:
                return ""
            
            # 根据类型生成相应的报告
            if report_type == "daily":
                return self.report_generator.generate_daily_report()
            elif report_type == "weekly":
                return self.report_generator.generate_weekly_report()
            elif report_type == "monthly":
                return self.report_generator.generate_monthly_report()
            else:
                return ""
                
        except Exception as e:
            logging.error(f"为调度器生成{report_type}报告失败: {str(e)}")
            return ""
    
    def on_auto_submit_triggered(self, report_type: str, report_content: str):
        """自动提交触发处理"""
        try:
            logging.info(f"自动提交触发: {report_type}")
            
            if self.system_tray:
                self.system_tray.show_auto_submit_message(report_type, report_content)
            
        except Exception as e:
            logging.error(f"自动提交处理失败: {str(e)}")
    
    def show_main_window(self):
        """显示主窗口"""
        if self.report_window:
            self.report_window.show()
            self.report_window.raise_()
            self.report_window.activateWindow()
    
    def quit_application(self):
        """退出应用程序"""
        try:
            logging.info("正在退出应用程序...")
            
            # 停止定时器
            if self.timer_manager:
                self.timer_manager.stop_all_timers()
            
            # 停止飞书调度器
            if self.feishu_scheduler:
                self.feishu_scheduler.stop()
                logging.info("飞书调度器已停止")
            
            # 保存配置
            if self.config_manager:
                self.config_manager.save_config()
            
            # 隐藏系统托盘
            if self.system_tray:
                self.system_tray.hide()
            
            # 关闭所有窗口
            if self.work_log_window:
                self.work_log_window.close()
            if self.report_window:
                self.report_window.close()
            if self.settings_window:
                self.settings_window.close()
            if self.quick_add_button:
                self.quick_add_button.close()
            
            # 释放单实例锁
            if self.single_instance:
                self.single_instance.release_lock()
                logging.info("单实例锁已释放")
            
            # 退出应用程序
            if self.app:
                self.app.quit()
            
            logging.info("应用程序已退出")
            
        except Exception as e:
            logging.error(f"退出应用程序时出错: {str(e)}")
    
    def run(self):
        """运行应用程序"""
        try:
            # 检查是否启动时最小化
            settings = self.config_manager.get_settings()
            start_minimized = settings.get("start_minimized", False)
            
            if not start_minimized:
                self.show_main_window()
            
            # 显示系统托盘
            if self.system_tray:
                self.system_tray.show()
            
            # 显示快速添加按钮（根据设置）
            if self.quick_add_button:
                # 检查是否启用快速添加按钮
                quick_add_button_enabled = settings.get("quick_add_button", True)
                if quick_add_button_enabled:
                    self.quick_add_button.show()
                else:
                    self.quick_add_button.hide()
            
            # 启动定时器
            if self.timer_manager:
                self.timer_manager.start_all_timers()
            
            # 启动飞书调度器
            if self.feishu_scheduler:
                if self.feishu_scheduler.start():
                    logging.info("飞书自动提交调度器已启动")
                else:
                    logging.warning("飞书自动提交调度器启动失败")
            
            logging.info("应用程序启动完成")
            
            # 运行应用程序主循环
            return self.app.exec_()
            
        except Exception as e:
            logging.error(f"应用程序运行失败: {str(e)}")
            QMessageBox.critical(
                None, "运行错误", 
                f"应用程序运行失败：{str(e)}"
            )
            return 1


def check_environment():
    """检查运行环境"""
    try:
        # 检查Python版本
        if sys.version_info < (3, 6):
            print("错误: 需要Python 3.6或更高版本")
            return False
        
        # 检查必要的目录
        required_dirs = ["data", "logs", "backup"]
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print(f"创建目录: {dir_name}")
        
        # 检查配置文件
        if not os.path.exists("config.json"):
            print("警告: 配置文件不存在，将使用默认配置")
        
        # 检查环境变量文件
        if not os.path.exists(".env"):
            print("警告: .env文件不存在，某些功能可能无法正常工作")
            if os.path.exists(".env.example"):
                print("提示: 请复制.env.example为.env并配置相关参数")
        
        return True
        
    except Exception as e:
        print(f"环境检查失败: {str(e)}")
        return False


def main():
    """主函数"""
    try:
        print("=" * 50)
        print("🐂 牛马日报助手 v1.0.0")
        print("智能工作日报管理工具")
        print("=" * 50)
        
        # 检查运行环境
        if not check_environment():
            print("环境检查失败，程序退出")
            return 1
        
        print("环境检查通过，正在启动应用程序...")
        
        # 创建应用程序管理器
        app_manager = ApplicationManager()
        
        # 运行应用程序
        exit_code = app_manager.run()
        
        print("应用程序已退出")
        return exit_code
        
    except KeyboardInterrupt:
        print("\n用户中断，程序退出")
        return 0
    except Exception as e:
        print(f"程序运行失败: {str(e)}")
        logging.error(f"程序运行失败: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)