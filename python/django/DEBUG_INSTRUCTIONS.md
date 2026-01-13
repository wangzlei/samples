# Django Sample Debugging Setup

## VSCode 调试配置已完成

### 1. 打开项目
```bash
# 在 VSCode 中打开 samples/django 目录
code samples/django/
```

### 2. 调试配置
已创建两个调试配置：

#### **Django Debug Server** (推荐)
- 使用 `app.py` 启动，包含所有 OpenTelemetry instrumentation
- 支持热重载和断点调试
- 包含 SQLite3 数据库 instrumentation

#### **Django Debug Server (Development)**  
- 使用标准 `manage.py` 启动
- 不包含 OpenTelemetry instrumentation

### 3. 设置断点并开始调试

1. **在 `views.py` 中设置断点**：
   - 打开 `samples/django/views.py`
   - 在第 275 行 `objs = list(qs)` 上设置断点
   - 这行代码会触发数据库查询并生成 client span

2. **启动调试器**：
   - 按 `F5` 或点击 "Run and Debug" 
   - 选择 "Django Debug Server"
   - 等待服务器启动 (显示 "Starting development server at http://127.0.0.1:8000/")

3. **触发断点**：
   ```bash
   curl http://127.0.0.1:8000/orm/
   ```

### 4. 调试要点

**关键调试位置：**
- `views.py:275` - `objs = list(qs)` (用户代码，触发数据库查询)
- Django 数据库内部代码 - SQLite3 instrumentation 会生成 client spans

**观察内容：**
- HTTP Server Span 的 code attributes 指向 views.py
- Database Client Span 的 code attributes 指向 Django 内部代码
- 这重现了 pet clinic billing service 的 code attributes 行为

### 5. Code Attributes Processor 调试

如果要调试 CodeAttributesSpanProcessor：
1. 在 `aws-opentelemetry-distro/src/amazon/opentelemetry/distro/code_correlation/code_attributes_span_processor.py` 设置断点
2. 特别关注 `_capture_code_attributes` 方法
3. 观察 stack frame 遍历和 user code 检测逻辑

### 6. 环境配置
- Python 解释器: `samples/venv/bin/python`
- Django 设置: `mysite.settings`
- 自动加载: 已启用
- justMyCode: false (可以调试库代码)

### 7. 故障排除

如果调试器无法启动：
1. 确认 venv 已激活且包含所需依赖
2. 检查 `samples/venv/bin/python` 路径是否正确
3. 确保在 `samples/django` 目录中打开 VSCode

如果断点不生效：
- 确保选择了正确的调试配置 "Django Debug Server"
- 检查 Python 解释器是否设置为 `../venv/bin/python`
