#!/usr/bin/python
__author__ = "Justin Stals"

# Takes in text via file or string and
# returns a dictionary of entities it mentions.

# The dictionary keys are entity categories, the values
# are the list of entities that fit that category

import os
import csv
import sys
import json
import pprint

# Required Google Cloud packages
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud.bigquery.client import Client
from oauth2client.client import GoogleCredentials

# Save your client_secrets.json file in the current directory

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getcwd() + f'/client_secret.json'
try:
	client = language.LanguageServiceClient()
except:
	print('Please save your client_secret.json file in the current directory.')

entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION', 'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')
mention_type = ('TYPE_UNKNOWN', 'PROPER', 'COMMON')

# Pass in a string of text and receive
# a list of the entities it mentions.

def find_entities(text, max_entities=10):

	document = types.Document(
    	content=text,
    	type=enums.Document.Type.PLAIN_TEXT
    )

	sentiment = client.analyze_sentiment(document=document).document_sentiment
	entities = client.analyze_entities(document=document).entities

	return simplify(entities)

# Parse out just the names of the entities in each respective category

def simplify(entities):

	result = {
		'people' : [],
		'locations' : [],
		'organizations' : [],
		'events' : [],
		'artworks' : [],
		'consumer_goods' : [],
		'other' : [],
		'unknown' : [],
	}

	for entity in entities:
		for mention in entity.mentions:
			if mention_type[mention.type] == 'PROPER':
				if entity_type[entity.type] == 'PERSON':
					if not entity.name in result['people']:
						result['people'].append(entity.name)
				elif entity_type[entity.type]== 'ORGANIZATION':
					if not entity.name in result['organizations']:
						result['organizations'].append(entity.name)
				elif entity_type[entity.type] == 'LOCATION':
					if not entity.name in result['locations']:
						result['locations'].append(entity.name)
				elif entity_type[entity.type] == 'EVENT':
					if not entity.name in result['events']:
						result['events'].append(entity.name)
				elif entity_type[entity.type] == 'WORK_OF_ART':
					if not entity.name in result['artworks']:
						result['artworks'].append(entity.name)
				elif entity_type[entity.type] == 'CONSUMER_GOOD':
					if not entity.name in result['consumer_goods']:
						result['consumer_goods'].append(entity.name)
				elif entity_type[entity.type] == 'OTHER':
					if not entity.name in result['other']:
						result['other'].append(entity.name)
				elif entity_type[entity.type] == 'UNKNOWN':
					if not entity.name in result['unknown']:
						result['unknown'].append(entity.name)

	return result

# Pass in a text file name in the current directory
# and receive the text it contains as a string.

def parse_file(text_file):

	file_path = os.getcwd() + f'/{text_file}'

	return open(file_path, 'r').read()

# Run by passing in your text file via the command line

def command_line():

	try:
		if client:

			if len(sys.argv) == 2:

				text = parse_file(sys.argv[1])
				pp = pprint.PrettyPrinter(depth=2)
				pp.pprint(find_entities(text))

			elif len(sys.argv) == 3:
				text = parse_file(sys.argv[1])
				pp = pprint.PrettyPrinter(depth=2)
				pp.pprint(find_entities(text, sys.argv[2]))

			else:
				print('Usage: python gcloud_entities.py <text_file> <number_of_entities (optional)>')
				print('Example: python gcloud_entities.py example.txt 5')
	except NameError:
		return

if __name__ == '__main__':
	command_line()
	