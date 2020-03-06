import os
from bitcoin.wallet import CBitcoinSecret, bitcoin, P2PKHBitcoinAddress, CBitcoinAddress
from bitcoin.core import b2x, lx, CMutableTxIn, CMutableTxOut, COutPoint, CMutableTransaction, x, b2lx
from bitcoin.core.script import CScript, SignatureHash, SIGHASH_ALL
import xlwings as xw
import requests
import time
import datetime
import pandas as pd
import uuid
import hashlib


# hardcode the testnet for now
bitcoin.SelectParams('testnet')

DABL_URL = 'https://console.projectdabl.com'


def world():
    _ = xw.Book.caller()
    # dummy function to test xlwings connectivity


def get_settings(wb):
    ws = wb.sheets['Settings']
    settings = {
        'ledger_id': ws.range('A2').value,
        'admin_jwt': ws.range('A4').value,
        'user_jwt': ws.range('A6').value,
        'key_file': ws.range('A8').value,
        'network': ws.range('A10').value,
        'token': ws.range('A12').value
    }
    return settings


def get_setting(setting, wb):
    settings = get_settings(wb)
    return settings.get(setting, None)


def update_utxos():
    wb = xw.Book.caller()
    ws_utxos = wb.sheets['UTXOs']
    ws_utxos.range('C1').value = 'Updating...'
    settings = get_settings(wb)
    key_file = settings.get('key_file', None)
    blockcypher_token = settings.get('token', None)
    network = settings.get('network', None)
    if not key_file or not blockcypher_token or not network:
        ws_utxos.range('C1').value = 'Error'
        return
    addresses = get_public_addresses(key_file)
    str_addresses = [str(addr) for addr in addresses]

    utxos = []
    for addr in str_addresses:
        utxos.extend(fetch_utxos(addr, blockcypher_token, network))
        time.sleep(1)

    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)

    dabl_utxos = dabl_send_search('Bitcoin.Transaction', 'UTXO', ledger_id, user_jwt)

    utxo_dict = { f"{utxo['txHash']}_{utxo['outputIdx']}" : utxo for utxo in utxos }
    utxo_dabl_dict = { f"{utxo['contractData']['utxoData']['txHash']}_{utxo['contractData']['utxoData']['outputIdx']}" : utxo for utxo in dabl_utxos }

    utxo_key_set = set(utxo_dict.keys())
    utxo_dabl_key_set = set(utxo_dabl_dict.keys())

    utxos_to_delete = utxo_dabl_key_set.difference(utxo_key_set)
    utxos_to_add = utxo_key_set.difference(utxo_dabl_key_set)

    contracts_to_archive = [v for k, v in utxo_dabl_dict.items() if k in utxos_to_delete]
    archive_commands = dabl_archive(contracts_to_archive)
    archive_resp = dabl_send_command(archive_commands, ledger_id, user_jwt)

    utxos_to_create = [v for k, v in utxo_dict.items() if k in utxos_to_add]
    create_commands = dabl_create_utxos(utxos_to_create, get_user_party(wb))
    create_resp = dabl_send_command(create_commands, ledger_id, user_jwt)

    df = pd.DataFrame(utxos)
    ws_utxos.range('C9').expand().value = ""
    ws_utxos.range('C9').value = df.values
    ws_utxos.range('C1').value = 'Done' if create_resp.status_code == 200 and archive_resp.status_code == 200 else 'Error'
    ws_utxos.range('C2').value = f'Last Update: {datetime.datetime.now()}'


def dabl_archive(contracts):
    commands = []
    for contract in contracts:
        command = {
            'contractId': contract['contractId'],
            'templateId': contract['templateId'].split('@', 1)[0],
            'choice': "Archive",
            'choiceArgument': {}
        }
        commands.append(command)

    archive_commands = {
        'workflowId': "archive",
        'commandId': str(uuid.uuid4()),
        'commands': commands
    }
    return archive_commands


def dabl_create_utxos(utxos, party):
    commands = []
    for utxo in utxos:
        command = {
            'createArguments': {
                'operator': party,
                'user': party,
                'utxoData': utxo,
            },
            'templateId': 'Bitcoin.Transaction.UTXO'
        }
        commands.append(command)

    create_commands = {
        'workflowId': "create-utxos",
        'commandId': str(uuid.uuid4()),
        'commands': commands
    }
    return create_commands


