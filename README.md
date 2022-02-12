# algorand_transaction_export
Algorand transaction export utility in Python.  Attempts to support ASAs and Yieldly transactions.

## Usage
Run with no options to get command line parameters.  Parameters:

* wallet - ID of the wallet to generate the export for
* filename - Filename to write out the export to.  Should end in ".csv"

Example:

python algo_export.py O7265XHAG7DR3FDN2XPX4HZGCWDGCI7HPYEJ5Z3TQ43G6UC27I4LK7JM7E algo.csv

You will need Python 3 with pip.  It uses requests, so also do:
pip install requests

## Fields

* Timestamp - UTC date and time
* Type - Type of transaction (buy, transfer, reward, wallet fee (for subscribing/unsubscribing to ASAs) ...)
* Base Currency - Name of token for transaction.  e.g. For a buy, this is the token bought.
* Base Amount - Quantity for Base Currency - inclusive of fees
* Quote Currency (optional) - Name of token consumed.  e.g.  For a buy, this is the token used to buy the base currency.
* Quote Amount (optional) - Quantity of Quote Currency - inclusive of fees
* Fee Currency (optional) - Currency used to pay the transaction fees
* Fee Amount (optional) - Amount of transaction fees, less any rewards included (can be negative)
* From (optional) - ID of from currency or ASA
* To (optional) - ID of to currency or ASA
* ID (optional) - Transaction ID for final settlement (see below)
* Description (optional) - Any notes

Many transactions involve multiple events.  For instance, if you subscribe to and buy an ASA, there's the subscription event, a fee-payment event, payment for the token, receipt of the token, and then collection of residuals.  This tool will report those five events as three transactions: subscribe, purchase, collection of residuals.

At the end of the run it will either generate an error and stop, or output what it thinks your current balance is based on the transactions it saw.  This might end up being profit/loss seen since the first transaction it saw if for some reason the initial funding transaction for your wallet isn't seen.  This value is meant as a sanity check.

## Known Issues or Potential Issues

I tested this using my wallet (not the one below), and I've done no transfers FROM my wallet to another ALGO wallet.  I've only transferred funds in, bought and sold ASAs, and used Yieldly.  I'm not sure what a transfer out looks like (unless it looks just like staking Yieldly), so it might not properly identify those.

Sometimes, in rare cases, the quantity for an ASA bought will be off by a very small amount - the amount of one fee.  In the handful of ASA buys/sells that I have, this happened to me once.  I just corrected that one by hand in the output after being unable to figure out what it had missed.

I've not done everything there is to do on Yieldly, so it might mis-identify some things.  In particular, detecting and correctly labeling rewards is awkward.  It works for me, but might not always for you if you're doing something that looks different from what I encountered.

Staking Yieldly is reported as a transfer out of the wallet.  (That's actually how they look in the transactions: A transfer to some wallet address.  Weird...)  For me, the Yieldly and ALGO rewards are correctly identified.

It always generates the report for all transactions - no date bounding options have been included.  I'll likely add that in at some point but haven't yet.

## Disclaimer

This tool is provided as-is with no warranty under the MIT License.  If using for official purposes (e.g. tax reporting - the layout above is compatible with cryptotaxcalculator.io) YOU ARE EXPECTED TO VERIFY EACH AND EVERY TRANSACTION YOURSELF.  What you report on your taxes, or any other official documentation, is entirely your responsibility.

## Support

If you find it useful, feel free to shoot me an ALGO or two (or 10,000 ... I'm not picky):
O7265XHAG7DR3FDN2XPX4HZGCWDGCI7HPYEJ5Z3TQ43G6UC27I4LK7JM7E

## Acknowledgement

This project was derived from (although it's not almost completely different) this project:
https://github.com/TeneoPython01/algorand_txn_csv_exporter
