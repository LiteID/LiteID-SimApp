from flask import Flask, request
from test import LiteIDContract
import twilio.twiml
import hashlib
import signal
import shelve
import random
import re

class InteractionStateMachine:
	def __init__(self, number):
		self.registered = False
		self.number = number
		self.state = "Start"
		self.items = {}
		self.Privatekey = "lol"
		self.AddressCheck = ""

	def run(self, body):
		stateArr = {
			"Start": self.s_start,
			"Actions": self.Actions,
			"create_account": self.create_account,
			"AddressCheck": self.what_is_the_address,
			"HashCheck": self.check_hash,
			"Exit": self.exit_prompt
		}
		return stateArr[self.state](body)

	def _caculate_hash(self, data):
		salt = bytearray(random.getrandbits(8) for i in range(32))
		origanal_hash = hashlib.sha256(data)
		salted_hash = hashlib.sha256(origanal_hash.digest() + salt)
		salt = (''.join('{:02x}'.format(x) for x in salt)).decode("hex")
		origanal_hash = origanal_hash.hexdigest().decode("hex")
		salted_hash = salted_hash.hexdigest().decode("hex")
		return salted_hash, salt, origanal_hash, data

	def Actions(self, body):
		if "addr" in body[0:6].lower():
			return self.Privatekey
		elif "ADD" in body[0:6]:
			m = re.match(u"ADD(.*)", body, flags=re.IGNORECASE)
			if m:
				res = self._caculate_hash(m.group(1).strip())
				self.items[res[2]] = res
				return "added {}".format(m.group(1).strip())
			else:
				return "could not find item to add"
		elif "show" in body[0:6].lower():
			output = ""
			for i in self.items:
				output += "{}\n".format(i[3])
			return output
		elif "check" in body[0:5].lower():
			self.state = "AddressCheck"
			return "What is the Address?"
		else:
			return "Actions: \nPrint Address: ADDR\nAdd Item: ADD <Text to add>\nShow Items: SHOW\nCheck Identity: CHECK"

	def s_start(self, body):
		if self.registered:
			self.state = "Actions"
			return "Actions: \nPrint Address: ADDR\nAdd Item: ADD <Text to add>\nShow Items: SHOW\nCheck Identity: CHECK"
		else:
			self.state = "create_account"
			return "Create Account? (y/n)"

	def create_account(self, body):
		if 'y' in body or 'Y' in body:
			# Create Etherium acount
			self.state = "Actions"
			return "Account Created\n\nActions: \nPrint Address: ADDR\nAdd Item: ADD <Text to add>\nShow Items: SHOW\nCheck Identity: CHECK"
		else:
			self.state = "Start"
			return ""

	def what_is_the_address(self, body):
		m = re.match("(0x[0-9a-f]{40})", body)
		if m:
			self.state = "HashCheck"
			self.AddressCheck = m.group(1)
			return "What is the hash to check?"
		elif "exit" in body.lower():
			self.state = "Actions"
			return "Account Created\n\nActions: \nPrint Address: ADDR\nAdd Item: ADD <Text to add>\nShow Items: SHOW\nCheck Identity: CHECK"
		else:
			return "Invalid address Try again or EXIT to exit"

	def check_hash(self, body):
		m = re.match("(0x[0-9a-f]{40})", body)
		a = LiteIDContract(contract_id=self.AddressCheck)
		hashes = a.dump_hashes()

		if m:
			orig = m.group(1)
		else:
			orig = hashlib.sha256(body).digest()
		for h in hashes:
			if hashlib.sha256(orig+h[1]) == h[0]:
				self.state = "Exit"
				return "Valid"
		self.state = "Exit"
		return "Not Valid"


	def exit_prompt(self, body):
		if "y" in body[0:6].lower():
			self.state = "Actions"
			return "Account Created\n\nActions: \nPrint Address: ADDR\nAdd Item: ADD <Text to add>\nShow Items: SHOW\nCheck Identity: CHECK"
		else:
			self.state = "HashCheck"
			return "What is the hash to check?"


app = Flask(__name__)
db = shelve.open('storage.db', writeback=True)

@app.route("/", methods=['GET', 'POST'])
def main_entry():
	"""Main entry for the state machine"""
	resp = twilio.twiml.Response()
	number = str(request.values.get('From'))
	if number not in db.keys():
		print "New number {}".format(number)
		temp = InteractionStateMachine(number)
		db[number] = temp
	message = str(db[number].run(request.values.get('Body')))
	resp.message(message)
	print "responded to \"{}\" with \"{}\"".format(request.values.get('Body'), message)
	return str(resp)


# Close the DB  on quit
def cleanup(signal, frame):
	db.close()
	print "Database Closed"

signal.signal(signal.SIGINT, cleanup)

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')