def update_parties():
    wb = xw.Book.caller()
    ws_settings = wb.sheets['Settings']
    ws_settings.range('B17').value = 'Updating...'

    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    admin_jwt = settings.get('admin_jwt', None)
    user_jwt = settings.get('user_jwt', None)

    party_map = dabl_fetch_party_map(ledger_id, admin_jwt)
    user_party = dabl_fetch_party_map(ledger_id, user_jwt)

    ws_settings.range('A20').expand().value = ""
    ws_settings.range('A23').expand().value = ""
    ws_settings.range('A20').value = user_party[0]
    ws_settings.range('A23').value = party_map
    ws_settings.range('B17').value = 'Done'
    ws_settings.range('B18').value = f'Last Update: {datetime.datetime.now()}'


def party_to_name(wb, party):
    party_map = get_party_map(wb)
    return party_map.get(party, '')


def name_to_party(wb, name):
    party_map = get_party_map(wb)
    name_map = {v : k  for k, v in party_map.items()}
    return name_map.get(name, '')


def get_party_map(wb):
    parties = wb.sheets['Settings'].range('A23').options(ndim=2).expand().value
    party_map = { p[0] : p[1] for p in parties }
    return party_map


def get_user_party(wb):
    return wb.sheets['Settings'].range('A20').value


def get_user_name(wb):
    return wb.sheets['Settings'].range('B20').value


def dabl_fetch_party_map(ledger_id, admin_jwt):
    user_party_contracts = dabl_send_search('DABL.User', 'UserParty', ledger_id, admin_jwt)
    party_map = [[c['contractData']['party'], c['contractData']['partyName']] for c in user_party_contracts]
    return party_map


def dabl_send_search(module_name, template_name, ledger_id, jwt):
    headers = {"Authorization": f"Bearer {jwt}", "Content-Type":"application/json"}
    search = {
        "%templates": [{"moduleName": module_name, "entityName": template_name}]
    }
    resp = requests.post(url=f'{DABL_URL}/data/{ledger_id}/contracts/search', headers=headers, verify=False, json=search)
    return resp.json()['result']


def dabl_send_command(command, ledger_id, jwt):
    headers = {"Authorization": f"Bearer {jwt}", "Content-Type":"application/json"}

    resp = requests.post(url=f'{DABL_URL}/data/{ledger_id}/command', headers=headers, verify=False, json=command)
    resp.status_code
    return resp


def fetch_utxos(address, token, network, spent=False, confirmations=3):
    chain = ''
    if network.lower() == 'mainnet':
        chain = 'main'
    elif network.lower() == 'testnet':
        chain = 'test3'

    blockcypher_url = f'https://api.blockcypher.com/v1/btc/{chain}/addrs/{address}'
    unspent = 0 if spent else 1
    blockcypher_params = f"?unspentOnly={unspent}&includeScript=1&confirmations={confirmations}&token={token}"
    response = requests.get(url=f'{blockcypher_url}{blockcypher_params}')
    utxos = []
    if response.status_code == 200:
        result = response.json()
        if 'txrefs' in result:
            for tx in result['txrefs']:
                utxo = {
                    'address': address,
                    'txHash': tx['tx_hash'],
                    'blockHeight': int(tx['block_height']),
                    'outputIdx': int(tx['tx_output_n']),
                    'value': int(tx['value']),
                    'sigScript': tx['script']
                }
                utxos.append(utxo)
    return utxos


def on_market_refresh():
    wb = xw.Book.caller()
    ws_market = wb.sheets['Market']
    ws_market.range('C1').value = 'Updating...'

    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)

    trader = dabl_fetch_trader(ledger_id, user_jwt, get_user_party(wb))
    if trader:
        ws_market.range('B4').value = get_user_name(wb)
        ws_market.range('B5').value = float(trader['contractData']['buyLimit'])
        ws_market.range('B7').value = int(trader['contractData']['sellLimit'])
    else:
        ws_market.range('B4').value = ''
        ws_market.range('B5').value = ''
        ws_market.range('B7').value = ''

    update_bids(wb)
    update_offers(wb)
    ws_market.range('C1').value = 'Done'
    ws_market.range('C2').value = f'Last Update: {datetime.datetime.now()}'


def update_bids(wb):
    ws_market = wb.sheets['Market']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)

    dabl_bids = dabl_send_search('Trading', 'BitcoinBid', ledger_id, user_jwt)
    bids = [
        {
            'BidID': b['contractData']['bidId'],
            'SubmittedBy': party_to_name(wb, b['contractData']['trader']),
            'Price': b['contractData']['price'],
            'Size': b['contractData']['size']
        }
        for b in dabl_bids]
    df_bids = pd.DataFrame(bids)
    ws_market.range('C9').expand().value = ''
    ws_market.range('C9').expand().value = df_bids.values


