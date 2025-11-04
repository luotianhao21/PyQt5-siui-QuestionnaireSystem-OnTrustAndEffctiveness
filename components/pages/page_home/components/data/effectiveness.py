from PyQt5.QtCore import QObject, pyqtSignal, QThread
import warnings
from scripts.database import Database, QuestionnaireScores, QuestionnaireFilterData
from scripts.questions import Questions
import pandas as pd
import numpy as np
from factor_analyzer import FactorAnalyzer # 因子分析
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity # 因子分析
from sklearn.preprocessing import StandardScaler

# 效度分析
class EffectivenessData:
    def __init__(self, id: int, dimension: str, factors: list[float], commonness: float, constant_input: bool = False):
        '''
        效度分析数据类

        @param id: 题目ID
        @param dimension: 维度
        @param factors: 因子列表
        @param commonness: 共同度
        @param constant_input: 是否是常量输入题
        '''
        self.id: int = id
        self.dimension: str = dimension
        self.factors: list[float] = factors
        self.commonness: float = commonness
        self.constant_input: bool = constant_input # 是否是常量输入题

class EffectivenessDatas:
    def __init__(self, dimensions: list[str], kmo: float, bartlett: float, p: float, effectiveness_datas: list[EffectivenessData]):
        '''
        效度分析数据列表类

        @param dimensions: 维度列表
        @param kmo: Kaiser-Meyer-Olkin指数
        @param bartlett: Bartlett指数
        @param p: 效度系数
        @param effectiveness_datas: 效度分析数据列表
        '''
        self.dimensions: list[str] = dimensions # 维度列表
        self.kmo: float = kmo # Kaiser-Meyer-Olkin指数
        self.bartlett: float = bartlett # Bartlett指数
        self.p: float = p # 效度系数
        self.effectiveness_datas: list[EffectivenessData] = effectiveness_datas # 效度分析数据列表

    def print(self):
        '''
        打印效度分析数据列表
        '''
        print("\n========== 效度分析数据列表 ==========")
        print(f"维度列表: {self.dimensions}")
        print(f"KMO指数: {self.kmo}")
        print(f"Bartlett指数: {self.bartlett}")
        print(f"p值: {self.p}")
        print("各题的因子列表和共同度:")
        for data in self.effectiveness_datas:
            print(f"题目ID: {data.id}, 因子列表: {data.factors}, 共同度: {data.commonness}")
        print("==========\n")

class EffectivenessDataPyqtSignal(QObject):
    finish: pyqtSignal = pyqtSignal(EffectivenessDatas) # 效度分析成功信号
    error: pyqtSignal = pyqtSignal(warnings.WarningMessage) # 效度分析失败信号

class EffectivenessWorker(QObject):
    """
    后台 worker：在附属 QThread 中运行效度分析并通过 signals 上报结果
    使用方式：moveToThread(thread)，连接 thread.started -> worker.run
    """
    signals = EffectivenessDataPyqtSignal()

    def __init__(self, effectiveness: 'Effectiveness'):
        super().__init__()
        self._effectiveness = effectiveness

    def run(self):
        try:
            # 运行原有的分析流程（同步逻辑）
            df: pd.DataFrame = self._effectiveness.getDataFrame()
            kmo_all, chi_square_value, p_value, effectiveness_datas, error_list = self._effectiveness.effectiveness_analysis(df)
            dimensions = self._effectiveness.getDimensions()
            datas_obj = EffectivenessDatas(dimensions, kmo_all, chi_square_value, p_value, effectiveness_datas)
            # 发射成功信号
            self.signals.finish.emit(datas_obj)
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

