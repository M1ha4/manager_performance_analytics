import pandas as pd
import numpy as np

# === 1. Загрузка данных ===
financial = pd.read_csv('data/financial_data.csv', sep=',')
prolong = pd.read_csv('data/prolongations.csv', sep=',')

# Приводим названия столбцов к нижнему регистру для удобства
financial.columns = [col.strip().lower() for col in financial.columns]
prolong.columns = [col.strip().lower() for col in prolong.columns]


# === 2. Предобработка данных ===
month_cols = [col for col in financial.columns if '2022' in col or '2023' in col or '2024' in col]


# Преобразуем значения сумм
for col in month_cols:
    financial[col] = (financial[col]
    .astype(str)
    .str.replace('\xa0', '', regex=True)
    .str.replace(' ', '', regex=True)
    .str.replace(',', '.', regex=True)
    .replace({'nan': np.nan, 'вноль': 'в ноль'}))



# === 3. Обработка спецзначений 'в ноль', 'стоп', 'end' ===


def clean_financial_row(row):
    values = row[month_cols].values
    # Исключаем проекты со 'стоп' или 'end'
    if any(str(v).lower() in ['стоп', 'end'] for v in values):
        return None # полностью исключаем
    # Если все значения 'в ноль', берем пред. месяц
    if all(str(v).lower() == 'в ноль' for v in values):
        idx = np.where(np.array([str(v).lower() == 'в ноль' for v in values]))[0]
        if len(idx) > 0 and idx[0] > 0:
            prev_month = month_cols[idx[0] - 1]
            row[month_cols[idx[0]]] = row[prev_month]
    # Преобразуем остальные значения в числа
    for col in month_cols:
        val = str(row[col]).lower()
        if val in ['nan', 'в ноль', 'стоп', 'end', '']:
            row[col] = 0
        else:
            try:
                row[col] = float(val)
            except:
                row[col] = 0
    return row



financial_cleaned = financial.apply(lambda x: clean_financial_row(x), axis=1)
financial_cleaned = financial_cleaned.dropna(subset=['id'])
