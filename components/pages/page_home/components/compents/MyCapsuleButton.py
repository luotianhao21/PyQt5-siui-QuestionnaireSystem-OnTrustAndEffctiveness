from siui.components.button import (
    SiCapsuleButton # 胶囊按钮
)

class MyCapsuleButton(SiCapsuleButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.color_list = [] # 设置数值区间的颜色

    def setColorWhen(self, min_value, max_value, color):
        if min_value > max_value:
            raise ValueError("min_value must be less than or equal to max_value")
        self.color_list.append((min_value, max_value, color))

    def setValue(self, value):
        super().setValue(value)
        is_num = False
        try:
            float(value)
            is_num = True
        except ValueError:
            pass
        # 获取当前数值区间的颜色
        if is_num:
            for color_range in self.color_list:
                try:
                    int(value)
                    if color_range[0] <= int(value) <= color_range[1]:
                        self.setThemeColor(color_range[2])
                        break
                except:
                    self.setThemeColor(self.color_list[-1][2])
                    break
            return None
        self.adjustSize() # 调整大小以适应内容