def update_offers(wb):
    ws_market = wb.sheets['Market']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)

    dabl_offers = dabl_send_search('Trading', 'BitcoinOffer', ledger_id, user_jwt)
    offers = [
        {
            'OfferID': b['contractData']['offerId'],
            'SubmittedBy': party_to_name(wb, b['contractData']['trader']),
            'Price': b['contractData']['price'],
            'Size': b['contractData']['size']
        }
        for b in dabl_offers]
    df_offers = pd.DataFrame(offers)
    ws_market.range('I9').expand().value = ''
    ws_market.range('I9').expand().value = df_offers.values


def dabl_fetch_trader(ledger_id, jwt, party):
    traders = dabl_send_search('Trading', 'Trader', ledger_id, jwt)
    for trader in traders:
        if trader['contractData']['trader'] == party:
            return trader
    return None


def on_submit_bid():
    wb = xw.Book.caller()
    ws_market = wb.sheets['Market']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)

    price = ws_market.range('H2').value
    size = ws_market.range('H3').value
    trader = dabl_fetch_trader(ledger_id, user_jwt, get_user_party(wb))

    if trader is None:
        ws_market.range('K2').value = f"Could not find trader role contract for {get_user_name(wb)}"
        return

    bid_id = str(get_next_order_id(wb))

    command = {
        'contractId': trader['contractId'],
        'templateId': trader['templateId'].split('@', 1)[0],
        'choice': "CreateBid",
        'choiceArgument': {
            'bidId': bid_id,
            'price': float(price),
            'size': int(size),
            'observers': list(get_party_map(wb).keys())
        }
    }

    create_bid_command = {
        'workflowId': f"create-bid-{bid_id}",
        'commandId': str(uuid.uuid4()),
        'commands': [command]
    }

    resp = dabl_send_command(create_bid_command, ledger_id, user_jwt)

    if resp.status_code == 200:
        update_bids(wb)
        ws_market.range('H2').value = ''
        ws_market.range('H3').value = ''
    else:
        ws_market.range('K2').value = f"Failed to Submit Bid"


def get_next_order_id(wb):
    ws_market = wb.sheets['Market']
    order_id = ws_market.range('A100').value
    next_order_id = order_id + 1
    ws_market.range('A100').value = next_order_id
    return int(next_order_id)


def on_submit_offer():
    wb = xw.Book.caller()
    ws_market = wb.sheets['Market']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)

    price = ws_market.range('H2').value
    size = ws_market.range('H3').value
    trader = dabl_fetch_trader(ledger_id, user_jwt, get_user_party(wb))

    if trader is None:
        ws_market.range('K2').value = f"Could not find trader role contract for {get_user_name(wb)}"
        return

    offer_id = str(get_next_order_id(wb))

    command = {
        'contractId': trader['contractId'],
        'templateId': trader['templateId'].split('@', 1)[0],
        'choice': "CreateOffer",
        'choiceArgument': {
            'offerId': offer_id,
            'price': float(price),
            'size': int(size),
            'observers': list(get_party_map(wb).keys())
        }
    }

    create_offer_command = {
        'workflowId': f"create-offer-{offer_id}",
        'commandId': str(uuid.uuid4()),
        'commands': [command]
    }

    resp = dabl_send_command(create_offer_command, ledger_id, user_jwt)

    if resp.status_code == 200:
        update_offers(wb)
        ws_market.range('H2').value = ''
        ws_market.range('H3').value = ''
    else:
        ws_market.range('K2').value = f"Failed to Submit Offer"


def on_hit_bid():
    wb = xw.Book.caller()
    ws_market = wb.sheets['Market']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)
    bid_id = int(wb.sheets['Market'].range('F5').value)

    bid = dabl_fetch_bid_offer(ledger_id, user_jwt, bid_id, True)

    if bid is None:
        ws_market.range('K2').value = f"Could not find bid contract with id {bid_id}"
        return

    trader = dabl_fetch_trader(ledger_id, user_jwt, get_user_party(wb))

    if trader is None:
        ws_market.range('K2').value = f"Could not find trader role contract for {get_user_name(wb)}"
        return

    command = {
        'contractId': trader['contractId'],
        'templateId': trader['templateId'].split('@', 1)[0],
        'choice': "HitBid",
        'choiceArgument': {
            'bidCid' : bid['contractId']
        }
    }

    hit_bid_command = {
        'workflowId': f"hit-bid-{bid_id}",
        'commandId': str(uuid.uuid4()),
        'commands': [command]
    }

    resp = dabl_send_command(hit_bid_command, ledger_id, user_jwt)

    if resp.status_code == 200:
        ws_market.range('F5').value = ''
        on_update_deals()
        update_bids(wb)


