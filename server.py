
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for
import random
import string

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.74.246.148/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.74.246.148/proj1part2"
#
DATABASEURI = "postgresql://vl2420:6609@34.74.246.148/proj1part2"
#DATABASEURI = "postgresql://vl2420:6609@34.73.37.51/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()
  
  
  

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

@app.route('/depositUser', methods=['POST'])
def depositUser():
    
    depositAmt = request.form['amount']
    g.conn.execute("DELETE FROM deposits_user WHERE ABS(ssn - (SELECT ssn FROM users WHERE name=\'{}\'))<= 10".format(userInput))
    g.conn.execute("INSERT INTO deposits_user SELECT ssn, bid, %s FROM users NATURAL JOIN bank WHERE name=\'{}\'".format(userInput), depositAmt)
    g.conn.execute("UPDATE users M set walletbal=M.walletbal-%s WHERE M.name=\'{}\'".format(userInput), depositAmt)
    g.conn.execute("UPDATE bank M set balance=M.balance+%s WHERE M.name=\'{}\'".format(userInput), depositAmt)
    
    
    return redirect(url_for('book'))
    #return render_template("book.html",**dict(userName="0",walletBalance=0, bankBalance=1))
    
@app.route('/depositcExchange', methods=['POST'])
def depositcExchange():
    
    depositAmt = request.form['amount']
    print("The type!")
    print(type(depositAmt))
    g.conn.execute("UPDATE deposits_cexchange set deposit=%s WHERE bid=(SELECT bid FROM users NATURAL JOIN bank WHERE name=\'{}\')".format(userInput),depositAmt)
    g.conn.execute("UPDATE CryptoExchange M set usdbal=M.usdbal+%s WHERE M.name=\'{}\'".format(userInput), depositAmt)
    g.conn.execute("UPDATE bank M set balance=M.balance-%s WHERE M.name=\'{}\'".format(userInput), depositAmt)
    
    
    return redirect(url_for('book'))
    #return render_template("book.html",**dict(userName="0",walletBalance=0, bankBalance=1))

@app.route('/withdrawUser', methods=['POST'])
def withdrawUser():
    
    withdrawAmt = request.form['amount']
    g.conn.execute("DELETE FROM withdraws_user WHERE ABS(ssn - (SELECT ssn FROM users WHERE name=\'{}\'))<= 10".format(userInput))
    g.conn.execute("INSERT INTO withdraws_user SELECT ssn, bid, %s FROM users NATURAL JOIN bank WHERE name=\'{}\'".format(userInput), withdrawAmt)
    g.conn.execute("UPDATE users M set walletbal=M.walletbal+%s WHERE M.name=\'{}\'".format(userInput), withdrawAmt)
    g.conn.execute("UPDATE bank M set balance=M.balance-%s WHERE M.name=\'{}\'".format(userInput), withdrawAmt)
    
    
    return redirect(url_for('book'))

@app.route('/withdrawcExchange', methods=['POST'])
def withdrawcExchange():
    
    withdrawAmt = request.form['amount']
    g.conn.execute("UPDATE withdraws_cexchange set withdraw=%s WHERE bid=(SELECT bid FROM users NATURAL JOIN bank WHERE name=\'{}\')".format(userInput),withdrawAmt)
    g.conn.execute("UPDATE CryptoExchange M set usdbal=M.usdbal-%s WHERE M.name=\'{}\'".format(userInput), withdrawAmt)
    g.conn.execute("UPDATE bank M set balance=M.balance+%s WHERE M.name=\'{}\'".format(userInput), withdrawAmt)
    
    
    return redirect(url_for('book'))

