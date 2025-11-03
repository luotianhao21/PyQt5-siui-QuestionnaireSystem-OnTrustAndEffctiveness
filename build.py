import os
import shutil
import time
import subprocess
name = "QuestionnaireSystem"
exclude_modules = [
    "torch",
]

# 获取当前时间
start = time.localtime()

cmd_list = [
    "pyinstaller",
    "--log-level=DEBUG",
    "--noconfirm",
    "--windowed",  # 无控制台（等同于 -w）
    "-i", "./img/baqian.ico",
    "--onedir",
    "--contents-directory=internal",
    f"--name={name}",
    "./start.py",
]
# 添加要排除的模块
for m in exclude_modules:
    cmd_list += ["--exclude-module", m]

resources = [("fonts", "internal/fonts"),
             ("img", "img"),
             ("icons", "internal/icons"),
             ("json", "internal/json"),
             ("components/siui", "internal/siui")] # 需要复制的文件夹

try:
    subprocess.run(cmd_list, check=True)
except subprocess.CalledProcessError as e:
    print("打包失败：", e)
    raise

for resource in resources:
    shutil.copytree(f"./{resource[0]}", f"./dist/{name}/{resource[1]}", dirs_exist_ok=True)

shutil.rmtree("./build", ignore_errors=True)
os.remove(f"./{name}.spec")

# 打包完成，获取当前时间
end = time.localtime()
print(f"打包完成，开始时间：{start}，结束时间：{end}")
print(f"总共用时：{time.strftime('%H:%M:%S', time.gmtime(time.mktime(end) - time.mktime(start)))}")