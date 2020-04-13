from flask import Flask, request
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
            
if __name__ == '__main__':
    app.run(debug=True)