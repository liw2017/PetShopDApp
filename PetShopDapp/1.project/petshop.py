'''
    APS1050 Final Project: Pet Shop DApp with four transfered features
    Renjie Dai <renjie.dai@mail.utoronto.ca>
    Wenxin Li <wency.li@mail.utoronto.ca>
    
'''



from flask import Flask, render_template, request, redirect, url_for, session
import json
from web3 import Web3, HTTPProvider


# compile your smart contract with truffle first 
truffleFile = json.load(open('./build/contracts/Petshop.json'))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']



# web3.py instance
w3 = Web3(HTTPProvider("http://localhost:7545/"))

# setting default account
w3account = w3.eth.accounts
# Instantiate and deploy contract
contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get transaction hash from deployed contract
tx_hash = contract.constructor().transact({'from': w3account[0]})

# Get tx receipt, then get contract address
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt['contractAddress']

contract_instance = w3.eth.contract(abi=abi, address=contract_address)



app = Flask(__name__)

#set secret key for session
app.secret_key = 'SUPER_SECRET_KEY'

#read peyshop data
with open('pets.json') as petdatajson:
    petdata = json.load(petdatajson)

petadd = []
pet = []
purchasedpet = []
msg = {}

#index page, sign in your account
@app.route("/")
def login():
    if session:
        pass
    else:
        session['accountid'] = 0
    return render_template('login.html', w3account=w3account,title='login')

#put account address (public key) in session, then redirect to petshop page
@app.route("/loginsuccess", methods = ['POST'])
def loginsuccess():
    actkey = request.form.get('accountkey')
    session['accountid'] = int(actkey)    
    return redirect(url_for('petshop'))

#petshop page, adopt pets or vote for your favorite pet
@app.route('/petshop', methods=['GET', 'POST'])
def petshop():
    if request.method == 'POST' :
        if request.form.get('petid'):
            contract_instance.functions.adopt(int(request.form.get('petid'))).transact({'from': w3account[session['accountid']]})
    red = contract_instance.functions.getAdopters().call()
    votestatus = contract_instance.functions.voters(w3account[session['accountid']]).call()
    liked = {}
    for i in range(16):
        candiList = contract_instance.functions.candidates(i+1).call()
        liked[candiList[0]-1] = [candiList[1],candiList[2]]
    return render_template('petshop.html', 
                           petdata=petdata, red=red, 
                           votestatus=votestatus, liked=liked, title='Pet Shop')

#vote your favorite pet, then redirect to petshop page
@app.route('/vote', methods=['POST'])
def vote():
    contract_instance.functions.vote(int(request.form.get('petid'))+1).transact({'from': w3account[session['accountid']]})
    return redirect(url_for('petshop'))


#Add pets
@app.route('/addpet', methods=['GET','POST'])
def addpet():
    msg['error'] = ''
    request_mothods = request.method
    if request_mothods == 'POST':
        newid = len(petadd)
        newname = request.form.get('petname')
        newbreed = request.form.get('petbreed')
        newage = request.form.get('petage')
        newlocation = request.form.get('petlocation')
        newprice = request.form.get('petprice')
        if newbreed == "Scottish Terrier" :
            newpicture = "static/scottish-terrier.jpeg"
        elif newbreed == "French Bulldog":
            newpicture = "static/french-bulldog.jpeg"
        elif newbreed == "Boxer":
            newpicture = "static/boxer.jpeg"
        else:
            newpicture = "static/golden-retriever.jpeg"
        if  newname and newbreed and newage and newlocation and newprice:
            newpet={
                    "id": newid,
                    "name": newname,
                    "picture": newpicture,
                    "age": newage,
                    "breed": newbreed,
                    "location": newlocation,
                    "price": newprice
                    }
            petadd.append(newpet)
            tx_hash1 = contract_instance.functions.createPet(newname,newbreed,int(newage),newlocation, newpicture,int(newprice)).transact({'from': w3account[session['accountid']]})

            tx_receipt1 = w3.eth.getTransactionReceipt(tx_hash1)
            
            eventhold = contract.events.PetCreated().processReceipt(tx_receipt1)
                        
            event = dict(eventhold[0]['args'])
            
            print(dict(eventhold[0]['args']))
            
            pet.append(event)
            msg['error'] = 'Submit Success!'
        else:
            msg['error'] = 'Submit Failed: incomplete pet information!'

    return render_template('addpet.html',petadd=petadd,pet=pet,msg=msg,title='Add Pet')



#buy pets
@app.route('/buypet', methods=['GET','POST'])
def buypet():
    msg['error'] = ''
    purchaseId = 0    
    request_mothods = request.method
    if request_mothods == 'POST':
        petId = request.form.get('petId')
        petId = int(petId)
        price = int(pet[int(petId)-1]['price'])
        if pet[petId-1]['owner'] == w3account[session['accountid']]:
            msg['error'] = 'Failed: You cannot buy your own pets.'
        else:
            contract_instance.functions.purchasePet(petId).transact({'from': w3account[session['accountid']],'value': price*1000000000000000000})
            pet[petId-1]['purchased'] = True
            pet[petId-1]['owner'] = w3account[session['accountid']]
    return render_template('buypet.html',pet=pet,purchaseId=purchaseId, msg=msg, title='Buy Pet')



#donate ehter
@app.route('/donate', methods=['GET','POST'])
def donate():
    donate_value=0
    con_balance = w3.eth.get_balance(contract_address)
    request_mothods = request.method
    if request_mothods == 'POST':
        donate_value = request.form.get("donatevalue")
        if donate_value:
            donate_value = int(donate_value)
            sendEth = w3.eth.send_transaction({
                                    'from' :  w3account[session['accountid']],
                                    'to': contract_address,
                                    'value': donate_value*1000000000
                                    })
            sendEth_receipt = w3.eth.getTransactionReceipt(sendEth)
            if sendEth_receipt:
                con_balance = w3.eth.get_balance(contract_address)
                return render_template('donatesuccess.html',con_balance=con_balance)
    else:
        pass
    return render_template('donate.html',con_balance=con_balance,donate_value=donate_value,title='Donate')



@app.route('/donatesuccess', methods=['GET','POST'])
def donatesuccess():
    con_balance = w3.eth.get_balance(contract_address)
    return render_template('donatesuccess.html',con_balance=con_balance)


if __name__ == '__main__':
    app.run(debug=False ,port=8080)
