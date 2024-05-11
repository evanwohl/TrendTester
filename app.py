from datetime import datetime
from flask import Flask, render_template, request
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
        wins = []
        losses = []
        for ticker in tickers:
            data = logic.prep_data_calculate_indicators(ticker,
                                                        request.form.getlist('indicator'),
                                                        int(request.form['start_year']),
                                                        request.form.to_dict())
            balance, win, loss = logic.backtest_strategy(data, signal_dict, ticker)
            balances.append(balance)
            wins.append(win)
            losses.append(loss)
        max_len = max([len(balance) for balance in balances])
        for i in range(len(balances)):
            balances[i] = ([100] * (max_len - len(balances[i]))) + balances[i]
        portfolio_value = [sum([balance[i] for balance in balances]) for i in range(max_len)]
        roi = ((portfolio_value[-1] - portfolio_value[0]) / portfolio_value[0])
        start_year = int(request.form['start_year'])
        current_year = datetime.now().year
        num_years = current_year - start_year
        annualized_roi = (1 + roi) ** (1 / num_years) - 1
        plot_img = logic.plot_results(portfolio_value)
        initial_investment = 100 * len(tickers)
        final_investment_value = round(portfolio_value[-1], 2)
        average_win = sum([sum(win) for win in wins]) / sum(len(win) for win in wins)
        average_loss = sum([sum(loss)for loss in losses]) / sum(len(loss) for loss in losses)
        win_rate = sum([len(win) for win in wins]) / (sum([len(win) for win in wins]) + sum([len(loss) for loss in losses]))
        num_trades = sum([len(win) for win in wins]) + sum([len(loss) for loss in losses])
        print(f"Average Win: {average_win}")
        print(f"Average Loss: {average_loss}")
        print(f"Win Rate: {win_rate}")
        print(f"Number of Trades: {num_trades}")

        return render_template('results.html', plot_img=plot_img,
                               roi=round(roi*100, 2), annualized_roi=round(annualized_roi*100, 2),
                               initial_investment=initial_investment,
                               final_investment_value=final_investment_value,
                               average_win=round(average_win, 2),
                               average_loss=round(average_loss, 2),
                               win_rate=round(win_rate*100, 2),
                               num_trades=num_trades*2)



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
        selected_indicator_parameters = {
            indicator: indicator_parameters[indicator] for indicator in indicators}
        return render_template('build.html',
                               indicators=selected_indicator_parameters)


if __name__ == '__main__':
    app.run(port=10000)