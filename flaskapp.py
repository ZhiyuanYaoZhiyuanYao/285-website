from flask import Flask, request, redirect,render_template_string
import requests
import json
import datetime


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # show html form
        return '''
            <h2>
            Warning: If any input is illegal, the output is not guaranteed. 
            </h2>
            <form method="post">
                </br></br> Stock Symbol </br> <input type="text" name="stockSymbol" /> 
                </br></br>Allotment </br><input type="text" name="allotment" />
                </br></br>Final Price </br><input type="text" name="finalPrice" />
                </br></br>Sell Commission</br><input type="text" name="sellCommission" />
                </br></br>Initial Price</br><input type="text" name="initialPrice" />
                </br></br>Buy Commision</br><input type="text" name="buyCommission" />
                </br></br>Tax Rate on Capital Gainn(%)</br><input type="text" name="taxRate" />
                </br></br><input type="submit" value="Calculate" />
            </form>
        '''
    elif request.method == 'POST':
        # calculate result
        stockSymbol = request.form.get('stockSymbol')
        allotment = int(request.form.get('allotment'))
        finalPrcie = float(request.form.get('finalPrice'))
        sellCommission = float(request.form.get('sellCommission'))
        initialPrice = float(request.form.get('initialPrice'))
        buyCommission = float(request.form.get('buyCommission'))
        taxRate = float(request.form.get('taxRate')) / 100

        proceeds = allotment * finalPrcie

        if len(stockSymbol) < 1:
            return "Stock Symbol needed!"

        if allotment <= 0:
            return "Allotment should be more than 0!"
        
        if finalPrcie <= 0 or initialPrice <= 0:
            return "Final or initial price shoule be more than 0!"
        
        if taxRate < 0:
            return "Tax rate should not be negative!"

        if finalPrcie > initialPrice:
            cost = allotment * initialPrice + buyCommission + sellCommission + taxRate * (allotment * (finalPrcie - initialPrice) - buyCommission - sellCommission)
        else:
            cost = allotment * initialPrice + buyCommission + sellCommission
            
        netProfit = proceeds - cost
        
        if cost != 0:
            returnOnInvestment = (netProfit / cost) * 100
        else:
            returnOnInvestment = "n/a"

        breakEvenPrice = initialPrice + (buyCommission + sellCommission) / allotment

        ## Formatting if needed
        proceeds = round(proceeds, 2)
        cost = round(cost,2)
        netProfit = round(netProfit,2)
        returnOnInvestment = round(returnOnInvestment,2)
        breakEvenPrice = round(breakEvenPrice,3)
        ##

        return 'Stock Symbol:  ' + stockSymbol \
            + '</br></br>Proceeds:  ' + str(proceeds) \
            + '</br></br>Cost:  ' + str(cost) \
            + '</br></br>Net Profit:  ' + str(netProfit) \
            + '</br></br>Return on investment(%):  ' + str(returnOnInvestment) \
            + '</br></br>Break-even final share price:  ' + str(breakEvenPrice)