@app.route('/depositETHWallet', methods=['POST'])
def depositETHWallet():
    
    depositAmt = request.form['amount']
    g.conn.execute("UPDATE deposits_dwallet set depositeth=%s, depositbtc=0 WHERE address=(SELECT address from users NATURAL JOIN owns WHERE name=\'{}\')".format(userInput),depositAmt)
    g.conn.execute("UPDATE CryptoExchange M set ethbal=M.ethbal-%s WHERE M.name=\'{}\'".format(userInput), depositAmt)
    g.conn.execute("UPDATE digital_wallet M set ethbal=M.ethbal+%s WHERE M.address=(SELECT address from users NATURAL JOIN owns WHERE name=\'{}\')".format(userInput), depositAmt)
    
    return redirect(url_for('book'))

@app.route('/depositBTCWallet', methods=['POST'])
def depositBTCWallet():
    
    depositAmt = request.form['amount']
    g.conn.execute("UPDATE deposits_dwallet set depositeth=0, depositbtc=%s WHERE address=(SELECT address from users NATURAL JOIN owns WHERE name=\'{}\')".format(userInput),depositAmt)
    g.conn.execute("UPDATE CryptoExchange M set btcbal=M.btcbal-%s WHERE M.name=\'{}\'".format(userInput), depositAmt)
    g.conn.execute("UPDATE digital_wallet M set btcbal=M.btcbal+%s WHERE M.address=(SELECT address from users NATURAL JOIN owns WHERE name=\'{}\')".format(userInput), depositAmt)
    
    return redirect(url_for('book'))

@app.route('/withdrawETHWallet', methods=['POST'])
def withdrawETHWallet():
    
    withdrawAmt = request.form['amount']
    g.conn.execute("UPDATE withdraws_dwallet set withdraweth=%s, withdrawbtc=0 WHERE address=(SELECT address from users NATURAL JOIN owns WHERE name=\'{}\')".format(userInput),withdrawAmt)
    g.conn.execute("UPDATE CryptoExchange M set ethbal=M.ethbal+%s WHERE M.name=\'{}\'".format(userInput), withdrawAmt)
    g.conn.execute("UPDATE digital_wallet M set ethbal=M.ethbal-%s WHERE M.address=(SELECT address from users NATURAL JOIN owns WHERE name=\'{}\')".format(userInput), withdrawAmt)
    
    return redirect(url_for('book'))

@app.route('/withdrawBTCWallet', methods=['POST'])
def withdrawBTCWallet():
    
    withdrawAmt = request.form['amount']
    g.conn.execute("UPDATE withdraws_dwallet set withdraweth=0, withdrawbtc=%s WHERE address=(SELECT address from users NATURAL JOIN owns WHERE name=\'{}\')".format(userInput),withdrawAmt)
    g.conn.execute("UPDATE CryptoExchange M set btcbal=M.btcbal+%s WHERE M.name=\'{}\'".format(userInput), withdrawAmt)
    g.conn.execute("UPDATE digital_wallet M set btcbal=M.btcbal-%s WHERE M.address=(SELECT address from users NATURAL JOIN owns WHERE name=\'{}\')".format(userInput), withdrawAmt)
    
    return redirect(url_for('book'))


@app.route('/convertUSDtoBTC', methods=['POST'])
def convertUSDtoBTC():
    
    convertAmt = request.form['amount']
    transNumbers=[]
    cursor = g.conn.execute("SELECT trans_number FROM convert")
    for result in cursor:
        transNumbers.append(result['trans_number'])
    cursor.close()
    
    newTransNumber=1
    while(newTransNumber in transNumbers):
        newTransNumber=newTransNumber+1
    
    rates=[]
    cursor = g.conn.execute("SELECT btc_usd_rate, eth_usd_rate FROM cryptocurrencies WHERE cname='bitcoin'")
    for result in cursor:
        rates.append(result['btc_usd_rate'])
        rates.append(result['eth_usd_rate'])
    cursor.close()
    BTCgained=float(convertAmt)/rates[0]
    
    g.conn.execute("INSERT INTO convert VALUES('bitcoin', {}, (SELECT userid FROM cryptoexchange WHERE name=\'{}\'),0,0,{})".format(newTransNumber,userInput,convertAmt))
    g.conn.execute("UPDATE CryptoExchange M set usdbal=M.usdbal-%s WHERE M.name=\'{}\'".format(userInput), convertAmt)
    g.conn.execute("UPDATE CryptoExchange M set btcbal=M.btcbal+%s WHERE M.name=\'{}\'".format(userInput), BTCgained)
    
    return redirect(url_for('book'))

