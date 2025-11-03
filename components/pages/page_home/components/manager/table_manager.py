from siui.components import SiLabel, SiPixLabel
from siui.components.widgets.abstracts.table import ABCSiTabelManager, SiRow
from siui.core import GlobalFont, Si, SiColor
from siui.gui import SiFont

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class TableManager(ABCSiTabelManager):
    # 因子分析
    # 表格管理器
    # #0 问题序号
    # #1 \占位\
    # #2 因子 1
    # #3 因子 2
    # #4 因子 3
    # #5 因子 4
    # #6 \占位\
    # #7 共同度

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dimensions_num: int = 4 # 因子个数
        self.dimensions_col_index: list[int] = [2, 3, 4, 5] # 因子列索引

    def setDimensionsNum(self, num: int):
        self.dimensions_num = num
        self.dimensions_col_index = [2, 3, 4, 5][:num]

    def _value_read_parser(self, row_index, col_index):
        return self.parent().getRowWidget(row_index)[col_index].text()

    def _value_write_parser(self, row_index, col_index, value):
        # 重写该方法以实现对表格数据的写入
        weight = self.parent().getRowWidget(row_index)[col_index] # 获取该单元格的控件
        weight.setTextColor(self.parent().getColor(SiColor.TEXT_B))
        weight.setFont(SiFont.tokenized(GlobalFont.S_BOLD))
        if value == "nan":
            weight.setHint("无法计算，故为nan")
        if is_float(value):
            if col_index in self.dimensions_col_index:
                if abs(float(value)) > 0.4:
                    weight.setTextColor("#72BBFF")
                    weight.setHint("绝对值大于0.4，表示该因子对该问题有较大影响")
            if col_index == 3+len(self.dimensions_col_index):
                if float(value) < 0.4:
                    weight.setTextColor("#FF5959")
                    weight.setHint("共同度小于0.4，表示该问题被因子解释的程度较低")
        weight.setText(str(value)) # 设置文本

    def _widget_creator(self, col_index):
        label = SiLabel(self.parent())
        label.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        return label

    def on_header_created(self, header: SiRow):
        for name in self.parent().column_names:
            new_label = SiLabel(self.parent())
            new_label.setFont(SiFont.tokenized(GlobalFont.S_BOLD))
            new_label.setTextColor(self.parent().getColor(SiColor.TEXT_B))
            new_label.setText(name)
            if name == "因子 1" or name == "因子 2" or name == "因子 3" or name == "因子 4":
                new_label.setHint("因子载荷系数：\n    表示因子与分析项之间的关系程度，\n    绝对值大于0.4可考虑删除该因子")
            if name == "共同度":
                new_label.setHint("共同度：\n    表示可被提取的信息量，\n    例如0.5代表可提取50%的信息，通常为0.4为标准")
            new_label.adjustSize()
            header.container().addWidget(new_label)

        header.container().arrangeWidgets()

class NavigationBarTableManager(TableManager):
    # 信度分析
    # 表格管理器
    # #0 问题序号
    # #1 CITC
    # #2 alpha

    def _value_read_parser(self, row_index, col_index):
        return self.parent().getRowWidget(row_index)[col_index].text()
    
    def _value_write_parser(self, row_index, col_index, value):
        weight = self.parent().getRowWidget(row_index)[col_index] # 获取该单元格的控件
        weight.setTextColor(self.parent().getColor(SiColor.TEXT_B))
        weight.setFont(SiFont.tokenized(GlobalFont.S_BOLD))
        if value == "nan":
            weight.setTextColor("#931F1F")
            weight.setHint("该项为<strong>重复常数值</strong>，无法计算")
        if is_float(value):
            if col_index == 1:
                if float(value) >= 0.4:
                    weight.setTextColor("#89FF89")
                elif 0.2 <= float(value) < 0.4:
                    weight.setTextColor("#FAFC7D")
                elif float(value) < 0.2:
                    weight.setTextColor("#FF5959")
        weight.setText(str(value)) # 设置文本

    def _widget_creator(self, col_index):
        label = SiLabel(self.parent())
        label.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        return label

    def on_header_created(self, header: SiRow):
        for name in self.parent().column_names:
            new_label = SiLabel(self.parent())
            new_label.setFont(SiFont.tokenized(GlobalFont.S_BOLD))
            new_label.setTextColor(self.parent().getColor(SiColor.TEXT_B))
            new_label.setText(name)
            if name == "校正项总计相关性(CITC)":
                new_label.setHint("校正项总计相关性(CITC)：\n    通常大于0.4，否则可考虑删除该项")
            if name == "项已删除的α系数":
                new_label.setHint("项已删除的α系数：\n    如果该系数明显高于α系数，则可以考虑删除该项")
            new_label.adjustSize()
            header.container().addWidget(new_label)

        header.container().arrangeWidgets()