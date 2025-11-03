import os
from typing import Union
from PyQt5.QtGui import QFont
from siui.core import GlobalFont
from siui.gui import SiFont

# 获取当前文件所在目录
root = os.path.dirname(os.path.abspath(__file__))

class NormalFont:
    """管理常规字体家族的类"""
    def __init__(self):
        self.normal_font = SiFont.tokenized(GlobalFont.S_NORMAL)

    def get_normal_font(self, size: Union[int, float] = 14, weight: int = 50, italic: bool = False):
        return_font = QFont(self.normal_font.family(), size, weight, italic)
        return_font.setBold(True)
        return return_font


class vivoSans:
    """管理vivo-sans字体家族的类"""
    
    # 字体权重常量
    BOLD_WEIGHT = QFont.Weight.Bold
    REGULAR_WEIGHT = QFont.Weight.Normal 
    LIGHT_WEIGHT = QFont.Weight.Light 
    MEDIUM_WEIGHT = QFont.Weight.Medium 
    THIN_WEIGHT = QFont.Weight.Thin
    
    def __init__(self):
        """初始化字体路径"""
        self.root = os.path.join(root, "vivo-sans")  # vivoSans字体所在目录
    
    def bold(self, size: Union[int, float] = 14, weight: int = BOLD_WEIGHT, italic: bool = False) -> QFont:
        """获取粗体字体"""
        return QFont(os.path.join(self.root, "vivoSans-Bold.ttf"), size, weight, italic)
    
    def regular(self, size: Union[int, float] = 14, weight: int = REGULAR_WEIGHT, italic: bool = False) -> QFont:
        """获取常规字体""" 
        return QFont(os.path.join(self.root, "vivoSans-Regular.ttf"), size, weight, italic)
    
    def light(self, size: Union[int, float] = 14, weight: int = LIGHT_WEIGHT, italic: bool = False) -> QFont:
        """获取细体字体"""
        return QFont(os.path.join(self.root, "vivoSans-Light.ttf"), size, weight, italic)
    
    def medium(self, size: Union[int, float] = 14, weight: int = MEDIUM_WEIGHT, italic: bool = False) -> QFont:
        """获取中等字体"""
        return QFont(os.path.join(self.root, "vivoSans-Medium.ttf"), size, weight, italic)
    
    def thin(self, size: Union[int, float] = 14, weight: int = THIN_WEIGHT, italic: bool = False) -> QFont:
        """获取极细字体"""
        return QFont(os.path.join(self.root, "vivoSans-Thin.ttf"), size, weight, italic)


# 单例实例
normal_font = NormalFont()
vivo_sans = vivoSans()