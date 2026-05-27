# Neo Legend CI/CD 配置指南

## 📋 流水线概览

本项目已配置 **GitHub Actions** 自动化 CI/CD 流水线，包含以下 4 个阶段：

```
┌─────────────┐    ┌─────────────┐    ┌──────────────┐
│   🔍 Lint    │ -> │  🧪 Test    │ -> │ 📦 Build     │
│ (代码质量)    │    │ (测试套件)   │    │ (构建验证)    │
└─────────────┘    └─────────────┘    └──────────────┘
                         │
                         v
                 ┌──────────────┐
                 │ 🌐 Deploy     │
                 │ (覆盖率报告)   │
                 └──────────────┘
```

---

## 🚀 触发条件

### 自动触发
- **Push 到分支**: `main`, `develop`
- **Pull Request**: 目标 `main` 分支

### 手动触发
在 GitHub 仓库页面：
1. 进入 **Actions** 标签页
2. 选择 **"Neo Legend CI Pipeline"**
3. 点击 **"Run workflow"** 按钮

---

## 🔧 各 Job 详细说明

### 1️⃣ **Job: Code Quality (Ruff)**

**目的**: 检查代码风格和潜在问题

**检查内容**:
- Ruff linter（Python 代码静态分析）
- 代码格式化检查（Ruff formatter）

**本地运行**:
```bash
# 安装 pre-commit hooks（推荐）
pip install pre-commit
pre-commit install

# 或者手动运行
ruff check src/ tests/
ruff format --check src/ tests/

# 自动修复问题
ruff check --fix src/ tests/
ruff format src/ tests/
```

**失败处理**: 
CI 会显示具体的错误位置和修复建议。运行上述命令自动修复大部分问题。

---

### 2️⃣ **Job: Test Suite**

**目的**: 运行全部 82 个测试用例，生成覆盖率报告

**矩阵策略**:
| Python 版本 | 用途 |
|-------------|------|
| 3.11 | 兼容性测试 |
| 3.12 | 主力版本 + 覆盖率报告 |

**生成的报告**:
- ✅ JUnit XML 格式测试结果 (`junit.xml`)
- ✅ Cobertura XML 覆盖率 (`coverage.xml`)
- ✅ HTML 可视化报告 (`htmlcov/`)

**查看覆盖率报告**:
1. 等待 CI 完成
2. 在 Actions 页面找到对应 run
3. 下载 **Artifacts** → `test-results-py3.12`
4. 解压后打开 `htmlcov/index.html`

**或者访问 GitHub Pages**（仅 main 分支）:
- URL 格式: `https://<username>.github.io/<repo-name>/`

**本地运行完整测试**:
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试 + 覆盖率
pytest tests/ \
  --cov=src/neo_legend \
  --cov-report=term-missing \
  --cov-report=html:htmlcov \
  -v

# 查看报告
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

**覆盖率阈值**: 
当前设置为 **80%**（低于此值 CI 将失败）。可在 [pyproject.toml](../pyproject.toml) 中修改：

```toml
[tool.coverage.report]
fail_under = 80  # 修改此值
```

---

### 3️⃣ **Job: Build Verification**

**目的**: 验证项目可以正确打包为分发包

**执行内容**:
1. 使用 `python -m build` 构建 sdist 和 wheel
2. 使用 `twine check` 验证包元数据完整性

**产物**: 
- 下载 Artifacts → `dist-package` 获取构建的 `.tar.gz` 和 `.whl` 文件

---

### 4️⃣ **Job: Deploy Coverage Report** (可选)

**条件**: 仅在 push 到 `main` 分支时触发

**功能**: 
将 HTML 覆盖率报告部署到 GitHub Pages

**配置步骤**:
1. 仓库 Settings → Pages
2. Source 选择 **GitHub Actions**
3. 保存后自动部署

---

## 🛠️ 本地开发工作流

### 推荐的 Git Hook 工作流