@app.route('/convertBTCtoUSD', methods=['POST'])
def convertBTCtoUSD():
    
    convertAmt = request.form['amount']
    transNumbers=[]
    cursor = g.conn.execute("SELECT trans_number FROM convert")
    for result in cursor:
        transNumbers.append(result['trans_number'])
    cursor.close()
    
    newTransNumber=1
    while(newTransNumber in transNumbers):
        newTransNumber=newTransNumber+1
    
    rates=[]
    cursor = g.conn.execute("SELECT btc_usd_rate, eth_usd_rate FROM cryptocurrencies WHERE cname='bitcoin'")
    for result in cursor:
        rates.append(result['btc_usd_rate'])
        rates.append(result['eth_usd_rate'])
    cursor.close()
    USDgained=float(convertAmt)*rates[0]
    
    g.conn.execute("INSERT INTO convert VALUES('usd', {}, (SELECT userid FROM cryptoexchange WHERE name=\'{}\'),{},0,0)".format(newTransNumber,userInput,convertAmt))
    g.conn.execute("UPDATE CryptoExchange M set usdbal=M.usdbal+%s WHERE M.name=\'{}\'".format(userInput), USDgained)
    g.conn.execute("UPDATE CryptoExchange M set btcbal=M.btcbal-%s WHERE M.name=\'{}\'".format(userInput), convertAmt)
    
    return redirect(url_for('book'))

@app.route('/convertUSDtoETH', methods=['POST'])
def convertUSDtoETH():
    
    convertAmt = request.form['amount']
    transNumbers=[]
    cursor = g.conn.execute("SELECT trans_number FROM convert")
    for result in cursor:
        transNumbers.append(result['trans_number'])
    cursor.close()
    
    newTransNumber=1
    while(newTransNumber in transNumbers):
        newTransNumber=newTransNumber+1
    
    rates=[]
    cursor = g.conn.execute("SELECT btc_usd_rate, eth_usd_rate FROM cryptocurrencies WHERE cname='bitcoin'")
    for result in cursor:
        rates.append(result['btc_usd_rate'])
        rates.append(result['eth_usd_rate'])
    cursor.close()
    ETHgained=float(convertAmt)/rates[1]
    
    g.conn.execute("INSERT INTO convert VALUES('etherium', {}, (SELECT userid FROM cryptoexchange WHERE name=\'{}\'),0,0,{})".format(newTransNumber,userInput,convertAmt))
    g.conn.execute("UPDATE CryptoExchange M set usdbal=M.usdbal-%s WHERE M.name=\'{}\'".format(userInput), convertAmt)
    g.conn.execute("UPDATE CryptoExchange M set ethbal=M.ethbal+%s WHERE M.name=\'{}\'".format(userInput), ETHgained)
    
    return redirect(url_for('book'))

@app.route('/convertETHtoUSD', methods=['POST'])
def convertETHtoUSD():
    
    convertAmt = request.form['amount']
    transNumbers=[]
    cursor = g.conn.execute("SELECT trans_number FROM convert")
    for result in cursor:
        transNumbers.append(result['trans_number'])
    cursor.close()
    
    newTransNumber=1
    while(newTransNumber in transNumbers):
        newTransNumber=newTransNumber+1
    
    rates=[]
    cursor = g.conn.execute("SELECT btc_usd_rate, eth_usd_rate FROM cryptocurrencies WHERE cname='bitcoin'")
    for result in cursor:
        rates.append(result['btc_usd_rate'])
        rates.append(result['eth_usd_rate'])
    cursor.close()
    USDgained=float(convertAmt)*rates[1]
    
    g.conn.execute("INSERT INTO convert VALUES('usd', {}, (SELECT userid FROM cryptoexchange WHERE name=\'{}\'),0,{},0)".format(newTransNumber,userInput,convertAmt))
    g.conn.execute("UPDATE CryptoExchange M set usdbal=M.usdbal+%s WHERE M.name=\'{}\'".format(userInput), USDgained)
    g.conn.execute("UPDATE CryptoExchange M set ethbal=M.ethbal-%s WHERE M.name=\'{}\'".format(userInput), convertAmt)
    
    return redirect(url_for('book'))

