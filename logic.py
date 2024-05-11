import numpy as np
import pandas as pd
import yfinance as yf
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
def get_risk_free_rate(start_year=2008):
    """
    Get the risk-free rate for the given start year
    :param start_year: an integer representing the start year
    :return: a float representing the risk-free rate
    """
    risk_free_rate = yf.Ticker('^IRX')
    risk_free_data = risk_free_rate.history(start=f"{str(start_year)}-01-01")
    return risk_free_data['Close'].mean()

def calculate_sharpe(portfolio_value, risk_free_rate):
    """
    Calculate the Sharpe ratio for the given portfolio value and risk-free rate
    :param portfolio_value: a list of floats representing the portfolio value over time
    :param risk_free_rate: a float representing the risk-free rate
    :return: a float representing the Sharpe ratio
    """
    returns = [(portfolio_value[i] - portfolio_value[i - 1]) for i in range(1, len(portfolio_value))]
    mean_return = np.mean(returns)
    std_dev = np.std(returns)
    sharpe = (mean_return - risk_free_rate) / std_dev
    return sharpe
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
    sma = tp.rolling(window=int(args['CCI_Periods'])).mean()
    mean_deviation = tp.rolling(window=int(args['CCI_Periods'])).apply(lambda x: abs(x - x.mean()).mean())
    df['CCI'] = (tp - sma) / (0.015 * mean_deviation)
    return df
def calculate_wr(df, args):
    """
    Calculate the Williams %R for the given data
    :param df: a pandas DataFrame with columns 'Close', 'High', 'Low'
    :param period: a positive integer representing the period for Williams %R
    :return: a pandas DataFrame with columns 'Close', 'High', 'Low', 'Williams %R'
    """
    df['Highest High'] = df['High'].rolling(window=int(args['WR_Period'])).max()
    df['Lowest Low'] = df['Low'].rolling(window=int(args['WR_Period'])).min()
    df['WR'] = ((df['Highest High'] - df['Close']) / (df['Highest High'] - df['Lowest Low'])) * -100
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


def get_average_risk_free_rate(start_year):
    """
    Fetches the average risk-free rate from the 13-week US Treasury Bill over a specified period using yfinance.

    :param start_date: Start date in 'YYYY-MM-DD' format.
    :param end_date: End date in 'YYYY-MM-DD' format.
    :return: Average risk-free rate as a float.
    """
    tbill = yf.Ticker("^IRX")
    hist = tbill.history(start=f"{start_year}-01-01")
    return hist['Close'].mean() / 100


def calculate_sharpe_ratio(portfolio_values, start_year):
    """
    Calculate the Sharpe Ratio for a given list of portfolio values and risk-free rate.

    :param portfolio_values: List of integers where each entry is the portfolio value for a trading day.
    :param risk_free_rate: Annual risk-free rate, expressed as a decimal.
    :return: The Sharpe Ratio as a float.
    """
    yearly_portfolio_values = [portfolio_values[i] for i in range(0, len(portfolio_values), 252)]
    returns = np.diff(yearly_portfolio_values) / yearly_portfolio_values[:-1]
    mean_return = np.mean(returns)
    std_deviation = np.std(returns)
    adjusted_return = mean_return - get_risk_free_rate(start_year)
    sharpe_ratio = adjusted_return / std_deviation if std_deviation != 0 else 0

    return sharpe_ratio
def backtest_strategy(df, args, ticker):
    """
    Backtest the trading strategy using the given data and strategy parameters
    :param df: a pandas dataframe containing the stock data and indicator values
    :param args: a dictionary containing the strategy parameters
    :param ticker: a string representing the stock ticker
    :return: a list of floats representing the portfolio balance over time
    """
    df = df.dropna()
    params = {}
    so = False
    macd = False
    for arg in args:
        if 'MACD' in arg:
            macd = True
        if 'Buy' in arg:
            if 'SO' in arg:
                so = True
                params['%D'] = 1
            else:
                params[arg.split("_")[0]] = 1
    if so:
        args['%D_Buy'] = args['SO_Buy']
        args['%D_Sell'] = args['SO_Sell']
        del args['SO_Buy']
        del args['SO_Sell']
    balance = [100]
    current_position = 0
    balance_at_last_trade = 100
    wins = []
    losses = []
    for index, row in df.iterrows():
        if current_position > 0:
            signal = True
            if macd:
                if row['MACD'] < row['Signal Line']:
                    signal = False
            if signal:
                for param in params:
                    signal_value = args[f"{param}_Sell"]
                    value = int(signal_value[1:])
                    if '>' in signal_value:
                        if row[param] < value:
                            signal = False
                            break
                    else:
                        if row[param] > value:
                            signal = False
                            break
            balance.append(row['Close'] * current_position)
            if signal:
                if row['Close'] * current_position > balance_at_last_trade:
                    wins.append(row['Close'] * current_position - balance_at_last_trade)
                else:
                    losses.append(balance_at_last_trade - row['Close'] * current_position)
                balance_at_last_trade = row['Close'] * current_position
                current_position = 0
        else:
            signal = True
            if macd:
                if row['MACD'] > row['Signal Line']:
                    signal = False
            if signal:
                for param in params:
                    signal_value = args[f"{param}_Buy"]
                    value = int(signal_value[1:])
                    if '>' in signal_value:
                        if row[param] < value:
                            signal = False
                            break
                    else:
                        if row[param] > value:
                            signal = False
                            break
            balance.append(balance[-1])
            if signal:
                current_position = balance[-1] / row['Close']
    if current_position > 0:
        if balance_at_last_trade < balance[-1]:
            wins.append(balance[-1] - balance_at_last_trade)
        else:
            losses.append(balance_at_last_trade - balance[-1])
    return balance, wins, losses

def calculate_volatility(portfolio_balance):
    """
    Calculate the volatility of the portfolio balance
    :param portfolio_balance: a list of floats representing the portfolio balance over time
    :return: a float representing the volatility of the portfolio
    """
    return np.std(portfolio_balance)
def plot_results(portfolio_balance):
    """
    Create a plot of the portfolio balance over time
    :param portfolio_balance: a list of floats representing the portfolio balance over time
    :return:
    """
    portfolio_balance = pd.DataFrame(portfolio_balance, columns=['Balance'])
    portfolio_balance['50 day avg'] = portfolio_balance['Balance'].rolling(window=50).mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    portfolio_balance['Balance'].plot(color='blue', linestyle='-', linewidth=1, label='Portfolio Balance')
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
    plt.close()
    return 'data:image/png;base64,' + string.rstrip()

def plot_pnl_distribution(trade_results):
    """
    Create a plot of the profit/loss distribution of the trades
    :param trade_results: a list of floats representing the profit/loss of each trade
    :return:
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(trade_results, bins=75, color='blue', alpha=0.7, edgecolor='black')
    plt.xlabel('Profit/Loss', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Profit/Loss Distribution of Trades', fontsize=14)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return 'data:image/png;base64,' + string.rstrip()

fnc = {
    "RSI": calculate_rsi,
    "MACD": calculate_macd,
    "SO": calculate_stochastic_oscillator,
    "CCI": calculate_cci,
    "ROC": calculate_roc,
    "WR": calculate_wr
}
if __name__ == '__main__':
    pass