使用 **pre-commit** 在提交/推送前自动检查：

```bash
# 1. 安装 pre-commit
pip install pre-commit

# 2. 安装 hooks（只需一次）
pre-commit install
pre-commit install --hook-type pre-push  # 推送前运行测试

# 3. 正常开发...
git add .
git commit -m "feat: add new chart type"

# 提交时自动：Ruff lint + 格式化
# 推送时自动：运行测试套件
git push origin main
```

### 快速验证命令

```bash
# 完整 CI 模拟（按顺序执行）
make ci  # 如果有 Makefile

# 或手动执行
ruff check src/ tests/ && \
ruff format --check src/ tests/ && \
pytest tests/ --cov=src/neo_legend -v && \
python -m build && \
twine check dist/*
```

---

## 📊 监控和通知

### 查看历史记录
- **Actions 页面**: https://github.com/<owner>/<repo>/actions
- 每次运行都有详细日志和产物下载

### Badge 徽章（可选）

在 README.md 中添加：

```markdown
![CI Status](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/github/<owner>/<repo>/branch/main/graph/badge.svg)
```

效果:
- ![CI Status](https://img.shields.io/github/actions/workflow/status/<owner>/<repo>/ci.yml?branch=main)
- ![Coverage](https://img.shields.io/codecov/c/github/<owner>/<repo>?token=XXXXX)

---

## ⚠️ 常见问题排查

### Q1: CI 中字体警告（UserWarning: Glyph missing from font）
**原因**: 测试用例使用了 Unicode 字符（emoji/中文），系统字体不支持  
**影响**: 仅警告，不影响测试通过  
**解决**: 忽略或安装字体包（如 `fonts-noto-cjk`）

### Q2: 覆盖率低于阈值
**现象**: CI 报错 `Coverage failure...`  
**解决**:
1. 本地运行 `pytest --cov=src/neo_legend` 查看具体覆盖情况
2. 为未覆盖的代码补充测试
3. 或调整 `fail_under` 阈值（不推荐）

### Q3: Ruff 报错 "Line too long"
**现象**: E501 错误  
**解决**: 已配置忽略此项（由 formatter 处理）。如果仍然报错，运行：
```bash
ruff format src/ tests/
```

### Q4: Codecov 上传失败
**现象**: `codecov/codecov-action@v4` 步骤失败  
**解决**:
1. 确保 repo 设置中启用了 Codecov
2.或在仓库 Secrets 中添加 `CODECOV_TOKEN`
3. 或删除该 step（非必需）

---

## 🔐 权限说明

CI 流水线需要以下 GitHub Token 权限（默认已包含）:

| 权限 | 用途 |
|------|------|
| `contents: read` | Checkout 代码 |
| `pages: write` | 部署覆盖率报告（可选） |
| `id-token: write` | OIDC 认证（可选） |

---

## 📝 自定义配置

### 修改 Python 版本矩阵
编辑 [.github/workflows/ci.yml](.github/workflows/ci.yml) 第 35-36 行：

```yaml
matrix:
  python-version: ["3.11", "3.12", "3.13"]  # 添加 3.13
```

### 添加新的 lint 规则
编辑 [pyproject.toml](pyproject.toml) 的 `[tool.ruff.lint.select]` 部分。

### 调整超时时间
在 workflow 的 job 级别添加：

```yaml
test:
  timeout-minutes: 30  # 默认 360 分钟
```

---

## 🎯 下一步建议

1. ✅ **启用 Codecov** (可选): 注册 [codecov.io](https://codecov.io) 并关联仓库
2. ✅ **配置 GitHub Pages**: 用于托管覆盖率报告
3. ✅ **添加 Badge**: 在 README 显示 CI 状态
4. ✅ **设置 Branch Protection**: 要求 PR 通过 CI 才能合并

---

**最后更新**: 2026-05-26  
**维护者**: Neo Legend Team
