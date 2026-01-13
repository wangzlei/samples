# Django Sample App - Debug Setup Instructions

## Overview
This setup allows you to step-by-step debug the Django sample app with OpenTelemetry instrumentation using VSCode.

## Debug Configurations Available

### 1. "Debug Django Sample App"
- **Purpose**: Standard debugging mode
- **Entry Point**: Starts debugging from the beginning of app.py
- **Port**: 8000
- **Usage**: Good for debugging the OpenTelemetry setup and instrumentation

### 2. "Debug Django Sample App (with entry stop)"
- **Purpose**: Debugging with immediate breakpoint at program entry
- **Entry Point**: Stops at the very first line of app.py
- **Port**: 8000
- **Usage**: Best for step-by-step debugging from the beginning

## Available Test Endpoints

Once the Django app is running, you can test these endpoints:

- `http://127.0.0.1:8000/` - Simple hello view with AWS request
- `http://127.0.0.1:8000/test/` - Test view with tracing
- `http://127.0.0.1:8000/slow/` - View with artificial delay
- `http://127.0.0.1:8000/param/123/` - Parameterized view
- `http://127.0.0.1:8000/class/` - Class-based view
- `http://127.0.0.1:8000/template/` - Template view with AWS S3/DynamoDB calls
- `http://127.0.0.1:8000/error/` - View that raises an exception
- `http://127.0.0.1:8000/debug/` - Debug middleware execution

## How to Start Debugging

1. **Set Breakpoints**: 
   - Open any file you want to debug (e.g., `samples/django/views.py`)
   - Click in the left margin to set breakpoints

2. **Start Debug Session**:
   - Press `F5` or go to Run → Start Debugging
   - Select "Debug Django Sample App" or "Debug Django Sample App (with entry stop)"

3. **Test Your Breakpoints**:
   - Once the server starts, open a browser or use curl to hit the endpoints
   - The debugger will stop at your breakpoints

## Key Files for Debugging

- **`app.py`**: Main entry point with OpenTelemetry setup
- **`views.py`**: Contains various test views
- **`urls.py`**: URL routing configuration
- **OpenTelemetry components**:
  - `aws-opentelemetry-distro/src/amazon/opentelemetry/distro/code_correlation/code_attributes_span_processor.py`
  - `aws-opentelemetry-distro/src/amazon/opentelemetry/distro/aws_opentelemetry_configurator.py`

## Debugging Tips

1. **Step Through OpenTelemetry Setup**: Set breakpoints in `app.py` to see how tracing is initialized
2. **Debug Request Processing**: Set breakpoints in views to see how spans are created
3. **Trace AWS SDK Calls**: The app includes boto3 calls that will be automatically instrumented
4. **Check Span Processors**: Debug the CodeAttributesSpanProcessor to see code correlation in action

## Python Environment

所有调试配置都明确使用samples目录下的虚拟环境：
```json
"python": "${workspaceFolder}/samples/venv/bin/python"
```

**变量说明：**
- `${workspaceFolder}` 是VSCode内置变量，代表当前工作区根目录
- 在这个项目中，`${workspaceFolder}` 解析为：`/Volumes/workplace/extension/aws-otel-python-instrumentation`
- 因此实际的Python路径是：`/Volumes/workplace/extension/aws-otel-python-instrumentation/samples/venv/bin/python`

这确保了调试时使用的是安装了所有依赖包的samples虚拟环境，包括：
- Django 5.2.7
- AWS OpenTelemetry Distro 0.12.1.dev0 (开发模式安装)
- 所有OpenTelemetry instrumentation包
- boto3, requests等依赖

## Environment Variables Set

- `PYTHONPATH`: Includes both the distro source and workspace root
- `DJANGO_SETTINGS_MODULE`: Points to mysite.settings
- `justMyCode`: Set to false to debug into OpenTelemetry libraries
- `python`: Explicitly set to `${workspaceFolder}/samples/venv/bin/python`

## Next Steps

1. Start with the "Debug Django Sample App (with entry stop)" configuration
2. Step through the OpenTelemetry initialization
3. Set breakpoints in views.py and test endpoints
4. Examine how spans are created and processed
