import currency

settings = Hash(default_value=0)

random.seed()

@construct
def seed(operator: str, dev_contract: str):
    settings['pot_max'] = 20000
    settings['refund_per'] = 0.01
    settings['refund_div'] = 100
    settings['dev_contract'] = dev_contract
    settings['operator'] = operator
    settings['list'] = ["pot_max", "refund_per", "refund_div", "dev_contract", "operator"]

@export
def smack(bet_amount: int):
    # lock max bet to 8% of current pot
    bet = determine_cost(bet_amount)

    #assert False, type(bet)

    # Take bet
    currency.transfer_from(amount=bet, to=ctx.this, main_account=ctx.caller)

    # Get random number
    x = random.randint(0, 10)

    # WIN
    if x >= 6:
        win_amount = bet * 2
        currency.transfer(amount=win_amount, to=ctx.caller)
        return '{"bet":' + str(bet) + ', "won":' + str(win_amount) + ', "status": 1}'

    # LOSE
    else:
        give_dev_token()
        check_overflow()
        return '{"bet":' + str(bet) + ', "status": 0}'

def determine_cost(bet_amount: int):
    max_bet = int(currency.balance_of(ctx.this) * 0.08 // 1)
    if bet_amount < max_bet:
        return bet_amount
    else:
        return max_bet

def give_dev_token():
    dev_contract = importlib.import_module(settings['dev_contract'])
    refund = dev_contract.balance_of(ctx.this) * (settings['refund_per'] / settings['refund_div'])
    dev_contract.transfer(refund, ctx.caller)

def check_overflow():
    overflow = currency.balance_of(ctx.this) - settings['pot_max']

    if overflow > 0:
        currency.transfer(amount=overflow, to=settings['dev_contract'])

@export
def change_settings(setting: str, new_value: Any):
    assert_operator()
    assert setting in settings['list'], setting + ' is not a configurable setting.'
    settings[setting] = new_value

@export
def transfer(amount: float, to: str):
    assert_operator()
    currency.transfer(amount=amount, to=to)

@export
def transfer_dev_token(amount: float, to: str):
    assert_operator()
    dev_contract = importlib.import_module(settings['dev_contract'])
    dev_contract.transfer(amount=amount, to=to)

def assert_operator():
    assert ctx.caller == settings['operator'], "Only operator can call this method."

# REMOVE FOR PRODUCTION
@export
def test_smack_win(bet_amount: int):
    # lock max bet to 8% of current pot
    bet = determine_cost(bet_amount)

    # Take bet
    currency.transfer_from(amount=bet, to=ctx.this, main_account=ctx.caller)

    # Get random number
    x = 6

    # WIN
    if x >= 6:
        win_amount = bet * 2
        currency.transfer(amount=win_amount, to=ctx.caller)
        return '{"bet":' + str(bet) + ', "won":' + str(win_amount) + ', "status": 1}'

    # LOSE
    else:
        give_dev_token()
        check_overflow()
        return '{"bet":' + str(bet) + ', "status": 0}'

@export
def test_smack_lose(bet_amount: int):
    # lock max bet to 8% of current pot
    bet = determine_cost(bet_amount)

    # Take bet
    currency.transfer_from(amount=bet, to=ctx.this, main_account=ctx.caller)

    # Get random number
    x = 5

    # WIN
    if x >= 6:
        win_amount = bet * 2
        currency.transfer(amount=win_amount, to=ctx.caller)
        return '{"bet":' + str(bet) + ', "won":' + str(win_amount) + ', "status": 1}'

    # LOSE
    else:
        give_dev_token()
        check_overflow()
        return '{"bet":' + str(bet) + ', "status": 0}'
