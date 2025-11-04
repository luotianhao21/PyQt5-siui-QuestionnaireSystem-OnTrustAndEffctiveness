from siui.components import SiLabel, SiPixLabel
from siui.components.widgets.abstracts.table import ABCSiTabelManager, SiRow
from siui.core import GlobalFont, Si, SiColor
from siui.gui import SiFont

# 卡方表格管理类
class ButtonCardK2Table(ABCSiTabelManager):
    def _value_read_parser(self, row_index, col_index):
        return self.parent().getRowWidget(row_index)[col_index].text()

    def _value_write_parser(self, row_index, col_index, value):
        # 重写该方法以实现对表格数据的写入
        widget = self.parent().getRowWidget(row_index)[col_index]
        widget.setTextColor(self.parent().getColor(SiColor.TEXT_B))
        widget.setFont(SiFont.tokenized(GlobalFont.S_BOLD))
        widget.setText(value)

    def _widget_creator(self, col_index):
        # 重写该方法以实现对表格控件的创建
        label = SiLabel(self.parent())
        label.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)
        return label

    def on_header_created(self, header: SiRow):
        for name in self.parent().column_names:
            new_label = SiLabel(self.parent())
            new_label.setFont(SiFont.tokenized(GlobalFont.S_BOLD))
            new_label.setTextColor(self.parent().getColor(SiColor.TEXT_D))
            new_label.setText(name)
            new_label.adjustSize()
            header.container().addWidget(new_label)

        header.container().arrangeWidgets()