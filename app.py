import re

from flask import Flask, jsonify, render_template
from bs4 import BeautifulSoup
import requests
from purl import URL

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/url=<path:q_link>')
def get_answers(q_link):
    url = URL(q_link)
    if url.domain() not in ['quora.com', 'www.quora.com']:
        return 'error, not quora'

    url = URL(
        scheme='https',
        host='www.quora.com',
        path=url.path(),
        query='share=1').as_string()

    soup = BeautifulSoup(requests.get(url).text)

    question = {}
    question['url'] = url
    question['title'] = soup.find("div", {"class": "question_text_edit"}).text
    question['topics'] = [topic.text for topic in soup.find_all("span", {"class": "TopicName"})]
    question['details'] = soup.find("div", {"class": "question_details_text"}).text

    answers = []

    divs = soup.find_all("div", {"class": "pagedlist_item"})
    
    try:
        ans_count = soup.find("div", {"class": "answer_count"}).text.strip()
        count = int(re.match(r'(\d+) Answers', ans_count).groups()[0])
    except:
        return jsonify(question=question, answers=answers)

    question['answer_count'] = count

    count = len(divs) - 1 if count < 6 else 6
    for i in range(count):
        one_answer = {
            'votes': '-1',
            'rank': 0,
            'answer': ''
        }
        author = {
            'name': 'Anonymous'
        }
        try:
            author['name'] = divs[i].find("div", {"class": "author_info"}).find("span", {"class": "feed_item_answer_user"}).find("a", {"class": "user"}).string
            author['bio'] = divs[i].find("div", {"class": "author_info"}).find("span", {"class": "feed_item_answer_user"}).find_all("span", {"class": "rep"})[1].find("span", {"class": "hidden"}).text
        except:
            author['bio'] = ''
        one_answer['author'] = author

        one_answer['votes'] = divs[i].find("span", {"class":"count"}).text

        html_block = divs[i].find("div", {"id": re.compile("(.*)_container")})
        one_answer['answer_html'] = html_block.prettify()
        one_answer['answer'] = html_block.text
        one_answer['rank'] = i + 1
        answers.append(one_answer)

    return jsonify(question=question, answers=answers)

@app.route('/topic=<path:s_link>')
def get_questions(s_link):
    url = URL(s_link)
    if url.domain() not in ['quora.com', 'www.quora.com']:
        return 'error, not quora'

    url = URL(
        scheme='https',
        host='www.quora.com',
        path=url.path(),
        query='share=1').as_string()

    soup = BeautifulSoup(requests.get(url).text)

    topic = {}
	# TODO: Find out what the next line should actually say
    topic['text'] = url.path

    questions = []

    divs = soup.find_all("div", {"class": "pagedlist_item"})
    
    try:
		# I don't think there's a direct equivalent to "answer_count".
		# More questions load if you scroll down.
		# Might need a different data structure.
        q_count = soup.find("div", {"class": "question_count"}).text.strip()
        count = int(re.match(r'(\d+) Answers', q_count).groups()[0])
    except:
        return jsonify(topic=topic, questions=questions)

    #topic['question_count'] = count

	# Does the count thing apply? If not, find another way.
    count = len(divs) - 1 if count < 6 else 6
    for i in range(count):
        one_question = {
            'url': '',
			'title': ''
        }
        try:
            author = {}
            author['name'] = divs[i].find("div", {"class": "author_info"}).find("span", {"class": "feed_item_answer_user"}).find("a", {"class": "user"}).string
            author['bio'] = divs[i].find("div", {"class": "author_info"}).find("span", {"class": "feed_item_answer_user"}).find_all("span", {"class": "rep"})[1].find("span", {"class": "hidden"}).text
        except:
            author['name'] = 'Anonymous'
            author['bio'] = ''
        one_question['author'] = author

        return jsonify(topic=topic, questions=questions, one_question=one_question)

        one_question['votes'] = divs[i].find("span", {"class":"numbers"}).text

        html_block = divs[i].find("div", {"id": re.compile("(.*)_container")}).contents
        question_html = ''
        for p in range(len(html_block) - 1):
            question_html += str(html_block[p])
        one_question['question_html'] = question_html
        one_answer['question'] = divs[i].find("div", {"class": "question_content"}).text
        one_answer['rank'] = i + 1
        answers.append(one_answer)

    return jsonify(topic=topic, questions=questions)

if __name__ == '__main__':
    app.run(debug=True)
