from bs4 import BeautifulSoup
import requests
import argparse
import json

# Arguments Parser
parser = argparse.ArgumentParser(description='Convert Quizlet to JSON or Text')
parser.add_argument('-j', '--json', action='store_false', default=False,
                    dest='file_format',
                    help='Convert the data to JSON format [DEFAULT]')
parser.add_argument('-t', '--text', action='store_true', default=False,
                    dest='file_format',
                    help='Convert the data to Text format')
parser.add_argument('-l', '--left', action='store_false', default=False,
                    dest='question_switch',
                    help='Set the flag if questions on left [DEFAULT]')
parser.add_argument('-r', '--right', action='store_true', default=False,
                    dest='question_switch',
                    help='Set the flag if questions on right')
parser.add_argument('-u', '--url', type=str, required=True,
                    help='Quizlet URL [Required]')
args = parser.parse_args()

# Constants
OUTPUT_TAG = args.file_format
QS_FLAG = args.question_switch
URL = args.url
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                  'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                  'Chrome/84.0.4147.89 Safari/537.36'
}


def get_response(url):
    """ Get the response object """
    if url is None:
        print("URL not provided")
    else:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f'Error {response.status_code}: Request Failed!')
        return response


def convert_to_json(rsp, flag):
    """Convert the data to JSON format"""
    quiz_list = []
    soup = BeautifulSoup(rsp.text, "html.parser")
    for mainDiv in soup.find_all("div", class_="SetPageTerm-content"):
        # Removing <span>
        for matched in mainDiv.findAll('span'):
            matched.unwrap()
        # Replacing <br> with line break
        for breaks in mainDiv.findAll('br'):
            breaks.replace_with('\n')
        json_data = {}
        definition = mainDiv.find(
            'a', attrs={'class': 'SetPageTerm-definitionText'})
        answer = mainDiv.find('a', attrs={'class': 'SetPageTerm-wordText'})
        if flag is True:
            json_data['Question'] = answer.text
            json_data['Answer'] = definition.text
        else:
            json_data['Question'] = definition.text
            json_data['Answer'] = answer.text
        quiz_list.append(json_data)
    # Exporting to a JSON file
    json_data = json.dumps(quiz_list)
    data = json.loads(json_data)
    with open('data.json', 'w') as f:
        json.dump(data, f)


def convert_to_text(rsp, flag):
    """ Convert the data to Text file format """
    soup = BeautifulSoup(rsp.text, "html.parser")
    count = 1
    with open('data.txt', 'w', encoding='utf-8') as f:
        for mainDiv in soup.find_all("div", class_="SetPageTerm-content"):
            for matched in mainDiv.findAll('span'):
                matched.unwrap()
            for breaks in mainDiv.findAll('br'):
                breaks.replace_with('\n')
            answer = mainDiv.find('a', attrs={'class': 'SetPageTerm-wordText'})
            definition = mainDiv.find(
                'a', attrs={'class': 'SetPageTerm-definitionText'})
            if flag is True:
                f.write(f'Question {count}\n')
                f.write(f'{answer.text}\n\n')
                f.write(f'Answer: {definition.text}\n\n')
            else:
                f.write(f'Question {count}\n')
                f.write(f'{definition.text}\n\n')
                f.write(f'Answer: {answer.text}\n\n')
            count = count + 1


rsp = get_response(URL)
if OUTPUT_TAG is False:
    convert_to_json(rsp, QS_FLAG)
else:
    convert_to_text(rsp, QS_FLAG)
