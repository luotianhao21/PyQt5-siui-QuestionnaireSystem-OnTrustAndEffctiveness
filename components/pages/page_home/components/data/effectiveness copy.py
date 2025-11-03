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
        print(f"Kaiser-Meyer-Olkin指数: {self.kmo}")
        print(f"Bartlett指数: {self.bartlett}")
        print(f"效度系数: {self.p}")
        print("各题的因子列表和共同度:")
        for data in self.effectiveness_datas:
            print(f"题目ID: {data.id}, 因子列表: {data.factors}, 共同度: {data.commonness}")
        print("==========\n")

class EffectivenessDataPyqtSignal(QObject):
    finish = pyqtSignal(EffectivenessDatas) # 效度分析成功信号
    error = pyqtSignal(warnings.WarningMessage) # 效度分析失败信号

class Effectiveness:
    def __init__(self, questions: list[int], scores_list: list[list[int]]):
        '''
        效度分析管理类

        @param questions: 题目ID列表
        @param scores_list: 各个问卷的分数列表
        '''
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
        print(f"KMO指数: {kmo_model}")
        if kmo_model < 0.5 or np.isnan(kmo_model):
            error_list.append("KMO 指数过低或无效，数据不适合因子分析。\n")

        # 进行巴特利特球形检验
        chi_square_value, p_value = calculate_bartlett_sphericity(data)
        print(f"Bartlett指数: {chi_square_value}, p值: {p_value}")
        if np.isnan(chi_square_value) or np.isnan(p_value):
            error_list.append("Bartlett 检验失败，数据可能不适合因子分析。\n")

        # 执行因子分析，提取指定数量的因子
        dimensions = self.getDimensions()
        n_factors = min(len(dimensions), data.shape[1] - 1)  # 限制因子数量
        print(f"因子数量: {n_factors}")
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

        return kmo_all, chi_square_value, p_value, effectiveness_datas, error_list
    
    def getEffectivenessDatas(self) -> None:
        '''
        获取效度分析数据列表
        '''
        df: pd.DataFrame = self.getDataFrame()
        # 效度分析
        kmo_all, chi_square_value, p_value, effectiveness_datas, error_list = self.effectiveness_analysis(df)
        # 转换为EffectivenessDatas对象
        dimensions = self.getDimensions()
        self.signals.finish.emit(EffectivenessDatas(dimensions, kmo_all, chi_square_value, p_value, effectiveness_datas)) # 效度分析成功信号