@app.route('/convertETHtoBTC', methods=['POST'])
def convertETHtoBTC():
    
    convertAmt = request.form['amount']
    transNumbers=[]
    cursor = g.conn.execute("SELECT trans_number FROM convert")
    for result in cursor:
        transNumbers.append(result['trans_number'])
    cursor.close()
    
    newTransNumber=1
    while(newTransNumber in transNumbers):
        newTransNumber=newTransNumber+1
    
    rates=[]
    cursor = g.conn.execute("SELECT btc_usd_rate, eth_usd_rate, btc_eth_rate FROM cryptocurrencies WHERE cname='bitcoin'")
    for result in cursor:
        rates.append(result['btc_usd_rate'])
        rates.append(result['eth_usd_rate'])
        rates.append(result['btc_eth_rate'])
    cursor.close()
    BTCgained=float(convertAmt)/rates[2]
    
    g.conn.execute("INSERT INTO convert VALUES('bitcoin', {}, (SELECT userid FROM cryptoexchange WHERE name=\'{}\'),0,{},0)".format(newTransNumber,userInput,convertAmt))
    g.conn.execute("UPDATE CryptoExchange M set btcbal=M.btcbal+%s WHERE M.name=\'{}\'".format(userInput), BTCgained)
    g.conn.execute("UPDATE CryptoExchange M set ethbal=M.ethbal-%s WHERE M.name=\'{}\'".format(userInput), convertAmt)
    
    return redirect(url_for('book'))

@app.route('/convertBTCtoETH', methods=['POST'])
def convertBTCtoETH():
    
    convertAmt = request.form['amount']
    transNumbers=[]
    cursor = g.conn.execute("SELECT trans_number FROM convert")
    for result in cursor:
        transNumbers.append(result['trans_number'])
    cursor.close()
    
    newTransNumber=1
    while(newTransNumber in transNumbers):
        newTransNumber=newTransNumber+1
    
    rates=[]
    cursor = g.conn.execute("SELECT btc_usd_rate, eth_usd_rate, btc_eth_rate FROM cryptocurrencies WHERE cname='bitcoin'")
    for result in cursor:
        rates.append(result['btc_usd_rate'])
        rates.append(result['eth_usd_rate'])
        rates.append(result['btc_eth_rate'])
    cursor.close()
    ETHgained=float(convertAmt)*rates[2]
    
    g.conn.execute("INSERT INTO convert VALUES('etherium', {}, (SELECT userid FROM cryptoexchange WHERE name=\'{}\'),{},0,0)".format(newTransNumber,userInput,convertAmt))
    g.conn.execute("UPDATE CryptoExchange M set btcbal=M.btcbal-%s WHERE M.name=\'{}\'".format(userInput), convertAmt)
    g.conn.execute("UPDATE CryptoExchange M set ethbal=M.ethbal+%s WHERE M.name=\'{}\'".format(userInput), ETHgained)
    
    return redirect(url_for('book'))

