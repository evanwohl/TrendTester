from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session
import logic
app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start')
def start():
    return render_template('start.html')

@app.route('/build', methods=['GET', 'POST'])
def build():
    if request.method == 'POST':
        tickers = request.form['tickers'].split(',')
        print(request.form.to_dict())
        signal_dict = {}
        for item in request.form:
            if 'Signal' in item:
                signal_dict[item.split(" ")[0]] = request.form[item]
        balances = []
        for ticker in tickers:
            data = logic.prep_data_calculate_indicators(ticker, request.form.getlist('indicator'), int(request.form['start_year']), request.form.to_dict())
            balance = logic.backtest_strategy(data, signal_dict, ticker)
            balances.append(balance)
        max_len = max([len(balance) for balance in balances])

        for i in range(len(balances)):
            balances[i] = ([100] * (max_len - len(balances[i]))) + balances[i]
        portfolio_value = [sum([balance[i] for balance in balances]) for i in range(max_len)]
        max_drawdown_percent = 0
        for i in range(len(portfolio_value)):
            for j in range(i, len(portfolio_value)):
                max_drawdown_percent = max(max_drawdown_percent,
                                           (portfolio_value[j] -
                                            portfolio_value[i]) / portfolio_value[i])
        print(max_drawdown_percent)
        roi = ((portfolio_value[-1] - portfolio_value[0]) / portfolio_value[0])
        start_year = int(request.form['start_year'])
        current_year = datetime.now().year
        num_years = current_year - start_year
        annualized_roi = (1 + roi) ** (1 / num_years) - 1
        print(roi, annualized_roi, max_drawdown_percent)
        plot_img = logic.interepret_results(portfolio_value)
        volatility = logic.calculate_volatility(portfolio_value)
        return render_template('results.html', plot_img=plot_img,
                               roi=roi*100, annualized_roi=annualized_roi*100,
                               max_drawdown_percent=max_drawdown_percent,
                               volatility=volatility)
    else:
        indicators = request.args.getlist('indicator')
        if len(indicators) == 0:
            return render_template('start.html')
        indicator_parameters = {
            "RSI": ("RSI", ["Period", "Buy Signal", "Sell Signal"]),
            "MACD": ("MACD", ["Short EMA Period", "Long EMA Period", "Signal Period"]),
            "SO": ("Stochastic Oscillator", ["%K Period", "%D Period", "Buy Signal", "Sell Signal"]),
            "CCI": ("Commodity Channel Index", ["Periods", "Buy Signal", "Sell Signal"]),
            "ROC": ("Rate of Change", ["Period", "Buy Signal", "Sell Signal"]),
            "WR": ("Williams %R", ["Period", "Buy Signal", "Sell Signal"]),
        }
        selected_indicator_parameters = {indicator: indicator_parameters[indicator] for indicator in indicators}
        return render_template('build.html', indicators=selected_indicator_parameters)


if __name__ == '__main__':
    app.run()