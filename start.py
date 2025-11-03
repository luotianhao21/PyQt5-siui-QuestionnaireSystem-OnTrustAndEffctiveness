import sys
import time
import os
import traceback

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from ui import MySiliconApp

import siui
from siui.core import SiGlobal

def main():
    app = QApplication(sys.argv)
    window = MySiliconApp()
    window.show()

    # 创建计时器
    timer = QTimer(window)

    return app.exec_()

if __name__ == '__main__':
    exit_code = 0
    try:
        exit_code = main()
    except Exception:
        traceback.print_exc()
        exit_code = 1
    '''finally:
        try:
            if os.name == 'nt':
                os.system('pause')  # Windows 下等待按键
            else:
                input('按回车键退出...')  # 其它平台回车退出
        except Exception:
            pass'''
    sys.exit(exit_code)