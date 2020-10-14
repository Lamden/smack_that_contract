import currency
#import submission  #Don't need for testing smack_that

supply = Variable()
balances = Hash(default_value=0)
owner = Variable()

@construct
def seed(amount=1000000):
    balances['jeff'] = amount - 1000
    balances['con_smack_that'] = 1000
    supply.set(amount)
    owner.set('jeff')

@export
def transfer(amount: float, to: str):
    sender = ctx.caller
    assert balances[sender] >= amount, 'Not enough coins to send!'
    balances[sender] -= amount
    balances[to] += amount


@export
def balance_of(account: str):
    return balances[account]


@export
def total_supply():
    return supply.get()


@export
def allowance(main: str, spender: str):
    return balances[main, spender]


@export
def approve(amount: float, to: str):
    sender = ctx.caller
    balances[sender, to] += amount
    return balances[sender, to]


@export
def transfer_from(amount: float, to: str, main_account: str):
    sender = ctx.caller
    assert balances[main_account, sender
        ] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {}'.format(
        balances[main_account, sender], amount)
    assert balances[main_account] >= amount, 'Not enough coins to send!'
    balances[main_account, sender] -= amount
    balances[main_account] -= amount
    balances[to] += amount


@export
def redeem(amount: float):
    assert balances[ctx.caller] >= amount, 'Not enough tokens to redeem!'
    assert amount > 0, 'Invalid amount!'
    balances[ctx.caller] -= amount
    share = amount / supply.get()
    reward = share * currency.balance_of(ctx.this)
    if reward > 0:
        currency.transfer(reward, ctx.caller)
    supply.set(supply.get() - amount)


@export
def change_ownership(new_owner: str):
    assert ctx.caller == owner.get(), 'Only the owner can change ownership!'
    owner.set(new_owner)

'''
@export
def change_developer(contract: str, new_developer: str):
    assert ctx.caller == owner.get(
        ), 'Only the owner can change the developer!'
    submission.change_developer(contract=contract, new_developer=new_developer)
'''