# -*- coding: utf-8 -*
import time
from multiprocessing.dummy import Pool as ThreadPool
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def html_page(url):
    request = session.get(url)
    return request.text


def write_to_file(question, answer, number_file):
    with open('question-answer1\\' + 'file' + str(number_file) + '.txt', 'w', encoding='utf-8') as output_file:
        try:
            for i in range(len(question)):
                for j in range(len(question[i])):
                    output_file.write(question[i][j] + '\t' + answer[i][j] + '\n')
        except IndexError:
            print('Ошибка в размерности списка!')
            print('Размерность: question[', i,']=',len(question[i]))
            print('Размерность: answer[', i,']=',len(answer[i]))



def find_fake_question(fake_question,fake_answer):
    for i in range(len(fake_question)):
        if len(fake_question[i]) != len(fake_answer[i]):
            print('Размерность...')
            print('Было вопросов:', len(fake_question[i]))
            print('Было ответов:', len(fake_answer[i]))
            j = 0
            while j < len(fake_question[i]):
                if fake_question[i][j] == ('.     \n'):
                    fake_question[i].pop(j)
                    continue
                j += 1
            print('Стало вопросов:', len(fake_question[i]))
            print('Стало ответов:', len(fake_answer[i]))
    return fake_question, fake_answer


def get_last_page():
    soup = BeautifulSoup(html_page(url_first_page), 'html5lib')
    page = soup.find('li', {'class': 'pager-last last'}).find('a').get('href')
    number_pages = int(page[len(page) - 2] + page[len(page) - 1])
    return number_pages


def get_urls_pages(url):
    data = html_page(url)
    soup = BeautifulSoup(data, 'html5lib')
    path_block_tours = soup.find_all('tr', {'class': ['odd', 'even']})
    path_tour = [path_block_tours[i].find_all('a') for i in range(len(path_block_tours))]
    urls = []
    for i in range(len(path_tour)):
        if len(path_tour[i]) > 1:
            for j in range(1, len(path_tour[i])):
                urls.append(url_first_page + path_tour[i][j].get('href'))
        else:
            urls.append(url_first_page + path_tour[i][0].get('href'))

    return urls


def get_question(url):
    data = html_page(url)
    soup = BeautifulSoup(data, 'html5lib')
    path_question = soup.find_all('div', {'class': 'question'})
    question = []
    if len(path_question) > 0 and len(soup.find_all('div', {'style': 'margin-top:20px;'})) == 0:
        for i in range(len(path_question)):
            question.append(path_question[i].p.text + '\n')
    elif len(path_question) > 0 and len(soup.find_all('div', {'style': 'margin-top:20px;'})) != 0:
        # записать class='margin-top:20px;'
        path_block_question = soup.find_all('div', {'style': 'margin-top:20px;'})
        path_question = [path_block_question[i].find_all('p') for i in range(len(path_block_question))]
        for i in range(len(path_question)):
            for j in range(len(path_question[i])):
                if path_question[i][j].i is None:
                    question.append(path_question[i][j].text + '\n')
        # записать class='question'
        path_question = soup.find_all('div', {'class': 'question'})
        for i in range(len(path_question)):
            question.append(path_question[i].p.text + '\n')
    else:
        # записать class='margin-top:20px;'
        path_block_question = soup.find_all('div', {'style': 'margin-top:20px;'})
        path_question = [path_block_question[i].find_all('p') for i in range(len(path_block_question))]
        for i in range(len(path_question)):
            for j in range(len(path_question[i])):
                if path_question[i][j].i is None:
                    question.append(path_question[i][j].text + '\n')
    return question


def get_answer(url):
    data = html_page(url)
    soup = BeautifulSoup(data, 'html5lib')
    path_answer = soup.find_all('div', {'class': 'collapsible collapsed'})
    path_question = soup.find_all('div', {'class': 'question'})
    answer = []
    if len(path_question) > 0 and len(soup.find_all('div', {'style': 'margin-top:20px;'})) == 0:
        for i in range(len(path_answer)):
            answer.append(path_answer[i].p.text + '\n')
    elif len(path_question) > 0 and len(soup.find_all('div', {'style': 'margin-top:20px;'})) != 0:
        # записать class='collapsible collapsed'
        for i in range(len(path_answer)):
            answer.append(path_answer[i].p.text + '\n')
    else:
        for i in range(len(path_answer)):
            if path_answer[i].p is not None:
                answer.append(path_answer[i].p.text + '\n')
    return answer


def get_file_with_questions_and_answers(number_pages):
    number_file = 0
    pool = ThreadPool(10)
    for k in tqdm(range(number_pages+1)):
        urls = get_urls_pages('https://db.chgk.info/last?page=' + str(k))  # получить ссылки на все туры турниров
        question = pool.map(get_question, urls)
        answer = pool.map(get_answer, urls)
        question,answer = find_fake_question(question,answer)
        write_to_file(question, answer, number_file) # записать вопросы и ответы турнира (все туры)
        number_file += 1
    pool.close()
    pool.join()
    return


if __name__ == '__main__':
    time_begin = time.time()
    session = requests.Session()
    session.headers.update({
        'User-Agent':
            'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    })

    url_first_page = 'https://db.chgk.info/'  # первая страница
    number_pages = get_last_page()  # всего страниц
    get_file_with_questions_and_answers(number_pages)

    print('Время исполнения программы: ', time.time() - time_begin)
    exit()
