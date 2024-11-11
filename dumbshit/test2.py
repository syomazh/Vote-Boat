from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv

import requests
import xmltodict
import xml.etree.ElementTree as ET

load_dotenv()

app = Flask(__name__)

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
VOTESMART_KEY = os.getenv("VOTESMART_API_KEY")

WIKIPEDIA_API_URL = 'https://en.wikipedia.org/w/api.php'
VOTE_SMART_URL = 'http://api.votesmart.org'

VOTE_CONTEXT = 75

def get_candidate_id(full_name):
    # Split the full name into first and last names
    name_parts = full_name.split()
    if len(name_parts) < 2:
        return "not found"
    
    first_name = name_parts[0]
    last_name = name_parts[-1]
    
    params = {
        'key': VOTESMART_KEY,
        'lastName': last_name
    }
    response = requests.get(f'{VOTE_SMART_URL}/Candidates.getByLastname', params=params)
    
    # Parse the XML response
    data = xmltodict.parse(response.text)
    
    if 'candidateList' in data and 'candidate' in data['candidateList']:
        candidates = data['candidateList']['candidate']
        if isinstance(candidates, list):
            return candidates[0]['candidateId']
        else:
            return candidates['candidateId']
    return "not found"

get_candidate_id("John Smith")
def get_candidate_id(full_name):
    # Split the full name into first and last names
    name_parts = full_name.split()
    if len(name_parts) < 2:
        return "not found"
    
    first_name = name_parts[0]
    last_name = name_parts[-1]
    
    params = {
        'key': VOTESMART_KEY,
        'lastName': last_name
    }
    response = requests.get(f'{VOTE_SMART_URL}/Candidates.getByLastname', params=params)
    
    # Parse the XML response
    data = xmltodict.parse(response.text)
    
    if 'candidateList' in data and 'candidate' in data['candidateList']:
        candidates = data['candidateList']['candidate']
        if isinstance(candidates, list):
            for candidate in candidates:
                if candidate['firstName'] == first_name or candidate.get('nickName') == first_name:
                    return candidate['candidateId']
        else:
            if candidates['firstName'] == first_name or candidates.get('nickName') == first_name:
                return candidates['candidateId']
    return "not found"

print(get_candidate_id("Adrian Smith"))

# 21284