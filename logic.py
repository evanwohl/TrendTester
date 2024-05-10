import urllib
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf
import pandas
import matplotlib.pyplot as plt
import base64
from io import BytesIO
def get_stock_price(ticker, start_year=2008):
    """
    Get the stock price data for the given ticker and start year
    :param ticker: a string representing the stock ticker
    :param start_year: an integer representing the start year
    :return: a pandas DataFrame with columns 'Close', 'High', 'Low'
    """
    stock = yf.Ticker(ticker)
    stock_data = stock.history(start=f"{str(start_year)}-01-01")
    return stock_data[['Close', 'High', 'Low']]

def calculate_rsi(df, args):
    """
    Calculate the Relative Strength Index for the given data
    :param df: a pandas DataFrame with a column 'Close'
    :param period: a positive integer representing the period for RSI
    :return: a pandas DataFrame with columns 'Close', 'RSI'
    """
    delta = df['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=int(args['RSI_Period'])).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=int(args['RSI_Period'])).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df
def calculate_stochastic_oscillator(df, args):
    """
    Calculate the stochastic oscillator for the given data
    :param df: a pandas DataFrame with column 'Price'
    :param k_period: a positive representing the period for %K
    :param d_period: a positive representing the period for %D
    :return: a pandas DataFrame with columns 'Price', 'High', 'Low', 'SO High', 'SO Low', '%K', '%D'
    """
    df['SO High'] = df['Close'].rolling(window=int(args['SO_%K Period'])).max()
    df['SO Low'] = df['Close'].rolling(window=int(args['SO_%K Period'])).min()
    df['%K'] = ((df['Close'] - df['SO Low']) / (df['SO High'] - df['SO Low'])) * 100
    df['%D'] = df['%K'].rolling(window=int(args['SO_%D Period'])).mean()
    return df

def calculate_macd(df, args):
    """
    Calculate the MACD and Signal Line for the given data
    :param df: a pandas DataFrame with a column 'Close'
    :param short_ema_period: a positive integer representing the period for the short EMA
    :param long_ema_period: a positive integer representing the period for the long EMA
    :param signal_period: a positive integer representing the period for the signal line
    :return: a pandas DataFrame with columns 'Close', 'MACD', 'Signal Line'
    """
    short_ema = df['Close'].ewm(span=int(args['MACD_Short EMA Period']), adjust=False).mean()
    long_ema = df['Close'].ewm(span=int(args['MACD_Long EMA Period']), adjust=False).mean()
    df['MACD'] = short_ema - long_ema
    df['Signal Line'] = df['MACD'].ewm(span=int(args['MACD_Signal Period']), adjust=False).mean()
    return df
def calculate_roc(df, args):
    """
    Calculate the Rate of Change for the given data
    :param df: a pandas DataFrame with a column 'Close'
    :param period: a positive integer representing the period for the Rate of Change
    :return: a pandas DataFrame with columns 'Close', 'ROC'
    """
    df['ROC'] = ((df['Close'] - df['Close'].shift(int(args['ROC_Period']))) / df['Close'].shift(int(args['ROC_Period']))) * 100
    return df
def calculate_cci(df, args):
    """
    Calculate the Commodity Channel Index for the given data
    :param df: a pandas DataFrame with columns 'Close', 'High', 'Low'
    :param periods: a positive integer representing the period for CCI
    :return: a pandas DataFrame with columns 'Close', 'High', 'Low', 'CCI'
    """
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    sma = tp.rolling(window=int(args['CCI_Period'])).mean()
    mean_deviation = tp.rolling(window=int(args['CCI_Periods'])).apply(lambda x: abs(x - x.mean()).mean())
    df['CCI'] = (tp - sma) / (0.015 * mean_deviation)
    return df
def prep_data_calculate_indicators(ticker, indicators, start_year, args):
    """
    Prepare the data for the given stock ticker and calculate the indicators
    :param ticker: a string representing the stock ticker
    :return: a pandas DataFrame with columns 'Close', 'High', 'Low', 'RSI', 'MACD', 'Signal Line', 'CCI', 'ROC', 'SO High', 'SO Low', '%K', '%D'
    """
    data = get_stock_price(ticker, start_year)
    for indicator in indicators:
        data = fnc[indicator](data, args)
    return data

def backtest_strategy(df, args, ticker):
    df = df.dropna()
    params = {}
    so = False
    for arg in args:
        if 'Buy' in arg:
            if 'SO' in arg:
                so = True
                params['%D'] = 1
            else:
                params[arg.split("_")[0]] = 1
            print(params)
    if so:
        args['%D_Buy'] = args['SO_Buy']
        args['%D_Sell'] = args['SO_Sell']
        del args['SO_Buy']
        del args['SO_Sell']
    balance = [100]
    current_position = 0
    for index, row in df.iterrows():
        if current_position > 0:
            signal = True
            for param in params:
                if row[param] > int(args[f"{param}_Sell"]):
                    signal = False
            balance.append(row['Close'] * current_position)
            if signal:
                print(f"SELL {current_position} SHARES {ticker} AT ${row['Close']} ON {index}")
                current_position = 0
        else:
            signal = True
            for param in params:
                print(param)
                if row[param] < int(args[f"{param}_Buy"]):
                    signal = False
            balance.append(balance[-1])
            if signal:
                print(f"BUY {balance[-1] / row['Close']} SHARES {ticker} AT ${row['Close']} ON {index}")
                current_position = balance[-1] / row['Close']
    print(balance)
    return balance

def calculate_volatility(portfolio_balance):
    """
    Calculate the volatility of the portfolio balance
    :param portfolio_balance: a list of floats representing the portfolio balance over time
    :return: a float representing the volatility of the portfolio
    """
    return np.std(portfolio_balance)
def interepret_results(portfolio_balance):
    portfolio_balance = pd.DataFrame(portfolio_balance, columns=['Balance'])
    portfolio_balance['50 day avg'] = portfolio_balance['Balance'].rolling(window=50).mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    portfolio_balance['Balance'].plot(color='blue', linestyle='-', linewidth=1, label='Portfolio Balance')
    portfolio_balance['50 day avg'].plot(color='orange', linestyle='-', linewidth=1, label='50-point Moving Avg')
    plt.xlabel('Data Point', fontsize=12)
    plt.ylabel('Balance', fontsize=12)
    plt.title('Portfolio Balance Over Time', fontsize=14)
    ax.legend()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read()).decode('utf-8')
    return 'data:image/png;base64,' + string.rstrip()
fnc = {
    "RSI": calculate_rsi,
    "MACD": calculate_macd,
    "SO": calculate_stochastic_oscillator,
    "CCI": calculate_cci,
    "ROC": calculate_roc,
    "WR": calculate_roc
}
if __name__ == '__main__':
    tickers = ['AAPL', 'MSFT']
    indicators = ['RSI',]
    start_year = 2010
    holder = []
    for ticker in tickers:
        data = prep_data_calculate_indicators(ticker, indicators, start_year)
        holder.append(data)