@app.route('/sendBetweenWallets', methods=['POST'])
def sendBetweenWallets():
    
    currencyType = request.form['currencyType']
    transferAmount = request.form['amount']
    recipientAddress =request.form['hashAddress']
    
    transferAmount=float(transferAmount)
    
    ethSentVal=0
    btcSentVal=0
    nft1SentVal=0
    nft2SentVal=0
    nft3SentVal=0
    address1Val=""
    contractHash=''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))
    
    cursor = g.conn.execute("SELECT address FROM users NATURAL JOIN owns WHERE name=\'{}\'".format(userInput))
    for result in cursor:
        address1Val=result['address']
    cursor.close()
    
    if (currencyType=='eth'):
        ethSentVal+=transferAmount
    elif(currencyType=='btc'):
        btcSentVal+=transferAmount
    elif(currencyType=='nft1'):
        nft1SentVal+=transferAmount
    elif(currencyType=='nft2'):
        nft2SentVal+= transferAmount
    elif(currencyType=='nft3'):
        nft3SentVal+=transferAmount
    else:
        ethSentVal=0
    
    g.conn.execute("INSERT INTO sends_to VALUES(\'{}\',\'{}\',{},{},{},{},{},\'{}\')".format(address1Val,recipientAddress,ethSentVal,
                                                                                 btcSentVal,nft1SentVal,nft2SentVal,
                                                                                 nft3SentVal,contractHash))
    g.conn.execute("UPDATE digital_wallet M set btcbal=M.btcbal+{},ethbal=M.ethbal+{},nft1bal=M.nft1bal+{},nft2bal=M.nft2bal+{},nft3bal=M.nft3bal+{} WHERE M.address=\'{}\'".format(btcSentVal, ethSentVal,nft1SentVal, nft2SentVal,nft3SentVal,recipientAddress))
    g.conn.execute("UPDATE digital_wallet M set btcbal=M.btcbal-{},ethbal=M.ethbal-{},nft1bal=M.nft1bal-{},nft2bal=M.nft2bal-{},nft3bal=M.nft3bal-{} WHERE M.address=\'{}\'".format(btcSentVal, ethSentVal,
                                                                                                                                                                                nft1SentVal, nft2SentVal,
                                                                                                                                                                                nft3SentVal, address1Val))
    return redirect(url_for('book'))