@app.route('/info', methods=['GET', 'POST'])
def fetchStockInfo():
    stockInputTemplate = '''
        </br>
        <h3> Please enter a stock symbol below to retrieve the latest information </h3>
        <form action="/info" method="post">
                </br></br> Stock Symbol </br> <input type="text" name="stockSymbol" /> 
                </br></br><input type="submit" value="Enter" />
        </form>
        </br>
    '''

    if request.method == 'GET':
        # show html form
        return stockInputTemplate
    elif request.method == 'POST':
        # calculate result
        stockSymbol = request.form.get('stockSymbol')

        if len(stockSymbol) < 1:
            return "<h2 style='color:red'> Stock symbol is missing!" + stockInputTemplate
        elif len(stockSymbol) > 5:
            return "<h2 style='color:red'>Stock symbol too long! Please check and try again!" + stockInputTemplate
        
        ### Get the stock info
        url = "https://yahoo-finance15.p.rapidapi.com/api/yahoo/qu/quote/" + stockSymbol
        headers = {
            'x-rapidapi-host': "yahoo-finance15.p.rapidapi.com",
            'x-rapidapi-key': "9ae486e0d4msha3db6a5682c65c3p121be2jsn9ed77b53d91b"
        }
        response = requests.request("GET", url, headers=headers)

        if len(response.text) == 0:
            return "<h2 style='color:red'>Unable to find information. Please check your input and try again</br>" + stockInputTemplate

        jsonResponse = response.json()
        ### End of getting stock info
        if len(jsonResponse) == 0:
            return "<h2 style='color:red'>Unable to find information. Please check your input and try again</br>" + stockInputTemplate
        if jsonResponse[0]["quoteType"] != "EQUITY":
            return "<h2 style='color:red'>Your inquiry type is not equity, please enter an euqity symbol!" + stockInputTemplate
        
        ## Information to display
        # 1) current date and time
        dt = datetime.datetime.utcnow()
        # 2) longName (symbol)
        nameSymbol = "Stock Name: " + str(jsonResponse[0]["longName"]) + " (" + jsonResponse[0]["symbol"] + ")"
        # 3) regularMarketPrice 
        if len(str(jsonResponse[0]["regularMarketPrice"])) == 0:
            stockPrice = "<p style='color:red'> Unavailable"
        else:
            stockPrice = "Stock Price: " + str(round(jsonResponse[0]["regularMarketPrice"],2))
        # 4) regularMarketChange 
        if len(str(jsonResponse[0]["regularMarketChange"])) == 0:
            valueChange = "<p style='color:red'> Unavailable"
        else:
            rawRegularMarketChange = round(jsonResponse[0]["regularMarketChange"],3)
            stringFormatRegularMarketChange = str(rawRegularMarketChange) 
            if rawRegularMarketChange > 0:
                stringFormatRegularMarketChange = "+" + stringFormatRegularMarketChange 
            valueChange = "Value Change: " + stringFormatRegularMarketChange
        # 5) regularMarketChangePercent
        if len(str(jsonResponse[0]["regularMarketChangePercent"])) == 0:
             regularMarketChangePercent = "<p style='color:red'> Unavailable"
        else:
            rawRegularMarketChangePercent = round(jsonResponse[0]["regularMarketChangePercent"],2)
            stringFormatRegularMarketChangePercent = str(rawRegularMarketChangePercent) + "%"
            if rawRegularMarketChangePercent > 0:
                stringFormatRegularMarketChangePercent = "+" + stringFormatRegularMarketChangePercent
            valueChangePercentage = "Value Change Percentage: " + stringFormatRegularMarketChangePercent
        # 6) financialCurrency
        if len(str(jsonResponse[0]["financialCurrency"])) == 0:
            financialCurrency = "<p style='color:red'> Unavailable"
        else:
            financialCurrency = "Financial Currency: " + jsonResponse[0]["financialCurrency"]
        return render_template_string(
        '''
        <html><body>
        Current time:
        <p>{{dt}} (utc)</p>
        Your local browser time is:
        <p><span id="timeNow"></span></p>

        <p>{{nameSymbol}}</p>
        <p>{{stockPrice}}</p>
        <p>{{valueChange}}</p>
        <p>{{valueChangePercentage}}</p>
        <p>{{financialCurrency}}</p>

        <script>
        var elem = document.getElementById("timeNow")
        var now = new Date();
        var options = { month: 'short', day: '2-digit',
                        hour: 'numeric', minute: '2-digit', second:'2-digit' };
        elem.innerHTML = now.toLocaleString('en-us', options);
        </script>
        </body></html>
        ''',
        dt=dt, \
        nameSymbol=nameSymbol, \
        stockPrice=stockPrice, \
        valueChange=valueChange, \
        valueChangePercentage=valueChangePercentage, \
        financialCurrency=financialCurrency) \
        + stockInputTemplate

if __name__ == '__main__':
    app.run(debug=True)