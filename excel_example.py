import pandas as pd
import numpy as np
import os
import logging
from pathlib import Path
from src import version

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataMatrixProcessor:
    def __init__(self, folder_name="pandas_output"):
        """初始化文件夹路径"""
        self.output_dir = Path(folder_name)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"输出目录已准备: {self.output_dir.absolute()}")

    def generate_random_long_data(self, min_size=1000, max_size=5000):
        """生成随机长度的长向量数据"""
        size = np.random.randint(min_size, max_size)
        data = np.random.randn(size) * 100  # 生成正态分布数据并放大
        logging.info(f"生成了长度为 {size} 的原始数据")
        return data

    def reshape_to_optimal_matrix(self, data):
        """将一维数据拆分为矩阵。如果不满整除，则用NaN填充。"""
        size = len(data)
        cols = int(np.ceil(np.sqrt(size))) # 计算列数（向上取整的平方根）
        rows = int(np.ceil(size / cols))   # 计算行数
        
        logging.info(f"矩阵维度计算结果: {rows} 行 x {cols} 列")
        
        # 填充数据以匹配矩阵形状
        padded_data = np.pad(data.astype(float), 
                            (0, rows * cols - size), 
                            mode='constant', 
                            constant_values=np.nan)
        
        matrix = padded_data.reshape(rows, cols)
        
        # 转换为 DataFrame
        df = pd.DataFrame(matrix, 
                          columns=[f"Col_{i+1}" for i in range(cols)],
                          index=[f"Row_{i+1}" for i in range(rows)])
        return df

    def save_with_styling(self, df, filename="matrix_result.xlsx"):
        """保存 DataFrame 到 Excel，并应用样式和统计信息"""
        file_path = self.output_dir / filename
        
        # 计算一些基础统计信息
        summary_df = df.describe()

        try:
            # 使用 xlsxwriter 作为引擎，以便进行样式操作
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                # 写入主数据
                df.to_excel(writer, sheet_name='Data_Matrix')
                # 写入统计摘要
                summary_df.to_excel(writer, sheet_name='Summary_Statistics')

                # 获取 xlsxwriter 对象进行样式定制
                workbook  = writer.book
                worksheet = writer.sheets['Data_Matrix']

                # 定义一种高亮样式：背景为淡黄色，字体为深红色
                highlight_fmt = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C0006'})

                # 对数据区域应用条件格式（大于 0 的值高亮显示）
                # 注意：条件格式范围从数据起始位置开始
                max_row, max_col = df.shape
                worksheet.conditional_format(1, 1, max_row, max_col,
                                           {'type':     'cell',
                                            'criteria': '>',
                                            'value':    0,
                                            'format':   highlight_fmt})

                # 设置列宽
                worksheet.set_column(0, max_col, 12)

            logging.info(f"文件成功保存至: {file_path}")
        except Exception as e:
            logging.error(f"保存文件时出错: {e}")

def main():
    # 实例化处理器
    processor = DataMatrixProcessor("pandas_data_results")

    # 1. 生成随机长数据
    raw_data = processor.generate_random_long_data(2500, 5000)

    # 2. 转换为矩阵（DataFrame）
    matrix_df = processor.reshape_to_optimal_matrix(raw_data)

    # 3. 保存并美化
    processor.save_with_styling(matrix_df, "Complex_Data_Export.xlsx")

if __name__ == "__main__":
    # 检查是否安装了必要的库
    try:
        import xlsxwriter
    except ImportError:
        print("请先安装 xlsxwriter: pip install xlsxwriter")
    else:
        main()
