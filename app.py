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


## VOTE SMART


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
    

def get_candidate_votes(api_key, candidate_id):
    url = f"https://api.votesmart.org/Votes.getByOfficial"
    params = {
        'key': api_key,
        'candidateId': candidate_id,
        'o': 'xml'  # Get results in XML format
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.content)
            return root
        except ET.ParseError:
            print("Error: Response is not valid XML")
            print("Response text:", response.text)
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
def get_candidate_votes_text(votes):
    if votes is not None:
        result_str = ""
        for i, vote in enumerate(votes.findall('.//bill')):
            if i >= VOTE_CONTEXT:
                break
            title = vote.find('title').text
            vote_action = vote.find('vote').text
            result = []
            result.append(f"Bill Title: {title}")
            result.append(f"How Voted: {vote_action}")
            result.append("-" * 30)
            result_sublevel = "\n".join(result)
            result_str += result_sublevel
        return result_str
    else:
        return("No votes found or error retrieving data.")

def get_candidate_bio(candidate_id):
    params = {
        'key': VOTESMART_KEY,
        'candidateId': candidate_id
    }
    response = requests.get(f'{VOTE_SMART_URL}/CandidateBio.getBio', params=params)
    
    # Print the response content for debugging
    # print("Bio Response Content:", response.text)
    
    # Parse the XML response
    try:
        data = xmltodict.parse(response.text)
        candidate = data.get('bio', {}).get('candidate', {})
        office = data.get('bio', {}).get('office', {})
        
        if not isinstance(candidate, dict):
            candidate = {}
        if not isinstance(office, dict):
            office = {}
        
    except Exception as e:
        return "no smart info"
    
    candidate_info = {
        'stateId': office.get('stateId', 'N/A'),
        'birthPlace': candidate.get('birthPlace', 'N/A'),
        'birthDate': candidate.get('birthDate', 'N/A'),
        'party': office.get('parties', 'N/A'),
        'religion': candidate.get('religion', 'N/A')
        

    }
    candidate_info_str = f"State ID: {candidate_info['stateId']}, Birth Place: {candidate_info['birthPlace']}, Birth Date: {candidate_info['birthDate']}, Party: {candidate_info['party']}, Religion: {candidate_info['religion']}"
    candidate_info['infoString'] = candidate_info_str
    return candidate_info_str

## WIKIPEDIA

def get_wikipedia_summary(title):
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'extracts',
        'exintro': True,
        'explaintext': True,
        'titles': title
    }
    response = requests.get(WIKIPEDIA_API_URL, params=params)
    data = response.json()
    pages = data['query']['pages']
    page = next(iter(pages.values()))
    return page['extract']


def get_wikipedia_text(title):
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'revisions',
        'rvprop': 'content',
        'titles': title
    }
    response = requests.get(WIKIPEDIA_API_URL, params=params)
    data = response.json()
    pages = data['query']['pages']
    page = next(iter(pages.values()))
    text = page['revisions'][0]['*']
    
    # If the text is too long, return the summary instead
    if len(text) > 10000:  # Adjust the length as needed
        return get_wikipedia_summary(title)
    
    return text

def get_wikipedia_links(title):
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'extlinks',
            'titles': title
        }
        response = requests.get(WIKIPEDIA_API_URL, params=params)
        data = response.json()
        pages = data['query']['pages']
        page = next(iter(pages.values()))
        if 'extlinks' in page:
            links = [link['*'] for link in page['extlinks']]
            return links
        else:
            return []
    

## OPENAI
def get_openai_links(prompt):
    """Generate a response from OpenAI API based on the prompt."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "you are an election information bot. provide 5 links on the candidate/official for research. only provide the links, NEVER say anythin else "},
                    {"role": "user", "content": prompt + " " + get_candidate_bio(get_candidate_id(prompt))}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def get_openai_response(prompt):
    """Generate a response from OpenAI API based on the prompt."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an election information chatbot."},
                    {"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"
    

def get_openai_factcheck(prompt, fact):
    """Generate a response from OpenAI API based on the prompt."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "YOU will only ever return TRUE or FALSE, do not return anything else only one word that is either TRUE or FALSE. if the following information heavily contradicts the info in the prompt respond FALSE, otherwise return TRUE info: " + fact},
                    {"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

    

def get_openai_bio(prompt, focus_issue, candidate_name):
    """Generate a response from OpenAI API based on the prompt."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": " based on the following provide a short 4-6 sentence summary on the candidate:" + str(candidate_name) +". Focus on providing info on " + str(focus_issue) + "if possible. NEVER SAY THAT YOU DO NOT HAVE OR CANNOT PROVIDE INFORMATION ON ANYTHING. try to keep it between 30-65 words" },
                    {"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def get_openai_vote(voting_record, candidate_name, focus_issue):
    """Generate a response from OpenAI API based on the prompt."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Based on the following provide a short paragraph political summary on " + str(candidate_name) + "'s voting history. Focus on providing info on " + str(focus_issue) + "if possible. NEVER SAY THAT YOU DO NOT HAVE OR CANNOT PROVIDE INFORMATION ON ANYTHING. try to keep it between 60-80 words"
                },
                {
                    "role": "user",
                    "content": voting_record
                }
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"
    


## OTHER
def get_last_name(name):
    return name.split()[-1]

def capitalize_first_letter(text):
    return ' '.join(word.capitalize() for word in text.split())

# MAIN FUNCTIONS
def fack_check(input_text, fact):
    output = get_openai_factcheck(input_text, fact)
    if output == "FALSE":
        return False
    else:
        return True
    
def get_links(input_text, id):
    full_name = input_text
    
    bio = get_candidate_bio(id)
    
    return get_openai_links(full_name + " " + bio)



def get_bio_info(input_text, id, focus_issue):
    full_name = input_text
    wiki_text = "No wikipedia info found"
    try:
        wiki_text = get_wikipedia_text(full_name)
    except Exception as e:
        pass
    
    smart_data = get_candidate_bio(id)
    return get_openai_bio( "Smart Data {" + smart_data +  "} " + wiki_text, focus_issue, full_name)

def get_vote_info(input_text, id, focus_issue):
    full_name = input_text
    last_name = get_last_name(full_name)
    if last_name == "not found":
        return "No info on candidate"
    
    votes = get_candidate_votes(VOTESMART_KEY, id)
    
    vote_text = get_candidate_votes_text(votes)
    response = get_openai_vote(vote_text , full_name, focus_issue)
    print("focus issue", focus_issue)
    return response


    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    focus_issue = request.json.get("topic")
    
    if not user_input:
        return jsonify({"error": "No Info found"}), 400
    
    full_name = capitalize_first_letter(user_input)
    last_name = get_last_name(full_name)
    
    if not last_name:
        return jsonify({"error": "No info found"}), 400
    
    id = get_candidate_id(full_name)
    
    if not id:
        return jsonify({"error": "NO info found"}), 404
    
    bio = get_bio_info(full_name, id, focus_issue)
    vote = get_vote_info(full_name, id, focus_issue)
    links = get_links(full_name, id)
    
    # if bio is None or vote is None or links is None:
    #     return jsonify({"error": "Failed to retrieve candidate information"}), 500
    
    print("Bio:", bio)
    return jsonify({
        "bio": bio,
        "vote": vote,
        "links": links,
        "info": "Additional candidate info here"  # Add extra data if needed
    })

    

if __name__ == '__main__':
    app.run(debug=True)
