from siui.components.widgets.navigation_bar import SiNavigationBarH

class MyNavigationBarH(SiNavigationBarH):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root_container = None # 根容器
        self.item_widgets = [] # 每个导航对应的组件
        self.current_showing_widgets = [] # 当前显示的组件

    def setRootContainer(self, container):
        self.root_container = container

    def addItems(self, items: list):
        for item in items:
            self.addItem(item)

    def addItem(self, name: str, side="left"):
        super().addItem(name, side)
        self.item_widgets.append([]) # 为每个导航项添加一个空的组件列表

    def addItemWidget(self, index: int, widget):
        widget.setVisible(False) # 初始不可见
        if 0 <= index < len(self.item_widgets):
            self.item_widgets[index].append(widget)

    def setEnabledIndexOf(self, index: int):
        for widget in self.current_showing_widgets:
            # 先移除当前显示的组件
            self.root_container.removeWidget(widget)
            widget.setVisible(False)
            self.current_showing_widgets.remove(widget)
        for widget in self.item_widgets[index]:
            # 再添加新的组件
            self.root_container.addWidget(widget)
            widget.setVisible(True)
            self.current_showing_widgets.append(widget)
        self.setCurrentIndex(index) # 设置当前导航项

    def _on_button_clicked(self, index):
        if self.root_container is None:
            raise ValueError("根容器未设置，请使用 setRootContainer 方法设置")
        
        self.setEnabledIndexOf(index) # 设置当前导航项的组件显示