def on_cancel_bid():
    wb = xw.Book.caller()
    ws_market = wb.sheets['Market']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)
    bid_id = int(ws_market.range('F5').value)

    bid = dabl_fetch_bid_offer(ledger_id, user_jwt, bid_id, True)

    if bid is None:
        ws_market.range('K2').value = f"Could not find bid contract with id {bid_id}"
        return

    command = {
        'contractId': bid['contractId'],
        'templateId': bid['templateId'].split('@', 1)[0],
        'choice': "CancelBid",
        'choiceArgument': {
            'party' : get_user_party(wb)
        }
    }

    cancel_bid_command = {
        'workflowId': f"cancel-bid-{bid_id}",
        'commandId': str(uuid.uuid4()),
        'commands': [command]
    }

    resp = dabl_send_command(cancel_bid_command, ledger_id, user_jwt)

    if resp.status_code == 200:
        ws_market.range('F5').value = ''
        update_bids(wb)


def on_lift_offer():
    wb = xw.Book.caller()
    ws_market = wb.sheets['Market']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)
    offer_id = int(ws_market.range('L5').value)

    offer = dabl_fetch_bid_offer(ledger_id, user_jwt, offer_id, False)

    if offer is None:
        ws_market.range('K2').value = f"Could not find bid contract with id {offer_id}"
        return

    trader = dabl_fetch_trader(ledger_id, user_jwt, get_user_party(wb))

    if trader is None:
        ws_market.range('K2').value = f"Could not find trader role contract for {get_user_name(wb)}"
        return

    command = {
        'contractId': trader['contractId'],
        'templateId': trader['templateId'].split('@', 1)[0],
        'choice': "LiftOffer",
        'choiceArgument': {
            'offerCid' : offer['contractId']
        }
    }

    lift_offer_command = {
        'workflowId': f"lift-offer-{offer_id}",
        'commandId': str(uuid.uuid4()),
        'commands': [command]
    }

    resp = dabl_send_command(lift_offer_command, ledger_id, user_jwt)

    if resp.status_code == 200:
        ws_market.range('L5').value = ''
        on_update_deals()
        update_offers(wb)


def on_cancel_offer():
    wb = xw.Book.caller()
    ws_market = wb.sheets['Market']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)
    offer_id = int(ws_market.range('L5').value)

    offer = dabl_fetch_bid_offer(ledger_id, user_jwt, offer_id, False)

    if offer is None:
        ws_market.range('K2').value = f"Could not find offer contract with id {offer_id}"
        return

    command = {
        'contractId': offer['contractId'],
        'templateId': offer['templateId'].split('@', 1)[0],
        'choice': "CancelOffer",
        'choiceArgument': {
            'party' : get_user_party(wb)
        }
    }

    cancel_offer_command = {
        'workflowId': f"cancel-offer-{offer_id}",
        'commandId': str(uuid.uuid4()),
        'commands': [command]
    }

    resp = dabl_send_command(cancel_offer_command, ledger_id, user_jwt)

    if resp.status_code == 200:
        ws_market.range('L5').value = ''
        update_offers(wb)


def dabl_fetch_bid_offer(ledger_id, jwt, order_id, is_bid=True):
    template_name, field_name = ('BitcoinBid', 'bidId') if is_bid else ('BitcoinOffer', 'offerId')
    bid_offers = dabl_send_search('Trading', template_name, ledger_id, jwt)
    for bid_offer in bid_offers:
        if bid_offer['contractData'][field_name] == str(order_id):
            return bid_offer
    return None


def on_approve_request():
    wb = xw.Book.caller()
    ws_reqs = wb.sheets['Requests']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)
    request_id = int(ws_reqs.range('F5').value)
    ws_reqs.range('F4').value = 'Approving...'

    bid_request = dabl_fetch_bid_offer_request(ledger_id, user_jwt, request_id, True)
    offer_request = None
    trade_request = None
    resp = None

    if bid_request:
        command = {
            'contractId': bid_request['contractId'],
            'templateId': bid_request['templateId'].split('@', 1)[0],
            'choice': "ApproveBid",
            'choiceArgument': {}
        }

        approve_bid_command = {
            'workflowId': f"approve-bid-{request_id}",
            'commandId': str(uuid.uuid4()),
            'commands': [command]
        }
        resp = dabl_send_command(approve_bid_command, ledger_id, user_jwt)

    if not bid_request:
        offer_request = dabl_fetch_bid_offer_request(ledger_id, user_jwt, request_id, False)

    if offer_request:
        command = {
            'contractId': offer_request['contractId'],
            'templateId': offer_request['templateId'].split('@', 1)[0],
            'choice': "ApproveOffer",
            'choiceArgument': {}
        }

        approve_offer_command = {
            'workflowId': f"approve-offer-{request_id}",
            'commandId': str(uuid.uuid4()),
            'commands': [command]
        }
        resp = dabl_send_command(approve_offer_command, ledger_id, user_jwt)

    if not offer_request:
        trade_request = dabl_fetch_trade_request(ledger_id, user_jwt, request_id)

    if trade_request:
        command = {
            'contractId': trade_request['contractId'],
            'templateId': trade_request['templateId'].split('@', 1)[0],
            'choice': "ApproveTradeRequest",
            'choiceArgument': {}
        }

        approve_trade_command = {
            'workflowId': f"approve-trade-{request_id}",
            'commandId': str(uuid.uuid4()),
            'commands': [command]
        }
        resp = dabl_send_command(approve_trade_command, ledger_id, user_jwt)

    if resp and resp.status_code == 200:
        ws_reqs.range('F4').value = 'Done'
        ws_reqs.range('F5').value = ''
        on_update_requests()
    else:
        ws_reqs.range('F4').value = 'Error'


