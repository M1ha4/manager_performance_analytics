import pandas as pd
import numpy as np

# === 1. Загрузка данных ===
financial = pd.read_csv('data/financial_data.csv', sep=',')
prolong = pd.read_csv('data/prolongations.csv', sep=',')

# Приводим названия столбцов к нижнему регистру для удобства
financial.columns = [col.strip().lower() for col in financial.columns]
prolong.columns = [col.strip().lower() for col in prolong.columns]


