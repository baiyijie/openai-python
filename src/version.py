import sys
import os
from pathlib import Path

# 1. 获取当前脚本的绝对路径
current_file = Path(__file__).resolve()

# 2. 获取项目的根目录 (当前文件的上一级目录的上一级)
# .parent 是 folder_a, .parent.parent 就是 project_root
project_root = current_file.parent

# 3. 将项目根目录添加到搜索路径中
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
# 测试调用
# data_tool.your_function()

from openai import qq

# Make sure to modify __release_datetime__ to release time when making official release.
__version__ = '2.0.0'
# default release datetime for branches under active development is set
# to be a time far-far-away-into-the-future
__release_datetime__ = '2099-09-06 00:00:00'
