"""
卡方数据储存类
1. 储存满足卡方横竖条件的数据
2. 计算卡方数据
"""

from scipy import stats  # 用于计算P值
from PyQt5.QtCore import pyqtSignal, QThread, QObject
import warnings
from scripts.database import Database, QuestionnaireScores, QuestionnaireFilterData


class K2ReturnData:
    def __init__(self, k2table: list[list[int]], chi2: float, df: int, p_value: float):
        self.K2Table: list[list[int]] = k2table
        self.chi2: float = chi2
        self.df: int = df
        self.p_value: float = p_value

    def __str__(self) -> str:
        _str: str = (f"{self.K2Table}"
                     f"卡方:{self.chi2}\n"
                     f"自由度:{self.df}\n"
                     f"p值:{self.p_value}")
        return _str

    def getShowTable(self) -> list[list]:
        show_table: list[list] = []
        for row in self.K2Table:
            row_copy = row.copy()  # 复制原始行，避免修改
            row_copy.append(sum(row_copy))  # 添加行合计
            show_table.append(row_copy)
        # 计算列合计（包括行合计列）
        column_sum_row = [sum(col) for col in zip(*show_table)]
        show_table.append(column_sum_row)
        return show_table

class K2DataSignal(QObject):
    finish: pyqtSignal = pyqtSignal(K2ReturnData)
    error: pyqtSignal = pyqtSignal(warnings.WarningMessage)

class K2DataWorker(QObject):

    signals = K2DataSignal()

    def __init__(self, k2data: 'K2Data', dimensions: list[str]):
        super().__init__()
        self.k2data = k2data
        self.database = Database()
        self.dimensions: list[str] = dimensions
        self.K2Table: list[list[int]] = [
            [0, 0],  # 优秀：[知信行合格, 知信行不合格]
            [0, 0],  # 良好：[知信行合格, 知信行不合格]
            [0, 0]  # 不合格：[知信行合格, 知信行不合格]
        ]

    def run(self):
        try:
            # 获取所有问卷分数列表
            questionnaire_scores: list[QuestionnaireScores] = []
            questionnaires = self.database.getQuestionDataByFilters(self.k2data.questionnaire_filter_data)
            for row in questionnaires:
                __id = row[0]
                questionnaire_scores.append(self.database.getQuestionnairesScores(__id))

            self.clearData()
            for questionnaire_score in questionnaire_scores:
                self.addData(
                    questionnaire_score.isDimensionsPassed(self.dimensions),
                    questionnaire_score.getHealthStatusStatus()
                )
            chi2, df, p_value = self.calculate_chi2()
            emit_data: K2ReturnData = K2ReturnData(self.K2Table, chi2, df, p_value)
            self.signals.finish.emit(emit_data)

        except Exception as e:
            # 将异常封装为 warnings.WarningMessage 并发射 error 信号
            try:
                wm = warnings.WarningMessage(str(e), Warning, "", 0)
            except Exception:
                # 兜底，构造最简单的 WarningMessage
                class _WM: pass
                wm: warnings.WarningMessage = _WM()
                wm.message = str(e)
            self.signals.error.emit(wm)

    def addData(self, _3_dimensions: bool, health_status: str) -> None:
        health_status_list: list[str] = ["优秀", "良好", "不合格"]
        if health_status not in health_status_list:
            print(f"未知健康状态值：{health_status}，已跳过")
            return None

        self.K2Table[health_status_list.index(health_status)][0 if _3_dimensions else 1] += 1
        return None

    def clearData(self):
        self.K2Table: list[list[int]] = [
            [0, 0],  # 优秀：[知信行合格, 知信行不合格]
            [0, 0],  # 良好：[知信行合格, 知信行不合格]
            [0, 0]  # 不合格：[知信行合格, 知信行不合格]
        ]

    def calculate_chi2(self):
        observed = self.K2Table
        # 检查观测表是否有效（无全零行/列）
        if any(sum(row) == 0 for row in observed):
            raise ValueError("存在全为0的行，无法计算卡方值")
        if any(sum(col) == 0 for col in zip(*observed)):
            raise ValueError("存在全为0的列，无法计算卡方值")
        # 调用scipy内置函数（返回：卡方值、P值、自由度、理论频数）
        chi2, p_value, df, _ = stats.chi2_contingency(observed)
        return chi2, df, p_value
        

class K2Data(QObject):
    def __init__(self):
        """
        采用3*2表格（3行2列）
        3行：health_status(优秀、良好、不合格)
        2列：知信行（合格、不合格）
        """
        # 初始化
        super().__init__()
        self._k2_worker = None
        self._k2_thread = None
        self.signals = K2DataSignal()
        self.questionnaire_filter_data: QuestionnaireFilterData = QuestionnaireFilterData()

    def getK2(self, dimensions: list[str], questionnaire_filter_data: QuestionnaireFilterData):
        """
        获取卡方（使用附属线程）
        """
        # 如果已有正在运行的线程，则不重复启动（可按需改为先停止旧线程）
        existing_thread = getattr(self, "_k2_thread", None)
        if existing_thread is not None and existing_thread.isRunning():
            return

        self.questionnaire_filter_data = questionnaire_filter_data

        # 创建线程 和 worker
        thread: QThread = QThread(self)
        worker = K2DataWorker(self, dimensions)
        self._k2_worker = worker
        self._k2_thread = thread

        # 当线程开始时执行worker.run
        thread.started.connect(worker.run)

        # 将 worker 的结果转发到外部的 signals
        worker.signals.finish.connect(self.signals.finish)
        worker.signals.error.connect(self.signals.error)

        # 分析完成或出错后退出线程并清理对象
        worker.signals.finish.connect(thread.quit)
        worker.signals.error.connect(thread.quit)

        # 清理引用，避免 QThread: Destroyed while thread is still running
        def _clear_refs():
            try:
                # 延迟删除引用以便 Qt 完成内部清理
                if getattr(self, "_k2_worker", None) is worker:
                    self._k2_worker = None
                if getattr(self, "_k2_thread", None) is thread:
                    self._k2_thread = None
            except Exception:
                pass

        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(_clear_refs)

        # 启动线程（在新线程中执行 run）
        thread.start()

    def stopEffectiveness(self, wait_ms: int = 2000) -> None:
        '''
        尝试停止正在运行的效度分析线程（最佳努力）
        '''
        thread: QThread = getattr(self, "_k2_thread", None)
        if thread is None:
            return
        try:
            # 请求退出并等待一段时间
            thread.quit()
            thread.wait(wait_ms)
        except Exception:
            pass