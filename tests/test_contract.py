#tests/test_contract.py
import unittest
import json
from contracting.client import ContractingClient
client = ContractingClient()

seed_values = {
    'pot_max': 20000,
    'refund_per': 0.01,
    'refund_div': 100,
    'list': ["pot_max", "refund_per", "refund_div", "dev_contract", "operator"]
}

initial_state = {
    "operator": "jeff",
    "dev_contract": "con_smackeroos"
}

with open('./currency.py') as f:
    code = f.read()
    client.submit(code, name='currency')
with open('./con_smackeroos.py') as f:
    code = f.read()
    client.submit(code, name='con_smackeroos')
with open('../contracts/con_smack_that.py') as f:
    code = f.read()
    client.submit(
        code,
        name='con_smack_that',
        constructor_args=initial_state
    )

class MyTestCase(unittest.TestCase):
    con_smack_that = None
    con_smackeroos = None
    currency_contract = None

    def change_signer(self, name):
        client.signer = name
        self.con_smack_that = client.get_contract('con_smack_that')
        self.con_smackeroos = client.get_contract('con_smackeroos')
        self.currency_contract = client.get_contract('currency')

    def test_1_seed_constants(self):
        self.change_signer('stu')
        print("TEST SEED CONSTANTS")

        self.assertEqual(self.con_smack_that.quick_read('settings', 'pot_max'), seed_values['pot_max'])
        self.assertEqual(self.con_smack_that.quick_read('settings', 'refund_per'), seed_values['refund_per'])
        self.assertEqual(self.con_smack_that.quick_read('settings', 'refund_div'), seed_values['refund_div'])
        self.assertEqual(self.con_smack_that.quick_read('settings', 'dev_contract'), initial_state['dev_contract'])
        self.assertEqual(self.con_smack_that.quick_read('settings', 'operator'), initial_state['operator'])
        self.assertEqual(self.con_smack_that.quick_read('settings', 'list'), seed_values['list'])

        self.assertEqual(self.con_smackeroos.quick_read('balances', 'con_smack_that'), 1000)

    def test_2_smack(self):
        self.change_signer('stu')

        prev_balance = self.currency_contract.quick_read('balances', 'stu')

        bet_amount = 1
        res = json.loads(self.con_smack_that.smack(bet_amount=bet_amount))

        self.assertEqual(res['bet'], bet_amount)

        new_balance = self.currency_contract.quick_read('balances', 'stu')

        if res['status'] == 1:
            self.assertEqual(res['won'], bet_amount*2)
            self.assertEqual(new_balance, prev_balance + bet_amount)
            self.assertEqual(self.con_smackeroos.quick_read('balances', 'stu'), None)
        else:
            self.assertEqual(new_balance, prev_balance - bet_amount)
            self.assertGreater(self.con_smackeroos.quick_read('balances', 'stu'), None)

    def test_3a_win(self):
        self.change_signer('stu')

        prev_balance = self.currency_contract.quick_read('balances', 'stu')
        prev_smackaroos = self.con_smackeroos.quick_read('balances', 'stu')

        bet_amount = 100
        win_amount = bet_amount * 2
        res = json.loads(self.con_smack_that.test_smack_win(bet_amount=bet_amount))

        self.assertEqual(res['won'], win_amount)
        self.assertEqual(res['bet'], bet_amount)
        self.assertEqual(res['status'], 1)

        new_balance = self.currency_contract.quick_read('balances', 'stu')
        new_smackaroos = self.con_smackeroos.quick_read('balances', 'stu')
        self.assertEqual(new_balance, prev_balance + bet_amount)
        self.assertEqual(prev_smackaroos, new_smackaroos)

    def test_3b_win_bet_too_much(self):
        self.change_signer('stu')

        prev_balance = self.currency_contract.quick_read('balances', 'stu')
        prev_smackaroos = self.con_smackeroos.quick_read('balances', 'stu')

        contract_bal = self.currency_contract.quick_read('balances', 'con_smack_that') or 0

        bet_amount = 10000
        expected_bet = int(contract_bal * 0.08 // 1)
        win_amount = expected_bet * 2
        res = json.loads(self.con_smack_that.test_smack_win(bet_amount=bet_amount))

        self.assertEqual(res['bet'], expected_bet)
        self.assertEqual(res['won'], win_amount)
        self.assertEqual(res['status'], 1)

        new_balance = self.currency_contract.quick_read('balances', 'stu')
        new_smackaroos = self.con_smackeroos.quick_read('balances', 'stu')
        self.assertEqual(new_balance, prev_balance + expected_bet)
        self.assertEqual(prev_smackaroos, new_smackaroos)

    def test_4_lose(self):
        self.change_signer('stu')

        prev_balance = self.currency_contract.quick_read('balances', 'stu')
        prev_smackaroos = self.con_smackeroos.quick_read('balances', 'stu') or 0

        bet_amount = 100
        res = json.loads(self.con_smack_that.test_smack_lose(bet_amount=bet_amount))

        self.assertFalse("won" in res.keys())
        self.assertEqual(res['bet'], bet_amount)
        self.assertEqual(res['status'], 0)

        new_balance = self.currency_contract.quick_read('balances', 'stu')
        new_smackaroos = self.con_smackeroos.quick_read('balances', 'stu')
        self.assertEqual(new_balance, prev_balance - bet_amount)
        self.assertGreater(new_smackaroos, prev_smackaroos)

    def test_5a_change_refund_div(self):
        self.change_signer('jeff')

        prev_value = self.con_smack_that.quick_read('settings', 'refund_div')

        self.con_smack_that.change_settings(setting="refund_div", new_value=10)

        new_value = self.con_smack_that.quick_read('settings', 'refund_div')

        self.assertEqual(new_value, 10)
        self.assertNotEqual(prev_value, new_value)

    def test_5b_change_refund_per(self):
        self.change_signer('jeff')

        prev_value = self.con_smack_that.quick_read('settings', 'refund_per')

        self.con_smack_that.change_settings(setting="refund_per", new_value=1)

        new_value = self.con_smack_that.quick_read('settings', 'refund_per')

        self.assertEqual(new_value, 1)
        self.assertNotEqual(prev_value, new_value)

    def test_5c_change_operator(self):
        self.change_signer('jeff')

        prev_value = self.con_smack_that.quick_read('settings', 'operator')

        self.con_smack_that.change_settings(setting="operator", new_value='stu')

        new_value = self.con_smack_that.quick_read('settings', 'operator')

        self.assertEqual(new_value, 'stu')
        self.assertNotEqual(prev_value, new_value)

        self.change_signer('stu')
        self.con_smack_that.change_settings(setting="operator", new_value='jeff')

    def test_5d_change_operator_wrong_operator(self):
        self.change_signer('stu')
        prev_value = self.con_smack_that.quick_read('settings', 'operator')

        self.assertRaises(
            AssertionError,
            lambda: self.con_smack_that.change_settings(setting="operator", new_value='stu')
        )

        new_value = self.con_smack_that.quick_read('settings', 'operator')

        self.assertEqual(prev_value, new_value)

    def test_5e_change_dev_contract(self):
        self.change_signer('jeff')

        prev_value = self.con_smack_that.quick_read('settings', 'dev_contract')

        self.con_smack_that.change_settings(setting="dev_contract", new_value='con_something_else')

        new_value = self.con_smack_that.quick_read('settings', 'dev_contract')

        self.assertEqual(new_value, 'con_something_else')
        self.assertNotEqual(prev_value, new_value)

        self.con_smack_that.change_settings(setting="dev_contract", new_value=initial_state['dev_contract'])

    def test_5f_change_pot_max(self):
        self.change_signer('jeff')

        prev_value = self.con_smack_that.quick_read('settings', 'pot_max')

        self.con_smack_that.change_settings(setting="pot_max", new_value=1)

        new_value = self.con_smack_that.quick_read('settings', 'pot_max')

        self.assertEqual(new_value, 1)
        self.assertNotEqual(prev_value, new_value)

        self.con_smack_that.change_settings(setting="pot_max", new_value=seed_values['pot_max'])

    def test_5g_change_unlisted_setting(self):
        self.change_signer('jeff')

        prev_value = self.con_smack_that.quick_read('settings', 'list')

        self.assertRaises(
            AssertionError,
            lambda: self.con_smack_that.change_settings(setting="list", new_value=['nope'])
        )

        new_value = self.con_smack_that.quick_read('settings', 'list')

        self.assertEqual(prev_value, new_value)


    def test_6_transfer_tau(self):
        self.change_signer('jeff')
        prev_contract_bal = self.currency_contract.quick_read('balances', 'con_smack_that') or 0
        prev_stu_balance = self.currency_contract.quick_read('balances', 'jeff') or 0

        self.con_smack_that.transfer(amount=100, to="jeff")

        new_contract_bal = self.currency_contract.quick_read('balances', 'con_smack_that') or 0
        new_stu_balance = self.currency_contract.quick_read('balances', 'jeff') or 0

        self.assertEqual(new_contract_bal, prev_contract_bal - 100)
        self.assertEqual(new_stu_balance, prev_stu_balance  + 100)


    def test_7_transfer_dev_token(self):
        self.change_signer('jeff')
        prev_contract_bal = self.con_smackeroos.quick_read('balances', 'con_smack_that') or 0
        prev_stu_balance = self.con_smackeroos.quick_read('balances', 'jeff') or 0

        self.con_smack_that.transfer_dev_token(amount=prev_contract_bal, to="jeff")

        new_contract_bal = self.con_smackeroos.quick_read('balances', 'con_smack_that') or 0
        new_stu_balance = self.con_smackeroos.quick_read('balances', 'jeff') or 0

        self.assertEqual(new_contract_bal, 0)
        self.assertEqual(new_stu_balance, prev_stu_balance + prev_contract_bal)

    def test_8_overflow(self):
        # top up the currency balance of con_smack_that
        self.change_signer('alex')
        self.currency_contract.transfer(amount=20000, to='con_smack_that')

        smack_that_bal = self.currency_contract.quick_read('balances', 'con_smack_that') or 0
        dev_contract_bal = self.currency_contract.quick_read('balances', initial_state['dev_contract']) or 0

        self.change_signer('stu')
        bet_amount = 999999
        # Cause Loss
        res = json.loads(self.con_smack_that.test_smack_lose(bet_amount=bet_amount))

        new_smack_that_bal = self.currency_contract.quick_read('balances', 'con_smack_that') or 0
        new_dev_contract_bal = self.currency_contract.quick_read('balances', initial_state['dev_contract']) or 0

        print ('smack_that_bal:', smack_that_bal, 'new_smack_that_bal:', new_smack_that_bal)
        print('dev_contract_bal:', dev_contract_bal, 'new_dev_contract_bal', new_dev_contract_bal)

        self.assertEqual(new_smack_that_bal, seed_values['pot_max'])
        self.assertEqual(new_dev_contract_bal, dev_contract_bal + ((smack_that_bal + res['bet']) - seed_values['pot_max']))

if __name__ == '__main__':
    unittest.main()