def on_reject_request():
    wb = xw.Book.caller()
    ws_reqs = wb.sheets['Requests']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)
    request_id = int(ws_reqs.range('F5').value)
    ws_reqs.range('F4').value = 'Rejecting...'

    bid_request = dabl_fetch_bid_offer_request(ledger_id, user_jwt, request_id, True)
    offer_request = None
    trade_request = None
    resp = None

    if bid_request:
        command = {
            'contractId': bid_request['contractId'],
            'templateId': bid_request['templateId'].split('@', 1)[0],
            'choice': "RejectBid",
            'choiceArgument': {}
        }

        reject_bid_command = {
            'workflowId': f"reject-bid-{request_id}",
            'commandId': str(uuid.uuid4()),
            'commands': [command]
        }
        resp = dabl_send_command(reject_bid_command, ledger_id, user_jwt)

    if not bid_request:
        offer_request = dabl_fetch_bid_offer_request(ledger_id, user_jwt, request_id, False)

    if offer_request:
        command = {
            'contractId': offer_request['contractId'],
            'templateId': offer_request['templateId'].split('@', 1)[0],
            'choice': "RejectOffer",
            'choiceArgument': {}
        }

        reject_offer_command = {
            'workflowId': f"reject-offer-{request_id}",
            'commandId': str(uuid.uuid4()),
            'commands': [command]
        }
        resp = dabl_send_command(reject_offer_command, ledger_id, user_jwt)

    if not offer_request:
        trade_request = dabl_fetch_trade_request(ledger_id, user_jwt, request_id)

    if trade_request:
        command = {
            'contractId': trade_request['contractId'],
            'templateId': trade_request['templateId'].split('@', 1)[0],
            'choice': "RejectTradeRequest",
            'choiceArgument': {}
        }

        reject_trade_command = {
            'workflowId': f"reject-trade-{request_id}",
            'commandId': str(uuid.uuid4()),
            'commands': [command]
        }
        resp = dabl_send_command(reject_trade_command, ledger_id, user_jwt)

    if resp and resp.status_code == 200:
        ws_reqs.range('F4').value = 'Done'
        ws_reqs.range('F5').value = ''
        on_update_requests()
    else:
        ws_reqs.range('F4').value = 'Error'


def on_update_deals():
    wb = xw.Book.caller()
    ws_deals = wb.sheets['Deals']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)
    ws_deals.range('C1').value = 'Updating...'

    trade_contracts = dabl_send_search('Trading', 'BitcoinTrade', ledger_id, user_jwt)

    user_party = get_user_party(wb)

    deals = [
        {
            'DealID': d['contractData']['tradeId'],
            'Price': d['contractData']['price'],
            'Size': d['contractData']['size'],
            'Side': 'Bought' if user_party in [d['contractData']['buyer'], d['contractData']['buyerBackOffice'], d['contractData']['observers'][0]]  else 'Sold',
            'Buyer': party_to_name(wb, d['contractData']['buyer']),
            'Seller': party_to_name(wb, d['contractData']['seller']),
            'CashTx': d['contractData']['cashTransferId'],
            'BitcoinToAddress': d['contractData']['bitcoinAddress'],
            'BitcoinTx': d['contractData']['bitcoinTxHash'],
        }
        for d in trade_contracts]
    df_deals = pd.DataFrame(deals)

    ws_deals.range('C9').expand().value = ''
    ws_deals.range('C9').value = df_deals.values
    ws_deals.range('C1').value = 'Done'
    ws_deals.range('C2').value = f'Last Update: {datetime.datetime.now()}'