class Effectiveness(QObject):
    def __init__(self, questions: list[int], scores_list: list[list[int]]):
        '''
        效度分析管理类

        @param questions: 题目ID列表
        @param scores_list: 各个问卷的分数列表
        '''
        super().__init__()
        self._effectiveness_worker = None
        self._effectiveness_thread = None
        self.signals = EffectivenessDataPyqtSignal()
        self.questions = Questions() # 题目管理类

        self.filter_questions: list[int] = questions # 题目ID列表
        self.scores_list: list[list[int]] = scores_list # 各个问卷的分数列表

    def getDataFrame(self) -> pd.DataFrame:
        '''
        获取数据列表DataFrame
        '''
        df: pd.DataFrame = pd.DataFrame(self.scores_list, columns=self.filter_questions)
        df = pd.DataFrame(StandardScaler().fit_transform(df), columns=df.columns)  # 标准化数据

        # 检查并处理 NaN 或 inf
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.dropna(axis=0, how='any', inplace=True)

        # 按照题目ID排序
        df = df.sort_index(axis=1)
        return df
    
    def getDimensions(self) -> list[str]:
        '''
        获取题目列表中包含的维度列表
        '''
        dimensions: list[str] = []
        for question in self.filter_questions:
            dimension = self.questions.getQuestionDimension(question)
            if not dimension in dimensions:
                dimensions.append(dimension)
        return dimensions

    def effectiveness_analysis(self, data: pd.DataFrame) -> tuple[float, float, float, list[EffectivenessData], list[str]]:
        '''
        效度分析

        @param data: 题目分数列表DataFrame
        @return: 
        '''

        error_list: list[str] = []

        # 检查数据是否包含 NaN 或 inf
        if not np.isfinite(data).all().all():
            error_list.append("数据包含 NaN 或 inf，请检查输入数据。\n")

        # 计算KMO指数
        kmo_all, kmo_model = calculate_kmo(data)
        # print(f"KMO指数: {kmo_model}")
        if kmo_model < 0.5 or np.isnan(kmo_model):
            error_list.append("KMO 指数过低或无效，数据不适合因子分析。\n")

        # 进行巴特利特球形检验
        chi_square_value, p_value = calculate_bartlett_sphericity(data)
        # print(f"Bartlett指数: {chi_square_value}, p值: {p_value}")
        if np.isnan(chi_square_value) or np.isnan(p_value):
            error_list.append("Bartlett 检验失败，数据可能不适合因子分析。\n")

        # 执行因子分析，提取指定数量的因子
        dimensions = self.getDimensions()
        n_factors = min(len(dimensions), data.shape[1] - 1)  # 限制因子数量
        # print(f"因子数量: {n_factors}")
        factor_analyzer = FactorAnalyzer(n_factors=n_factors, rotation='varimax')
        factor_analyzer.fit(data)

        factor_loadings_result: list[list[float]] = factor_analyzer.loadings_  # 因子载荷
        factor_communality_result: list[float] = factor_analyzer.get_communalities()  # 共同度

        # 创建effectiveness_datas对象
        effectiveness_datas: list[EffectivenessData] = []
        for i, factor_loading in enumerate(factor_loadings_result):
            question_id = self.filter_questions[i]
            dimension = self.questions.getQuestionDimension(question_id)
            commonness = factor_communality_result[i]
            factors = factor_loading
            effectiveness_data = EffectivenessData(question_id, dimension, factors, commonness)
            effectiveness_datas.append(effectiveness_data)

        return kmo_model, chi_square_value, p_value, effectiveness_datas, error_list
    
    def getEffectivenessDatas(self) -> None:
        '''
        获取效度分析数据列表（使用附属线程异步运行）
        '''
        # 如果已有正在运行的线程，则不重复启动（可按需改为先停止旧线程）
        existing_thread = getattr(self, "_effectiveness_thread", None)
        if existing_thread is not None and existing_thread.isRunning():
            return

        # 创建线程与 worker，并保持引用防止被垃圾回收
        thread: QThread = QThread(self)  # 将 self 作为父对象以减少被回收几率
        worker = EffectivenessWorker(self)
        worker.moveToThread(thread)
        self._effectiveness_thread = thread
        self._effectiveness_worker = worker

        # 当线程启动时执行 worker.run
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
                if getattr(self, "_effectiveness_worker", None) is worker:
                    self._effectiveness_worker = None
                if getattr(self, "_effectiveness_thread", None) is thread:
                    self._effectiveness_thread = None
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
        thread: QThread = getattr(self, "_effectiveness_thread", None)
        if thread is None:
            return
        try:
            # 请求退出并等待一段时间
            thread.quit()
            thread.wait(wait_ms)
        except Exception:
            pass