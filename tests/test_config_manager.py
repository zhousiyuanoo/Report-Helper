# -*- coding: utf-8 -*-
"""
ConfigManager 测试模块

测试配置管理器的功能。
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock

# 添加src目录到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """ConfigManager 测试类"""
    
    def setUp(self):
        """测试前的设置"""
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.test_dir, "test_config.json")
        
        # 创建测试配置文件
        test_config = {
            "settings": {
                "reminder_enabled": True,
                "reminder_interval": 30,
                "auto_submit_enabled": False
            },
            "ai_config": {
                "enabled": False,
                "api_key": "",
                "model": "gpt-3.5-turbo"
            }
        }
        
        with open(self.test_config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """测试后的清理"""
        # 清理临时文件
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        os.rmdir(self.test_dir)
    
    @patch('config_manager.os.path.exists')
    def test_init_with_existing_config(self, mock_exists):
        """测试使用现有配置文件初始化"""
        mock_exists.return_value = True
        
        with patch('config_manager.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                "settings": {"test": "value"},
                "ai_config": {"enabled": False}
            })
            
            config_manager = ConfigManager(self.test_config_file)
            
            self.assertIsNotNone(config_manager.config)
            self.assertEqual(config_manager.get_settings().get("test"), "value")
    
    def test_get_settings(self):
        """测试获取设置"""
        config_manager = ConfigManager(self.test_config_file)
        settings = config_manager.get_settings()
        
        self.assertIsInstance(settings, dict)
        self.assertIn("reminder_enabled", settings)
        self.assertTrue(settings["reminder_enabled"])
    
    def test_update_settings(self):
        """测试更新设置"""
        config_manager = ConfigManager(self.test_config_file)
        
        new_settings = {
            "reminder_enabled": False,
            "reminder_interval": 60,
            "new_setting": "test_value"
        }
        
        config_manager.update_settings(new_settings)
        updated_settings = config_manager.get_settings()
        
        self.assertFalse(updated_settings["reminder_enabled"])
        self.assertEqual(updated_settings["reminder_interval"], 60)
        self.assertEqual(updated_settings["new_setting"], "test_value")
    
    def test_get_ai_config(self):
        """测试获取AI配置"""
        config_manager = ConfigManager(self.test_config_file)
        ai_config = config_manager.get_ai_config()
        
        self.assertIsInstance(ai_config, dict)
        self.assertIn("enabled", ai_config)
        self.assertFalse(ai_config["enabled"])
    
    def test_update_ai_config(self):
        """测试更新AI配置"""
        config_manager = ConfigManager(self.test_config_file)
        
        new_ai_config = {
            "enabled": True,
            "api_key": "test_key",
            "model": "gpt-4"
        }
        
        config_manager.update_ai_config(new_ai_config)
        updated_ai_config = config_manager.get_ai_config()
        
        self.assertTrue(updated_ai_config["enabled"])
        self.assertEqual(updated_ai_config["api_key"], "test_key")
        self.assertEqual(updated_ai_config["model"], "gpt-4")
    
    def test_save_config(self):
        """测试保存配置"""
        config_manager = ConfigManager(self.test_config_file)
        
        # 修改配置
        config_manager.update_settings({"test_save": "saved_value"})
        
        # 保存配置
        config_manager.save_config()
        
        # 重新加载配置验证保存是否成功
        new_config_manager = ConfigManager(self.test_config_file)
        settings = new_config_manager.get_settings()
        
        self.assertEqual(settings["test_save"], "saved_value")
    
    @patch('config_manager.logging')
    def test_error_handling(self, mock_logging):
        """测试错误处理"""
        # 测试无效的配置文件路径
        invalid_path = "/invalid/path/config.json"
        
        with patch('config_manager.os.path.exists', return_value=False):
            config_manager = ConfigManager(invalid_path)
            
            # 应该创建默认配置
            self.assertIsNotNone(config_manager.config)
            self.assertIn("settings", config_manager.config)
            self.assertIn("ai_config", config_manager.config)


if __name__ == '__main__':
    unittest.main()