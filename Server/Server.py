from flask import Flask, request, redirect
from tinydb import TinyDB, Query
import twilio.twiml

app = Flask(__name__)
db = TinyDB('db.json')
NumberSearch = Query()

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
	"""Respond to incoming calls with a simple text message."""
	resp = twilio.twiml.Response()
	number = request.values.get('From')
	if len(db.search(NumberSearch.number == number)) == 0:
		print "Unknown number added: "+request.values.get('From')
		db.insert({'number':request.values.get('From'), 'count':0})
	record = db.search(NumberSearch.number == number)[0]
	db.update({'count': record['count']+1}, NumberSearch.number == number)
	message = "Responses: "+str(record['count'])
	resp.message(message)
	print "responded with \""+message+"\""
	return str(resp)

if __name__ == "__main__":
		app.run(debug=True, host='0.0.0.0')