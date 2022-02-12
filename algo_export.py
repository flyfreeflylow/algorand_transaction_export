import requests
from datetime import datetime
import time
import copy
import sys

if len(sys.argv) != 3:
    print("Usage: python algo_export.py wallet filename")
    sys.exit()

my_wallet = sys.argv[1]
filename = sys.argv[2]
print("Wallet: "+my_wallet)
print("Output File: "+filename)

with open(filename, 'w') as f:
    # Write header row
    print("Timestamp (UTC),Type,Base Currency,Base Amount,Quote Currency (Optional),Quote Amount (Optional),Fee Currency (Optional),Fee Amount (Optional),From (Optional),To (Optional),ID (Optional),Description (Optional)", file=f)

    iteration = 0

    # many tx consist of multiple rows that need to be accumulated
    current_tx = copy.deepcopy({"timestamp":"", "type":"", "currency":"", "amount":0, "from_currency":"", "from_amount":0, "fee_currency":"ALGO", "fee_amount": 0, "from":"", "to":"", "tx":"", "notes":""})
    looper = True
    tx_done = False
    check_asa_sell = False
    check_asa_buy = False
    balance = 0
    while looper:

        range_start = 100 * iteration
        range_increment = 100
        range_end = range_start + range_increment - 1

        my_range = str(range_start) + '/to/' + str(range_end)

        #this is the API:
        my_url = 'https://api.algoexplorer.io/v1/account/'+my_wallet+'/transactions/from/'+my_range

        r = requests.get(my_url).json()
        if len(r) == 0:
            # Need to check and process the current tx
            if tx_done:
                # Record it
                prettytime = time.strftime("%d/%m/%Y %H:%M:%S", time.gmtime(current_tx["timestamp"]))
                print('"'+prettytime+'","'+current_tx["type"]+'","'+current_tx["currency"]+'",'+str(current_tx["amount"])+',"'+current_tx["from_currency"]+'",'+str(current_tx["from_amount"])+',"'+current_tx["fee_currency"]+'",'+str(current_tx["fee_amount"])+',"'+current_tx["from"]+'","'+current_tx["to"]+'","'+current_tx["tx"]+'","'+current_tx["notes"]+'"', file=f)
            elif check_asa_sell and current_tx["from_amount"]==0:
                # Wallet Fee
                current_tx["currency"] = current_tx["from_currency"]
                current_tx["amount"] = current_tx["from_amount"]
                current_tx["from_currency"] = ""
                current_tx["from_amount"] = 0
                current_tx["type"] = "Wallet Fee"
                balance -= current_tx["fee_amount"]
                prettytime = time.strftime("%d/%m/%Y %H:%M:%S", time.gmtime(current_tx["timestamp"]))
                print('"'+prettytime+'","'+current_tx["type"]+'","'+current_tx["currency"]+'",'+str(current_tx["amount"])+',"'+current_tx["from_currency"]+'",'+str(current_tx["from_amount"])+',"'+current_tx["fee_currency"]+'",'+str(current_tx["fee_amount"])+',"'+current_tx["from"]+'","'+current_tx["to"]+'","'+current_tx["tx"]+'","'+current_tx["notes"]+'"', file=f)
            elif check_asa_sell:
                # Delegation/Pool/Farm
                current_tx["currency"] = current_tx["from_currency"]
                current_tx["amount"] = current_tx["from_amount"]
                current_tx["from_currency"] = ""
                current_tx["from_amount"] = 0
                current_tx["type"] = "Transfer"
                balance -= current_tx["fee_amount"]
                prettytime = time.strftime("%d/%m/%Y %H:%M:%S", time.gmtime(current_tx["timestamp"]))
                print('"'+prettytime+'","'+current_tx["type"]+'","'+current_tx["currency"]+'",'+str(current_tx["amount"])+',"'+current_tx["from_currency"]+'",'+str(current_tx["from_amount"])+',"'+current_tx["fee_currency"]+'",'+str(current_tx["fee_amount"])+',"'+current_tx["from"]+'","'+current_tx["to"]+'","'+current_tx["tx"]+'","'+current_tx["notes"]+'"', file=f)
            elif check_asa_buy:
                print(" ")
                print(current_tx)
                print(" ")
                print("Final transaction error - was checking for ASA buy - not sure what this is?")
            else:
                # Just record it
                balance -= current_tx["fee_amount"]
                prettytime = time.strftime("%d/%m/%Y %H:%M:%S", time.gmtime(current_tx["timestamp"]))
                print('"'+prettytime+'","'+current_tx["type"]+'","'+current_tx["currency"]+'",'+str(current_tx["amount"])+',"'+current_tx["from_currency"]+'",'+str(current_tx["from_amount"])+',"'+current_tx["fee_currency"]+'",'+str(current_tx["fee_amount"])+',"'+current_tx["from"]+'","'+current_tx["to"]+'","'+current_tx["tx"]+'","'+current_tx["notes"]+'"', file=f)

            looper = False
            continue

        for row in r:
            if tx_done:
                prettytime = time.strftime("%d/%m/%Y %H:%M:%S", time.gmtime(current_tx["timestamp"]))
                print('"'+prettytime+'","'+current_tx["type"]+'","'+current_tx["currency"]+'",'+str(current_tx["amount"])+',"'+current_tx["from_currency"]+'",'+str(current_tx["from_amount"])+',"'+current_tx["fee_currency"]+'",'+str(current_tx["fee_amount"])+',"'+current_tx["from"]+'","'+current_tx["to"]+'","'+current_tx["tx"]+'","'+current_tx["notes"]+'"', file=f)
                current_tx = copy.deepcopy({"timestamp":"", "type":"", "currency":"", "amount":0, "from_currency":"", "from_amount":0, "fee_currency":"ALGO", "fee_amount": 0, "from":"", "to":"", "tx":"", "notes":""})
                tx_done = False

            if check_asa_sell and row["type"]=="pay" and row["to"]==my_wallet:
                # ASA Sell (recorded as BUY ALGO paying with ASA)
                check_asa_sell = False
                tx_done = True
                current_tx["timestamp"] = row["timestamp"]
                current_tx["currency"] = "ALGO"
                current_tx["amount"] += row["amount"]/1000000.000000 + current_tx["fee_amount"]
                current_tx["from"] = row["from"]
                current_tx["to"] = row["to"]
                current_tx["tx"] = row["txid"]
                current_tx["type"] = "Buy"
                balance += current_tx["amount"]-current_tx["fee_amount"]
                continue
            elif check_asa_sell and row["type"]!="pay" and row["from"]==my_wallet:
                # Delegation/Pool/Farm deposit - record - current row is another tx
                check_asa_sell = False
                current_tx["timestamp"] = row["timestamp"]
                current_tx["currency"] = current_tx["from_currency"]
                current_tx["amount"] = current_tx["from_amount"]
                current_tx["from_currency"] = ""
                current_tx["from_amount"] = 0
                current_tx["type"] = "Transfer"
                balance -= current_tx["fee_amount"]
                prettytime = time.strftime("%d/%m/%Y %H:%M:%S", time.gmtime(current_tx["timestamp"]))
                print('"'+prettytime+'","'+current_tx["type"]+'","'+current_tx["currency"]+'",'+str(current_tx["amount"])+',"'+current_tx["from_currency"]+'",'+str(current_tx["from_amount"])+',"'+current_tx["fee_currency"]+'",'+str(current_tx["fee_amount"])+',"'+current_tx["from"]+'","'+current_tx["to"]+'","'+current_tx["tx"]+'","'+current_tx["notes"]+'"', file=f)
                current_tx = copy.deepcopy({"timestamp":"", "type":"", "currency":"", "amount":0, "from_currency":"", "from_amount":0, "fee_currency":"ALGO", "fee_amount": 0, "from":"", "to":"", "tx":"", "notes":""})
            elif check_asa_sell:
                # Unsubscribed - record - current row is another tx
                check_asa_sell = False
                current_tx["timestamp"] = row["timestamp"]
                current_tx["currency"] = current_tx["from_currency"]
                current_tx["amount"] = current_tx["from_amount"]
                current_tx["from_currency"] = ""
                current_tx["from_amount"] = 0
                current_tx["type"] = "Wallet Fee"
                balance -= current_tx["fee_amount"]
                prettytime = time.strftime("%d/%m/%Y %H:%M:%S", time.gmtime(current_tx["timestamp"]))
                print('"'+prettytime+'","'+current_tx["type"]+'","'+current_tx["currency"]+'",'+str(current_tx["amount"])+',"'+current_tx["from_currency"]+'",'+str(current_tx["from_amount"])+',"'+current_tx["fee_currency"]+'",'+str(current_tx["fee_amount"])+',"'+current_tx["from"]+'","'+current_tx["to"]+'","'+current_tx["tx"]+'","'+current_tx["notes"]+'"', file=f)
                current_tx = copy.deepcopy({"timestamp":"", "type":"", "currency":"", "amount":0, "from_currency":"", "from_amount":0, "fee_currency":"ALGO", "fee_amount": 0, "from":"", "to":"", "tx":"", "notes":""})

            if check_asa_buy and row["type"]=="axfer" and row["to"]==my_wallet and row["from"]!=my_wallet:
                # Buy ASA
                tx_done = True
                check_asa_buy = False
                current_tx["timestamp"] = row["timestamp"]
                current_tx["type"] = "Buy"
                current_tx["currency"] = row["unitName"]
                current_tx["amount"] += row["amount"]/1000000.000000
                current_tx["from"] = row["from"]
                current_tx["to"] = row["to"]
                current_tx["tx"] = row["txid"]
                current_tx["from_amount"] += current_tx["fee_amount"]
                current_tx["amount"] += current_tx["fee_amount"]
                balance -= current_tx["from_amount"]
                continue
            elif check_asa_buy:
                check_asa_buy = False

            if row["type"] == "pay":
                # pay can be transfers in, or purchases, or fees
                if row["to"] == my_wallet:
                    # Received - this is the finish of either a transfer in or Sell ASA
                    tx_done = True
                    current_tx["timestamp"] = row["timestamp"]
                    current_tx["currency"] = "ALGO"
                    current_tx["amount"] += row["amount"]/1000000.000000 + current_tx["fee_amount"]
                    current_tx["from"] = row["from"]
                    current_tx["to"] = row["to"]
                    current_tx["tx"] = row["txid"]
                    if current_tx["from_amount"]==0 and "fromDescription" in row and len(row["fromDescription"])>0:
                        current_tx["type"] = "Transfer"
                    elif current_tx["from_amount"]==0:
                        current_tx["type"] = "Reward"
                    else:
                        current_tx["type"] = "Buy"
                    balance += current_tx["amount"]-current_tx["fee_amount"]
                elif row["from"] == my_wallet:
                    # Payment sent - needs to be accumulated
                    current_tx["from_currency"] = "ALGO"
                    current_tx["from_amount"] += row["amount"]/1000000.000000
                    current_tx["from"] = row["from"]
                    current_tx["to"] = row["to"]
                    current_tx["tx"] = row["txid"]
                    check_asa_buy = True
            elif row["type"] == "axfer":
                # axfer can be the transfer after a buy or sell, lp/delegation, or fees
                if row["to"] == my_wallet and row["from"] != my_wallet:
                    # Reward
                    tx_done = True
                    current_tx["timestamp"] = row["timestamp"]
                    current_tx["type"] = "Reward"
                    current_tx["currency"] = row["unitName"]
                    current_tx["amount"] += row["amount"]/1000000.000000
                    current_tx["from"] = row["from"]
                    current_tx["to"] = row["to"]
                    current_tx["tx"] = row["txid"]
                    balance -= current_tx["fee_amount"]
                elif row["to"] == my_wallet and row["from"] == my_wallet:
                    # Fee for subscribing/unsubscribing an ASA
                    tx_done = True
                    current_tx["timestamp"] = row["timestamp"]
                    current_tx["type"] = "Wallet Fee"
                    current_tx["currency"] = row["unitName"]
                    current_tx["amount"] += row["amount"]/1000000.000000
                    current_tx["from"] = row["from"]
                    current_tx["to"] = row["to"]
                    current_tx["tx"] = row["txid"]
                    balance -= current_tx["fee_amount"]
                elif row["from"] == my_wallet:
                    # Sell ASA - the next line is the payment in algo - accumulate this row
                    current_tx["timestamp"] = row["timestamp"]
                    current_tx["from_currency"] = row["unitName"]
                    current_tx["from_amount"] += row["amount"]/1000000.000000
                    current_tx["from"] = row["from"]
                    current_tx["to"] = row["to"]
                    current_tx["tx"] = row["txid"]
                    check_asa_sell = True

            # Always accumulate the fee and reward
            current_tx["fee_amount"] += row["fee"]/1000000.000000
            if "fromRewards" in row:
                current_tx["fee_amount"] -= row["fromRewards"]/1000000.000000

        iteration = iteration + 1
    
    print("ALGO Balance: "+str(balance))