def on_settle_cash():
    wb = xw.Book.caller()
    ws_deals = wb.sheets['Deals']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)
    deal_id = int(ws_deals.range('J4').value)
    cash_tx_id = ws_deals.range('J5').value
    bitcoin_to_address = ws_deals.range('J6').value
    ws_deals.range('H3').value = ''

    deal = dabl_fetch_trade(ledger_id, user_jwt, deal_id)

    if deal is None:
        ws_deals.range('H3').value = f'Could not find deal with ID {deal_id}'
        return

    command = {
        'contractId': deal['contractId'],
        'templateId': deal['templateId'].split('@', 1)[0],
        'choice': "SettleCash",
        'choiceArgument': {
            'cashId': cash_tx_id,
            'btcAddress': bitcoin_to_address
        }
    }

    settle_cash_command = {
        'workflowId': f"settle-cash-{deal_id}",
        'commandId': str(uuid.uuid4()),
        'commands': [command]
    }

    resp = dabl_send_command(settle_cash_command, ledger_id, user_jwt)

    if resp.status_code == 200:
        on_update_deals()
        ws_deals.range('J4').value = ''
        ws_deals.range('J5').value = ''
        ws_deals.range('J6').value = ''
    else:
        ws_deals.range('H3').value = 'Error'


def on_send_bitcoin():
    wb = xw.Book.caller()
    ws_deals = wb.sheets['Deals']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)
    deal_id = int(ws_deals.range('F5').value)
    ws_deals.range('D3').value = ''
    key_file = settings.get('key_file', None)
    fee = 50000  # calculate based on bytes

    deal = dabl_fetch_trade(ledger_id, user_jwt, deal_id)

    if deal is None:
        ws_deals.range('D3').value = f'Could not find deal with ID {deal_id}'
        return

    utxos = wb.sheets['UTXOs'].range('C9').expand().options(pd.DataFrame, index=False).value
    utxos.columns = ['address', 'tx_hash', 'block_height', 'tx_output_n', 'value', 'script']

    ins, outs, fee, tx, tx_hash = build_bitcoin_tx(utxos, deal['contractData']['bitcoinAddress'], int(deal['contractData']['size']), fee, key_file)

    create_bitcoin_tx_command = {
        'createArguments': {
            'operator': get_user_party(wb),
            'user': get_user_party(wb),
            'txInputs': ins,
            'txOutputs': outs,
            'fee': int(fee),
            'rawTx': tx,
            'txHash': tx_hash,
            'observers': [deal['contractData']['buyerBackOffice']]
        },
        'templateId': 'Bitcoin.Transaction.SignedTransaction'
    }

    exercise_settle_bitcoin_command = {
        'contractId': deal['contractId'],
        'templateId': deal['templateId'].split('@', 1)[0],
        'choice': "SettleBitcoin",
        'choiceArgument': {
            'txHash': tx_hash
        }
    }

    send_bitcoin_command = {
        'workflowId': "send-bitcoin",
        'commandId': str(uuid.uuid4()),
        'commands': [create_bitcoin_tx_command, exercise_settle_bitcoin_command]
    }

    resp = dabl_send_command(send_bitcoin_command, ledger_id, user_jwt)

    if resp.status_code == 200:
        on_update_deals()
        ws_deals.range('F5').value = ''
        on_update_transactions()
    else:
        ws_deals.range('D3').value = 'Error'


def on_update_transactions():
    wb = xw.Book.caller()
    ws_trans = wb.sheets['Transactions']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)
    ws_trans.range('C1').value = 'Updating...'

    signed_transaction_contracts = dabl_send_search('Bitcoin.Transaction', 'SignedTransaction', ledger_id, user_jwt)

    signed_txs = [
        {
            'TxHash': tx['contractData']['txHash'],
            'NumInputs': len(tx['contractData']['txInputs']),
            'ValueIn': sum([int(utxo['value']) for utxo in tx['contractData']['txInputs']]),
            'InputAddresses': ', '.join(set([utxo['address'] for utxo in tx['contractData']['txInputs']])),
            'NumOutputs': len(tx['contractData']['txOutputs']),
            'ValueOut': sum([int(out['value']) for out in tx['contractData']['txOutputs']]),
            'OutputAddresses': ', '.join(set([out['address'] for out in tx['contractData']['txOutputs']])),
            'Fee': tx['contractData']['fee'],
            'RawTx': tx['contractData']['rawTx']
        }
        for tx in signed_transaction_contracts]
    df_txs = pd.DataFrame(signed_txs)

    ws_trans.range('C9').expand().value = ''
    ws_trans.range('C9').value = df_txs.values
    ws_trans.range('C1').value = 'Done'
    ws_trans.range('C2').value = f'Last Update: {datetime.datetime.now()}'


