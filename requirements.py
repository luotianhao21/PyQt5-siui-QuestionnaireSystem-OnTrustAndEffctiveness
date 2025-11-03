# 项目所需库安装
import subprocess
import os
import sys

def install_package(package):
    """使用 pip 安装指定的 Python 包"""

def logger(str):
    """日志记录"""
    print(f"[Python包 | 安装器] {str}")

class Installer:
    def __init__(self):
        self.normal_package = []     # 常规包
        self.http_packages = []      # 下载包

    def add_normal_package(self, package: str):
        self.normal_package.append(package)

    def add_http_package(self, url: str):
        self.http_packages.append(url)
    
    def add_package(self, package: str):
        if package.startswith("http://") or package.startswith("https://"):
            self.add_http_package(package)
        else:
            self.add_normal_package(package)

    def add_packages(self, packages: list[str]):
        for package in packages:
            self.add_package(package)
        
    def install_normal_packages(self):
        for package in self.normal_package:
            logger(f"开始安装常规包 {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    def install_http_packages(self):
        # 查看是否安装有requests库
        try:
            import requests
        except ImportError:
            logger("正在安装requests库...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            import requests
        for url in self.http_packages:
            logger(f"开始下载 {url} 并安装...")
            file_name = os.path.basename(url)
            r = requests.get(url)

            with open(file_name, "wb") as f:
                f.write(r.content)
            # 解压文件
            subprocess.check_call([sys.executable, "-m", "pip", "install", file_name])
            os.remove(file_name)

    def install_packages(self):
        self.install_normal_packages()
        self.install_http_packages()

# 需要安装的包列表
packages = [
    "PyQt5",
    "pandas",
    "numpy",
    "scipy",
    "scikit-learn",
    "pingouin",
    "factor-analyzer",
    "https://github.com/ChinaIceF/PyQt-SiliconUI/archive/refs/heads/main.zip",
]

if __name__ == "__main__":
    installer = Installer()
    installer.add_packages(packages)
    installer.install_packages()