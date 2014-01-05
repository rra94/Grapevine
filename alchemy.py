from alchemyapi import AlchemyAPI
alchemyapi = AlchemyAPI()

def alchemical_response(myText):
	response = alchemyapi.sentiment("text", myText)
	try:
		tup = response["docSentiment"]["type"], response["docSentiment"]["score"]
	except KeyError:
		tup = "neutral", 0
	return tup


