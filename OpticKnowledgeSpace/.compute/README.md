# OpticKnowledgeSpace 计算环境

本目录存放知识库相关的 Python 计算环境，使用 [uv](https://docs.astral.sh/uv/) 管理。

## 环境信息

- 虚拟环境：`OpticKnowledgeSpace/.compute/.venv`
- Python 版本：3.13.14
- 包管理器：uv

## 常用命令

```bash
# 激活虚拟环境（Git Bash）
source OpticKnowledgeSpace/.compute/.venv/Scripts/activate

# 激活虚拟环境（PowerShell）
OpticKnowledgeSpace\.compute\.venv\Scripts\Activate.ps1

# 使用 uv 安装包到当前环境
uv pip install numpy

# 使用 uv 运行脚本（自动使用 .venv）
cd OpticKnowledgeSpace/.compute
uv run python script.py

# 锁定依赖
uv pip freeze > requirements.txt

# 从 requirements.txt 安装
uv pip install -r requirements.txt
```

## 已包含的示例脚本

- `scripts/prism_refraction.py`：使用 `rayoptics`/`opticalglass` 对 N-BK7 棱镜做折射-色散追迹，输出 `attachments/visuals/prism_refraction_rayoptics.png`，已嵌入 `10-concepts/dispersion.md`。

## 注意事项

- 当前 `.venv` 为基础空环境，仅含 Python 标准库。
- 后续安装依赖时建议记录到 `pyproject.toml` 或 `requirements.txt`。
- 如遇到 `SSL_CERT_DIR` 警告，可忽略；若影响包下载，再检查系统证书配置。
