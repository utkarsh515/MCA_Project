import pandas as pd

def preprocess_data(df):
    # Clean and engineer features like TotalSales
    df['TotalSales'] = df['Quantity'] * df['UnitPrice']
    df.dropna(subset=['CustomerID', 'InvoiceDate'], inplace=True)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    df.dropna(subset=['InvoiceDate'], inplace=True)
    df = df[(df['Quantity'] > 0) & (df['TotalSales'] > 0)]

    ref_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (ref_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalSales': 'sum'
    }).reset_index()

    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

    # Assume model uses only numeric RFM values
    return rfm


def get_customer_result(df, customer_id):
    customer_id = int(customer_id)
    record = df[df['CustomerID'] == customer_id]
    if record.empty:
        return None

    result = {
        'CustomerID': int(record['CustomerID'].values[0]),
        'Churn': int(record['churn'].values[0]),
        'ChurnProbability': float(round(record['churn_probability'].values[0], 4)),
        'Rank': int(record['rank'].values[0])
    }
    return result



def get_top_n_churn(df, n):
    sorted_df = df.sort_values(by='churn_probability', ascending=False).head(n).copy()
    sorted_df['rank'] = range(1, len(sorted_df) + 1)  # Manually assign ranks 1 to N
    return sorted_df[['CustomerID', 'churn_probability', 'rank']].to_dict(orient='records')

# def get_top_n_churn(df, n):
#     top_customers = df.sort_values(by='churn_probability', ascending=False).head(n)
#     return top_customers[['CustomerID', 'churn_probability', 'rank']].to_dict(orient='records')
