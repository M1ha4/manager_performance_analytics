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


# === 4. Объединение с таблицей пролонгаций ===
merged = financial_cleaned.merge(prolong, on='id', how='left')



# === 5. Расчёт коэффициентов пролонгации ===
months = month_cols
results = []


for i in range(1, len(months)):
    prev_m = months[i - 1]
    curr_m = months[i]


    # Первый месяц пролонгации
    denom_df = merged[merged['month'] == prev_m] # проекты, завершившиеся в прошлом месяце
    if len(denom_df) == 0:
        continue


    denom_sum = denom_df[prev_m].sum()
    numer_sum = denom_df[curr_m].sum()
    coef1 = numer_sum / denom_sum if denom_sum > 0 else 0


    # Второй месяц пролонгации
    prev_prev_m = months[i - 2] if i - 2 >= 0 else None
    if prev_prev_m:
        denom2_df = merged[(merged['month'] == prev_prev_m) & (merged[months[i - 1]] == 0)]
        denom2_sum = denom2_df[prev_prev_m].sum()
        numer2_sum = denom2_df[curr_m].sum()
        coef2 = numer2_sum / denom2_sum if denom2_sum > 0 else 0
    else:
        coef2 = np.nan


    results.append({
        'month': curr_m,
        'coef_first_month': round(coef1, 3),
        'coef_second_month': round(coef2, 3)
    })


coef_df = pd.DataFrame(results)


# === 6. Расчёт коэффициентов по каждому менеджеру ===
am_results = []

for am in merged['account'].unique():
    am_df = merged[merged['account'] == am]

    for i in range(1, len(months)):
        prev_m = months[i - 1]
        curr_m = months[i]

        # --- Первый месяц пролонгации ---
        denom_sum = am_df[am_df['month'] == prev_m][prev_m].sum()
        numer_sum = am_df[am_df['month'] == prev_m][curr_m].sum()
        coef1 = numer_sum / denom_sum if denom_sum > 0 else 0

        # --- Второй месяц пролонгации ---
        prev_prev_m = months[i - 2] if i - 2 >= 0 else None
        if prev_prev_m:
            denom2_df = am_df[(am_df['month'] == prev_prev_m) & (am_df[months[i - 1]] == 0)]
            denom2_sum = denom2_df[prev_prev_m].sum()
            numer2_sum = denom2_df[curr_m].sum()
            coef2 = numer2_sum / denom2_sum if denom2_sum > 0 else 0
        else:
            coef2 = np.nan

        am_results.append({
            'account': am,
            'month': curr_m,
            'coef_first_month': round(coef1, 3),
            'coef_second_month': round(coef2, 3)
        })

am_coef_df = pd.DataFrame(am_results)