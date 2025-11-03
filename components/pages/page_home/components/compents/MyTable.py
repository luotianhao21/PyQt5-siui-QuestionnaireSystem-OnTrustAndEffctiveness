from siui.components.widgets.table import SiTableView

class MyTable(SiTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_writed = False # 是否已经写入数据
        self.data_lists = [] # 数据列表

    def init_Rows(self):
        # 添加完列后调用，初始化第一行
        _new_row = []
        for i in range(0, len(self.columnNames())):
            _new_row.append("")
        self.addRow(widgets=None, data=_new_row, is_init=True)

    def addRow(self, widgets: list = None, data: list = None, is_init: bool = False):
        # 重写以达到初始化时为空
        self.data_lists.append(data)
        super().addRow(widgets=widgets, data=data)
        if not is_init and not self.is_writed:
            self.is_writed = True
            self.deleteRow(0)

    def deleteRow(self, row_index: int):
        '''
        删除指定行
        '''
        # 直接清空
        for row_ in self.rows_[:]:
            self.container_.removeWidget(row_)
            self.rows_.remove(row_)
        # 删除self.data_lists中第row_index的数据
        self.data_lists.pop(row_index)
        if len(self.data_lists) == 0:
            self.init_Rows()
        else:
            for data in self.data_lists:
                super().addRow(data=data)