@app.route('/book', methods=['POST', 'GET'])
def book():
    if request.method=='POST':
        outputs=[]
        global userInput
        userInput = request.form['name']
        #outputs.append(g.conn.execute("SELECT M.walletbal FROM users M WHERE M.name=%s", userInput))
        #outputs.append(g.conn.execute("SELECT balance FROM users NATURAL JOIN bank WHERE name=%s", userInput))
        #cursor = g.conn.execute("SELECT M.walletbal FROM users M WHERE M.name='{}'".format(userInput))
        cursor = g.conn.execute("SELECT walletbal FROM users NATURAL JOIN bank WHERE name=\'{}\'".format(userInput))
        for result in cursor:
            outputs.append(result['walletbal'])  # can also be accessed using result[0]
        cursor.close()
    
        #cursor = g.conn.execute("SELECT balance FROM users NATURAL JOIN bank WHERE name='{}'".format(userInput))
        cursor = g.conn.execute("SELECT balance FROM users NATURAL JOIN bank WHERE name=\'{}\'".format(userInput))
        for result in cursor:
            outputs.append(result['balance'])
        cursor.close()
        
        cursor = g.conn.execute("SELECT usdbal, ethbal, btcbal FROM CryptoExchange WHERE name=\'{}\'".format(userInput))
        for result in cursor:
            outputs.append(result['usdbal'])
            outputs.append(result['ethbal'])
            outputs.append(result['btcbal'])
        cursor.close()

        cursor = g.conn.execute("SELECT btc_usd_rate, eth_usd_rate FROM cryptocurrencies WHERE cname='bitcoin'")
        for result in cursor:
            outputs.append(result['btc_usd_rate'])
            outputs.append(result['eth_usd_rate'])
        cursor.close()
        
        cursor = g.conn.execute("SELECT address FROM users NATURAL JOIN owns WHERE name=\'{}\'".format(userInput))
        for result in cursor:
            outputs.append(result['address'])
        cursor.close()

        cursor = g.conn.execute("SELECT ethbal,btcbal,nft1bal,nft2bal,nft3bal FROM users NATURAL JOIN owns NATURAL JOIN digital_wallet WHERE name=\'{}\'".format(userInput))
        for result in cursor:
            outputs.append(result['ethbal'])
            outputs.append(result['btcbal'])
            outputs.append(result['nft1bal'])
            outputs.append(result['nft2bal'])
            outputs.append(result['nft3bal'])
        cursor.close()
    
        outputdict = dict(userName=userInput,walletBalance=outputs[0], bankBalance=outputs[1],
                          cExchangeUSD=outputs[2],cExchangeETH=outputs[3],cExchangeBTC=outputs[4],
                          BTCPrice=outputs[5],ETHPrice=outputs[6],walletAddress=outputs[7],
                          digitalWalletETH=outputs[8],digitalWalletBTC=outputs[9],
                          digitalWalletNFT1=outputs[10],digitalWalletNFT2=outputs[11],
                          digitalWalletNFT3=outputs[12])
        print(outputdict)
        return render_template("book.html", **outputdict)
    else:
        #outputs.append(g.conn.execute("SELECT M.walletbal FROM users M WHERE M.name=%s", userInput))
        #outputs.append(g.conn.execute("SELECT balance FROM users NATURAL JOIN bank WHERE name=%s", userInput))
        #cursor = g.conn.execute("SELECT M.walletbal FROM users M WHERE M.name='{}'".format(userInput))
        outputs=[]
        cursor = g.conn.execute("SELECT walletbal FROM users NATURAL JOIN bank WHERE name=\'{}\'".format(userInput))
        for result in cursor:
            outputs.append(result['walletbal'])  # can also be accessed using result[0]
        cursor.close()
    
        #cursor = g.conn.execute("SELECT balance FROM users NATURAL JOIN bank WHERE name='{}'".format(userInput))
        cursor = g.conn.execute("SELECT balance FROM users NATURAL JOIN bank WHERE name=\'{}\'".format(userInput))
        for result in cursor:
            outputs.append(result['balance'])  # can also be accessed using result[0]
        cursor.close()
        
        cursor = g.conn.execute("SELECT usdbal, ethbal, btcbal FROM CryptoExchange WHERE name=\'{}\'".format(userInput))
        for result in cursor:
            outputs.append(result['usdbal'])
            outputs.append(result['ethbal'])
            outputs.append(result['btcbal'])
        cursor.close()
    
        cursor = g.conn.execute("SELECT btc_usd_rate, eth_usd_rate FROM cryptocurrencies WHERE cname='bitcoin'")
        for result in cursor:
            outputs.append(result['btc_usd_rate'])
            outputs.append(result['eth_usd_rate'])
        cursor.close()
    
        cursor = g.conn.execute("SELECT address FROM users NATURAL JOIN owns WHERE name=\'{}\'".format(userInput))
        for result in cursor:
            outputs.append(result['address'])
        cursor.close()
    
        cursor = g.conn.execute("SELECT ethbal,btcbal,nft1bal,nft2bal,nft3bal FROM users NATURAL JOIN owns NATURAL JOIN digital_wallet WHERE name=\'{}\'".format(userInput))
        for result in cursor:
            outputs.append(result['ethbal'])
            outputs.append(result['btcbal'])
            outputs.append(result['nft1bal'])
            outputs.append(result['nft2bal'])
            outputs.append(result['nft3bal'])
        cursor.close()
    
        outputdict = dict(userName=userInput,walletBalance=outputs[0], bankBalance=outputs[1],
                          cExchangeUSD=outputs[2],cExchangeETH=outputs[3],cExchangeBTC=outputs[4],
                          BTCPrice=outputs[5],ETHPrice=outputs[6],walletAddress=outputs[7],
                          digitalWalletETH=outputs[8],digitalWalletBTC=outputs[9],
                          digitalWalletNFT1=outputs[10],digitalWalletNFT2=outputs[11],
                          digitalWalletNFT3=outputs[12])
        print(outputdict)
        return render_template("book.html", **outputdict)


@app.route('/bookInput', methods=['POST'])
def bookInput():
    #if request.method=='POST':
        #return redirect(url_for('book'))
    return book()


@app.route('/testing')
def testing():
  return render_template("testing.html")


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
