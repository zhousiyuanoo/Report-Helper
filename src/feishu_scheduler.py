#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书自动提交调度器
负责定时检查和自动提交汇报到飞书
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional
from feishu_client import FeishuClient
from config_manager import ConfigManager


class FeishuScheduler:
    """飞书自动提交调度器"""
    
    def __init__(self, config_manager: ConfigManager, report_generator_func: Callable):
        """
        初始化调度器
        
        Args:
            config_manager: 配置管理器
            report_generator_func: 报告生成函数，接受report_type参数
        """
        self.config_manager = config_manager
        self.report_generator_func = report_generator_func
        self.feishu_client = None
        self.scheduler_thread = None
        self.running = False
        self.check_interval = 300  # 5分钟检查一次
        self.last_check_time = None
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _init_feishu_client(self) -> bool:
        """初始化飞书客户端"""
        try:
            config = self.config_manager.get_config()
            feishu_config = config.get("feishu_config", {})
            
            if not feishu_config.get("enabled", False):
                self.logger.info("飞书集成未启用")
                return False
            
            app_id = feishu_config.get("app_id")
            app_secret = feishu_config.get("app_secret")
            
            if not app_id or not app_secret:
                self.logger.error("飞书配置不完整，缺少app_id或app_secret")
                return False
            
            self.feishu_client = FeishuClient(app_id, app_secret)
            
            # 测试连接
            test_result = self.feishu_client.test_connection()
            if test_result["success"]:
                self.logger.info("飞书客户端初始化成功")
                return True
            else:
                self.logger.error(f"飞书连接测试失败: {test_result['message']}")
                return False
                
        except Exception as e:
            self.logger.error(f"初始化飞书客户端失败: {e}")
            return False
    
    def _should_check_now(self) -> bool:
        """判断是否应该进行检查"""
        now = datetime.now()
        
        # 如果是第一次检查
        if self.last_check_time is None:
            return True
        
        # 检查时间间隔
        if (now - self.last_check_time).total_seconds() >= self.check_interval:
            return True
        
        return False
    
    def _check_and_submit_reports(self) -> None:
        """检查并提交汇报"""
        try:
            if not self.feishu_client:
                if not self._init_feishu_client():
                    return
            
            config = self.config_manager.get_config()
            feishu_config = config.get("feishu_config", {})
            
            # 检查是否启用自动汇报
            if not feishu_config.get("auto_report_enabled", False):
                return
            
            chat_id = feishu_config.get("chat_id")
            if not chat_id:
                self.logger.error("未配置飞书群聊ID")
                return
            
            # 执行自动提交检查
            results = self.feishu_client.check_and_auto_submit(
                chat_id, self.report_generator_func, feishu_config
            )
            
            # 记录提交结果
            for result in results:
                if result["success"]:
                    self.logger.info(f"{result['type']}自动提交成功")
                    self._update_submit_status(result["type"], True)
                else:
                    self.logger.error(f"{result['type']}自动提交失败: {result['message']}")
            
            self.last_check_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"检查和提交汇报时发生异常: {e}")
    
    def _update_submit_status(self, report_type: str, success: bool) -> None:
        """更新提交状态"""
        try:
            config = self.config_manager.get_config()
            submit_status = config.get("submit_status", {})
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            if report_type == "日报":
                submit_status["last_daily_submit"] = today
            elif report_type == "周报":
                submit_status["last_weekly_submit"] = today
            elif report_type == "月报":
                submit_status["last_monthly_submit"] = today
            
            if success:
                submit_status["last_submit_date"] = today
                submit_status["submit_count"] = submit_status.get("submit_count", 0) + 1
            
            config["submit_status"] = submit_status
            self.config_manager.save_config(config)
            
        except Exception as e:
            self.logger.error(f"更新提交状态失败: {e}")
    
    def _scheduler_loop(self) -> None:
        """调度器主循环"""
        self.logger.info("飞书自动提交调度器已启动")
        
        while self.running:
            try:
                if self._should_check_now():
                    self._check_and_submit_reports()
                
                # 休眠一段时间再检查
                time.sleep(60)  # 每分钟检查一次是否需要执行
                
            except Exception as e:
                self.logger.error(f"调度器循环中发生异常: {e}")
                time.sleep(60)
        
        self.logger.info("飞书自动提交调度器已停止")
    
    def start(self) -> bool:
        """启动调度器"""
        if self.running:
            self.logger.warning("调度器已在运行中")
            return False
        
        # 初始化飞书客户端
        if not self._init_feishu_client():
            return False
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        return True
    
    def stop(self) -> None:
        """停止调度器"""
        if not self.running:
            return
        
        self.running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("调度器停止完成")
    
    def force_check(self) -> Dict[str, Any]:
        """强制执行一次检查"""
        result = {
            "success": False,
            "message": "",
            "results": []
        }
        
        try:
            if not self.feishu_client:
                if not self._init_feishu_client():
                    result["message"] = "飞书客户端初始化失败"
                    return result
            
            config = self.config_manager.get_config()
            feishu_config = config.get("feishu_config", {})
            chat_id = feishu_config.get("chat_id")
            
            if not chat_id:
                result["message"] = "未配置飞书群聊ID"
                return result
            
            # 强制检查所有类型的汇报
            submit_results = self.feishu_client.check_and_auto_submit(
                chat_id, self.report_generator_func, feishu_config
            )
            
            result["success"] = True
            result["results"] = submit_results
            result["message"] = f"检查完成，处理了{len(submit_results)}个汇报"
            
            # 更新提交状态
            for submit_result in submit_results:
                if submit_result["success"]:
                    self._update_submit_status(submit_result["type"], True)
            
        except Exception as e:
            result["message"] = f"强制检查失败: {str(e)}"
        
        return result
    
    def get_next_deadlines(self) -> Dict[str, Any]:
        """获取下次汇报截止时间信息"""
        if not self.feishu_client:
            return {"error": "飞书客户端未初始化"}
        
        return {
            "daily": self.feishu_client.get_report_deadlines("daily"),
            "weekly": self.feishu_client.get_report_deadlines("weekly"),
            "monthly": self.feishu_client.get_report_deadlines("monthly")
        }
    
    def test_report_submission(self, report_type: str = "日报") -> Dict[str, Any]:
        """测试汇报提交功能"""
        result = {
            "success": False,
            "message": ""
        }
        
        try:
            if not self.feishu_client:
                if not self._init_feishu_client():
                    result["message"] = "飞书客户端初始化失败"
                    return result
            
            config = self.config_manager.get_config()
            feishu_config = config.get("feishu_config", {})
            chat_id = feishu_config.get("chat_id")
            
            if not chat_id:
                result["message"] = "未配置飞书群聊ID"
                return result
            
            # 生成测试报告
            test_content = f"这是一个{report_type}测试报告，发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 发送测试报告
            if self.feishu_client.send_report(
                chat_id, test_content, 
                "card", 
                report_type
            ):
                result["success"] = True
                result["message"] = f"{report_type}测试发送成功"
            else:
                result["message"] = f"{report_type}测试发送失败"
            
        except Exception as e:
            result["message"] = f"测试失败: {str(e)}"
        
        return result