def on_transmit_bitcoin_tx():
    wb = xw.Book.caller()
    ws_trans = wb.sheets['Transactions']
    ws_trans.range('F4').value = 'Transmitting...'
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)
    tx_hash = ws_trans.range('C5').value
    signed_tx_contract = dabl_fetch_signed_tx(ledger_id, user_jwt, tx_hash)
    if not signed_tx_contract:
        ws_trans.range('F4').value = f'Could not find transaction {tx_hash}'
        return

    blockcypher_token = settings.get('token', None)
    network = settings.get('network', None)
    if not blockcypher_token or not network:
        ws_trans.range('F4').value = f'Missing Token or Network settings to transmit transaction {tx_hash}'
        return

    tx = push_raw_tx(signed_tx_contract['contractData']['rawTx'], blockcypher_token, network)
    if tx:
        ws_trans.range('C5').value = ''
        ws_trans.range('F4').value = 'Done'
        ws_trans.range('F5').value = f'Last Transmission: {datetime.datetime.now()}'
    else:
        ws_trans.range('F4').value = 'Error'


def push_raw_tx(raw_tx, token, network):
    chain = ''
    if network.lower() == 'mainnet':
        chain = 'main'
    elif network.lower() == 'testnet':
        chain = 'test3'
    blockcypher_url = f'https://api.blockcypher.com/v1/btc/{chain}/txs/push'
    blockcypher_params = f"?token={token}"
    headers = {"Content-Type": "application/json; charset=UTF-8", "Accept":"application/json"}
    tx = {
        'tx': raw_tx
    }
    response = requests.post(url=f'{blockcypher_url}{blockcypher_params}', headers=headers, json=tx)
    if response.status_code == 201:
        return response.json()

    return None


def dabl_fetch_signed_tx(ledger_id, jwt, tx_hash):
    txs = dabl_send_search('Bitcoin.Transaction', 'SignedTransaction', ledger_id, jwt)
    for tx in txs:
        if tx['contractData']['txHash'] == tx_hash:
            return tx
    return None


def build_bitcoin_tx(utxos, receiver_addr, amount, fee, key_file, change_addr=None):
    sorted_utxos = utxos.sort_values(by=['block_height', 'value'], ascending=[True, False])
    total_balance = 0
    utxos_to_spend = []
    for i, utxo in sorted_utxos.iterrows():
        if total_balance >= amount + fee:
            break

        balance = utxo['value']
        utxos_to_spend.append({
            'address': utxo['address'],
            'txHash': utxo['tx_hash'],
            'blockHeight': int(utxo['block_height']),
            'outputIdx': int(utxo['tx_output_n']),
            'value': int(utxo['value']),
            'sigScript': utxo['script']
        })

        total_balance += balance

    if total_balance < amount + fee:
        raise(f"Not enough balance to send! total balance: {total_balance}, required: {amount + fee}, amount to send: {amount}, fee: {fee}")

    if not change_addr:
        change_addr = utxos_to_spend[0]['address']

    txins = []
    for utxo in utxos_to_spend:
        txin = CMutableTxIn(COutPoint(lx(utxo['txHash']), utxo['outputIdx']))
        txins.append(txin)

    txouts = []
    txout = CMutableTxOut(amount, CBitcoinAddress(receiver_addr).to_scriptPubKey())
    txouts.append(txout)
    outs = [{'address': receiver_addr, 'value': amount}]

    if total_balance > amount + fee:
        change = total_balance - amount - fee
        txout = CMutableTxOut(change, CBitcoinAddress(change_addr).to_scriptPubKey())
        txouts.append(txout)
        outs.append({'address': change_addr, 'value': change})

    tx = CMutableTransaction(txins, txouts)

    sig_data = []

    for i, utxo in enumerate(utxos_to_spend):
        sighash = SignatureHash(CScript(x(utxo['sigScript'])), tx, i, SIGHASH_ALL)
        seckey = fetch_key_for_address(key_file, utxo['address'])
        if not seckey:
            raise(f"Could not find private key for address: {utxo['address']}")
        sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])
        sig_data.append([sig, seckey.pub])

    for i, txin in enumerate(txins):
        txin.scriptSig = CScript(sig_data[i])

    tx_hash = b2lx(hashlib.sha256(hashlib.sha256(tx.serialize()).digest()).digest())

    return utxos_to_spend, outs, fee, b2x(tx.serialize()), tx_hash


def fetch_key_for_address(key_file, address):
    keys = read_keys(key_file)
    bitcoin_secrets = [CBitcoinSecret(key) for key in keys]
    for key in bitcoin_secrets:
        addr = P2PKHBitcoinAddress.from_pubkey(key.pub)
        if str(addr) == address:
            return key

    return None


