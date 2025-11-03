import pandas as pd
import numpy as np
from scipy.stats import pearsonr, bartlett, ConstantInputWarning # citc相关性计算
from pingouin import cronbach_alpha # Cronbach's Alpha系数
import warnings

warnings.simplefilter("ignore", RuntimeWarning) # 忽略运行时警告
warnings.simplefilter("ignore", FutureWarning) # 忽略未来警告
warnings.simplefilter("ignore", UserWarning) # 忽略用户警告

# 信度分析
    
class QuestionTrustData:
    def __init__(self, id: int, CITC: float, alpha_without_item: float, constant_input: bool = False):
        '''
        信度分析数据类
        
        @param id: 题目ID
        @param CITC: 题目CITC
        @param alpha_without_item: 题目项已删除的α系数
        @param constant_input: 是否是常量输入题
        '''
        self.id = id
        self.CITC = CITC
        self.alpha_without_item = alpha_without_item
        self.constant_input: bool = constant_input # 是否是常量输入题

class QuestionTrustDatas:
    def __init__(self, original_alpha: float, trust_datas: list[QuestionTrustData]):
        '''
        信度分析数据列表类

        @param original_alpha: 原始量表的Cronbach's Alpha系数
        @param trust_datas: 信度分析数据列表
        '''
        self.original_alpha: float = original_alpha # 原始量表的Cronbach's Alpha系数
        self.trust_datas: list[QuestionTrustData] = trust_datas # 信度分析数据列表

    def print(self):
        '''
        打印信度分析数据列表
        '''
        print("\n========== 信度分析数据列表 ==========")
        print(f"原始量表的Cronbach's Alpha系数: {self.original_alpha}")
        print("各题的CITC和项已删除的α系数:")
        for data in self.trust_datas:
            print(f"题目ID: {data.id}, CITC: {data.CITC}, 项已删除的α系数: {data.alpha_without_item}")
        print("=====================================\n")

class QuestionTrust:
    def __init__(self, questions: list[int], scores_list: list[list[int]]):
        '''
        题目信度分析管理类

        @param questions: 题目ID列表
        @param scores_list: 各个问卷的分数列表
        '''
        self.questions = questions # 题目ID列表
        self.scores_list = scores_list # 各个问卷的分数列表

    def getDataFrame(self) -> pd.DataFrame:
        '''
        获取数据列表DataFrame
        '''
        df: pd.DataFrame = pd.DataFrame(self.scores_list, columns=self.questions)
        # 按照题目ID排序
        df = df.sort_index(axis=1)
        return df

    def calculate_citc_and_alpha(self, data: pd.DataFrame) -> tuple[float, list[dict]]:
        '''
        计算CITC和项已删除的α系数

        @param data: 题目分数列表DataFrame
        @return: 原始量表的Cronbach's Alpha系数，各题的CITC和项已删除的α系数列表
        @rtype: tuple[float, list[dict]]
        '''
        results: list[dict] = []

        tototal_items = data.shape[1] # 总题目数
        # 计算原始量表的α系数
        original_alpha = cronbach_alpha(data)[0]
        # 计算所有题项的总分
        total_score = data.sum(axis=1)

        for item in data.columns:
            # 计算CITC
            item_removed_total = total_score - data[item]
            constant_input = False
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=ConstantInputWarning)
                try:
                    citc, _ = pearsonr(data[item], item_removed_total)
                except ConstantInputWarning:
                    # 若出现常量输入警告
                    constant_input = True
            
            # 计算删除当前题项后的α系数
            data_without_item = data.drop(columns=[item])
            alpha_without_item = cronbach_alpha(data_without_item)[0]
            
            results.append({
                'id': item,
                'citc': round(citc, 4),
                'alpha_without_item': round(alpha_without_item, 4),
                'constant_input': constant_input
            })
            
        return original_alpha, results
        
    def getTrustDatas(self) -> QuestionTrustDatas:
        '''
        获取信度分析数据列表
        '''
        df: pd.DataFrame = self.getDataFrame()
        # 计算CITC和项已删除的α系数
        original_alpha, trust_datas = self.calculate_citc_and_alpha(df)
        # 转换为QuestionTrustData对象列表
        trust_data_objs: list[QuestionTrustData] = []
        for data in trust_datas:
            trust_data_objs.append(QuestionTrustData(data['id'], data['citc'], data['alpha_without_item'], data['constant_input']))
        # 返回信度分析数据列表
        return QuestionTrustDatas(original_alpha, trust_data_objs)