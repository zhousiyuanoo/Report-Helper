#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Helper 启动脚本

用于启动 Report Helper 应用程序的主入口点。
"""

import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

# 导入并运行主程序
if __name__ == "__main__":
    try:
        from src.main import main
        main()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保所有依赖都已正确安装")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)