def dabl_fetch_trade(ledger_id, jwt, deal_id):
    trades = dabl_send_search('Trading', 'BitcoinTrade', ledger_id, jwt)
    for trade in trades:
        if trade['contractData']['tradeId'] == str(deal_id):
            return trade
    return None


def read_keys(key_file):
    keys = []
    with open(key_file, 'r') as fp:
        key = fp.readline()
        while key:
            keys.append(key.strip())
            key = fp.readline()
    return keys


def get_public_addresses(key_file):
    keys = read_keys(key_file)
    bitcoin_secrets = [CBitcoinSecret(key) for key in keys]
    bitcoin_addresses = [P2PKHBitcoinAddress.from_pubkey(key.pub) for key in bitcoin_secrets]
    return bitcoin_addresses


def on_update_requests():
    wb = xw.Book.caller()
    ws_reqs = wb.sheets['Requests']
    settings = get_settings(wb)
    ledger_id = settings.get('ledger_id', None)
    user_jwt = settings.get('user_jwt', None)
    ws_reqs.range('C1').value = 'Updating...'

    bid_requests = dabl_send_search('Trading', 'BitcoinBidRequest', ledger_id, user_jwt)

    bids = [
        {
            'RequestID': b['contractData']['bidId'],
            'SubmittedBy': party_to_name(wb, b['contractData']['trader']),
            'Type': 'New Bid',
            'Price': b['contractData']['price'],
            'Size': b['contractData']['size'],
            'Status': 'Pending Approval'
        }
        for b in bid_requests]

    offer_requests = dabl_send_search('Trading', 'BitcoinOfferRequest', ledger_id, user_jwt)

    offers = [
        {
            'RequestID': o['contractData']['offerId'],
            'SubmittedBy': party_to_name(wb, o['contractData']['trader']),
            'Type': 'New Offer',
            'Price': o['contractData']['price'],
            'Size': o['contractData']['size'],
            'Status': 'Pending Approval'
        }
        for o in offer_requests]

    trade_requests = dabl_send_search('Trading', 'BitcoinTradeRequest', ledger_id, user_jwt)

    trades = [
        {
            'RequestID': t['contractData']['tradeId'],
            'SubmittedBy': party_to_name(wb, t['contractData']['trader']),
            'Type': 'Hit Bid' if t['contractData']['trader'] == t['contractData']['seller'] else 'Lift Offer',
            'Price': t['contractData']['price'],
            'Size': t['contractData']['size'],
            'Status': 'Pending Approval'
        }
        for t in trade_requests]

    approved_requests = dabl_send_search('Trading', 'ApprovedBitcoinTradeRequest', ledger_id, user_jwt)

    approved = [
        {
            'RequestID': a['contractData']['tradeId'],
            'SubmittedBy': party_to_name(wb, a['contractData']['trader']),
            'Type': 'Hit Bid' if a['contractData']['trader'] == a['contractData']['seller'] else 'Lift Offer',
            'Price': a['contractData']['price'],
            'Size': a['contractData']['size'],
            'Status': 'Approved'
        }
        for a in approved_requests]

    df_requests = pd.DataFrame(bids + offers + trades + approved)

    ws_reqs.range('C9').expand().value = ''
    ws_reqs.range('C9').value = df_requests.values
    ws_reqs.range('C1').value = 'Done'
    ws_reqs.range('C2').value = f'Last Update: {datetime.datetime.now()}'


def dabl_fetch_bid_offer_request(ledger_id, jwt, request_id, is_bid=False):
    template_name, field_name = ('BitcoinBidRequest', 'bidId') if is_bid else ('BitcoinOfferRequest', 'offerId')
    bid_offers = dabl_send_search('Trading', template_name, ledger_id, jwt)
    for bid_offer in bid_offers:
        if bid_offer['contractData'][field_name] == str(request_id):
            return bid_offer
    return None


def dabl_fetch_trade_requests(ledger_id, jwt, approved=False):
    template_name = 'ApprovedBitcoinTradeRequest' if approved else 'BitcoinTradeRequest'
    headers = {"Authorization": f"Bearer {jwt}", "Content-Type":"application/json"}
    search = {
        "%templates": [{"moduleName": "Trading", "entityName": template_name}]
    }
    trade_request_contracts = requests.post(url=f'{DABL_URL}/data/{ledger_id}/contracts/search', headers=headers, verify=False, json=search)
    trade_requests = trade_request_contracts.json()['result']
    return trade_requests


def dabl_fetch_trade_request(ledger_id, jwt, request_id):
    trade_requests = dabl_send_search('Trading', 'BitcoinTradeRequest', ledger_id, jwt)
    for trade_request in trade_requests:
        if trade_request['contractData']['tradeId'] == str(request_id):
            return trade_request
    return None
