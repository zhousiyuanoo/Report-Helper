# Report Helper 项目 Makefile
# 提供常用的开发和部署命令

.PHONY: help install install-dev test test-cov lint format clean build run setup pre-commit

# 默认目标
help:
	@echo "Report Helper 项目管理命令:"
	@echo ""
	@echo "安装相关:"
	@echo "  install      - 安装项目依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  setup        - 初始化开发环境"
	@echo ""
	@echo "代码质量:"
	@echo "  lint         - 运行代码检查"
	@echo "  format       - 格式化代码"
	@echo "  pre-commit   - 安装 pre-commit 钩子"
	@echo ""
	@echo "测试相关:"
	@echo "  test         - 运行测试"
	@echo "  test-cov     - 运行测试并生成覆盖率报告"
	@echo ""
	@echo "构建和运行:"
	@echo "  build        - 构建项目"
	@echo "  run          - 运行应用程序"
	@echo "  clean        - 清理构建文件"

# 安装项目依赖
install:
	pip install -r requirements.txt

# 安装开发依赖
install-dev:
	pip install -e .[dev]
	pip install pre-commit

# 初始化开发环境
setup: install-dev pre-commit
	@echo "开发环境初始化完成!"

# 安装 pre-commit 钩子
pre-commit:
	pre-commit install
	pre-commit install --hook-type commit-msg

# 代码格式化
format:
	black src/ tests/
	isort src/ tests/

# 代码检查
lint:
	flake8 src/ tests/
	mypy src/
	bandit -r src/
	pydocstyle src/

# 运行测试
test:
	pytest tests/ -v

# 运行测试并生成覆盖率报告
test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# 构建项目
build: clean
	python -m build

# 运行应用程序
run:
	python src/main.py

# 清理构建文件
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# 发布到 PyPI (测试)
upload-test: build
	twine upload --repository testpypi dist/*

# 发布到 PyPI (正式)
upload: build
	twine upload dist/*

# 检查包的完整性
check:
	twine check dist/*

# 生成依赖文件
freeze:
	pip freeze > requirements.txt

# 更新依赖
update:
	pip install --upgrade -r requirements.txt