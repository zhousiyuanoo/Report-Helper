# 牛马日报助手 (Report Helper)

智能工作日报管理工具，支持AI生成、飞书自动提交等功能。

## 项目结构

```
Report-Helper/
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── main.py            # 主程序入口
│   ├── config_manager.py  # 配置管理
│   ├── work_log_window.py # 工作日志窗口
│   ├── report_window.py   # 报告窗口
│   ├── settings_window.py # 设置窗口
│   ├── ai_generator.py    # AI生成器
│   ├── feishu_client.py   # 飞书客户端
│   ├── feishu_scheduler.py # 飞书调度器
│   ├── system_tray.py     # 系统托盘
│   ├── timer_manager.py   # 定时器管理
│   ├── quick_add_button.py # 快速添加按钮
│   └── report_generator.py # 报告生成器
├── tests/                  # 测试文件
│   ├── __init__.py
│   └── test_config_manager.py
├── resources/              # 资源文件
│   ├── icon.svg
│   └── niuma.svg
├── docs/                   # 文档目录
├── scripts/                # 脚本文件
├── data/                   # 数据目录
├── logs/                   # 日志目录
├── backup/                 # 备份目录
├── .github/workflows/      # GitHub Actions
├── run.py                  # 启动脚本
├── setup.py               # 安装脚本
├── pyproject.toml         # 项目配置
├── requirements.txt       # 依赖列表
├── pytest.ini            # 测试配置
├── tox.ini               # 多环境测试
├── Makefile              # 构建脚本
├── .gitignore            # Git忽略文件
├── .editorconfig         # 编辑器配置
├── .pre-commit-config.yaml # 预提交钩子
└── LICENSE               # 许可证
```

## 快速开始

### 运行应用程序

```bash
# 使用启动脚本（推荐）
python run.py

# 或者直接运行
python -m src.main
```

### 开发环境设置

```bash
# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest

# 代码格式化
black src/ tests/

# 代码检查
flake8 src/ tests/
```

### 使用 Makefile（推荐）

```bash
# 安装依赖
make install

# 运行应用
make run

# 运行测试
make test

# 代码检查和格式化
make lint
make format

# 构建项目
make build

# 查看所有可用命令
make help
```

## 功能特性

- 📝 智能工作日志记录
- 🤖 AI驱动的日报生成
- 📤 飞书自动提交
- ⏰ 定时提醒功能
- 🎨 现代化UI界面
- 🔧 灵活的配置管理
- 📊 数据备份与恢复

## 配置说明

应用程序的配置文件位于 `config.json`，首次运行会自动创建默认配置。

详细的配置说明请参考 `docs/` 目录下的文档。

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。