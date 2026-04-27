import re
import unittest
import uuid


class UsernameException(Exception):
    pass


class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class UserAlreadyYourFriendException(Exception):
    pass


class Payment:

    def __init__(self, amount, actor, target, note):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note


class User:

    def __init__(self, username, balance=0.0, credit_card_number=None):
        self.credit_card_number = credit_card_number
        self.balance = balance
        self.feed = []
        self.friends = []

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException('Username not valid.')


    def retrieve_feed(self):
        return self.feed

    def add_friend(self, new_friend):
        if not new_friend in self.friends:
            self.friends.append(new_friend)
            self.feed.append(f"{self.username} added {new_friend.username} as friends")
        else:
            raise UserAlreadyYourFriendException("This user is already your friend")

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number

        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target, amount, note):
        amount = float(amount)
        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        if self.balance >= amount:
            self.balance -= amount
            target.balance += amount
        else:
            self.pay_with_card(target, amount, note)

        self.feed.append(f"{self.username} paid {target.username} ${amount} for {note}")


    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def pay_with_balance(self, target, amount, note):
        # TODO: add code here
        pass

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match('^[A-Za-z0-9_\\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass


class MiniVenmo:
    def create_user(self, username, balance, credit_card_number):
        return User(username, balance, credit_card_number)

    def render_feed(self, feed):
        return "\n".join([item for item in feed])


    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")

            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)


class TestUser(unittest.TestCase):

    def test_this_works(self):
        with self.assertRaises(UsernameException):
            raise UsernameException()

    def test_crate_user(self):
        user = User("Bobby", 5.00, "4111111111111111")
        self.assertEqual(user.username, "Bobby")
        self.assertEqual(user.balance, 5.00)
        self.assertEqual(user.credit_card_number, "4111111111111111")

    def test_minivenmo_create_user(self):
        venmo = MiniVenmo()
        user = venmo.create_user("Anna", 10.00, "4111111111111111")
        self.assertEqual(user.username, "Anna")
        self.assertEqual(user.balance, 10.00)
        self.assertEqual(user.credit_card_number, "4111111111111111")

    def test_bobby_pay_anna_with_balance(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 10.00, "4111111111111111")
        anna = venmo.create_user("Anna", 5.00, "4111111111111112")

        bobby.pay(anna, 5.00, "Coffee")

        self.assertEqual(bobby.balance, 5.00)
        self.assertEqual(anna.balance, 10.00)

    def test_bobby_pay_anna_with_credit_card(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 10.00, "4111111111111111")
        anna = venmo.create_user("Anna", 5.00, "4111111111111112")

        bobby.pay(anna, 15.00, "Coffee")

        self.assertEqual(bobby.balance, 10.00)
        self.assertEqual(anna.balance, 20.00)

    def test_retrieve_feed(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 10.00, "4111111111111111")
        anna = venmo.create_user("Anna", 5.00, "4111111111111112")

        bobby.pay(anna, 5.00, "Coffee")
        feed = venmo.render_feed(bobby.retrieve_feed())

        self.assertEqual(feed, "Bobby paid Anna $5.0 for Coffee")

    def test_user_add_friend(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 10.00, "4111111111111111")
        anna = venmo.create_user("Anna", 5.00, "4111111111111112")

        bobby.add_friend(anna)
        feed = bobby.retrieve_feed()

        self.assertEqual(bobby.friends, [anna])
        self.assertEqual(feed[0], "Bobby added Anna as friends")

if __name__ == '__main__':
    unittest.main()

