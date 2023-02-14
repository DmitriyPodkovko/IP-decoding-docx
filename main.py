# Decoding the organization's IP address from docx using ipinfo
from re import compile
from sys import exit
from docx import Document
from sqlite3 import connect
from requests import get
from datetime import datetime, timedelta
from const import constants as c
from db import queries as q


def get_next_token():
    try:
        token = next(c.ITERATOR_TOKENS, '-1')
        if token == '-1':
            exit('TOKENS ARE ENDED !!!')
        print('Run ' + token)
        return token
    except Exception as e_tkn:
        print(f'Token assignment error: {str(e_tkn)}')


def get_response(url, ip_address, token):
    try:
        response = get(url + ip_address + token)
        print(response.status_code.__str__() + ' ' + ip_address + ' ' + url + ip_address + token)
        if response.status_code == 200:
            result = (f"{response.json()['city'] if 'city' in response.json() else 'No City'}, "
                      f"{response.json()['country'] if 'country' in response.json() else 'No Country'}, "
                      f"{response.json()['org'] if 'org' in response.json() else 'No Organisation'}")
            if type(result) is tuple:
                result = result[0]
            return result, token
        elif response.status_code == 429:
            token = get_next_token()
            return get_response(url, ip_address, token), token
    except Exception as e_req:
        print(f'Request execution error: {url + ip_address + token} ({str(e_req)})')


def handler(input_file, url, token, output_file):
    try:
        document = Document(input_file)
        count_resp_db = 0
        count_resp_ipinfo = 0
        count_insert_db = 0
        count_update_db = 0
        try:
            with connect(c.DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(q.QUERIES['CREATE_TABLE'])  # IF NOT EXISTS
                for paragraph in document.paragraphs:
                    ip_pattern = compile(r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}')
                    ip_list = ip_pattern.findall(paragraph.text)
                    for ip in range(0, len(ip_list)):
                        # Select from {DB_NAME}.db
                        cur.execute(q.QUERIES['GET_IP'], (ip_list[ip],))
                        row = cur.fetchone()
                        # check if IP exists in {DB_NAME}.db
                        if row is None:
                            # IP absent then make a request and insert result into {DB_NAME}.db
                            whois, token = get_response(url, ip_list[ip], token)
                            count_resp_ipinfo += 1
                            paragraph.text = paragraph.text.replace(ip_list[ip],
                                                                    ip_list[ip] + ' - ' + whois)
                            print(paragraph.text)
                            cur.execute(q.QUERIES['INSERT_IP'], (ip_list[ip], whois,))
                            conn.commit()
                            count_insert_db += 1
                        else:
                            # IP exist in {DB_NAME}.db
                            # get date now and calculate out of date (limit_date)
                            db_update_at = datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
                            today = datetime.now().replace(microsecond=0)
                            limit_date = today - timedelta(days=c.LIMIT_DAY)
                            # if IP date in {DB_NAME}.db is out of date
                            # then make a request and update IP date in {DB_NAME}.db
                            if db_update_at < limit_date:
                                whois, token = get_response(url, ip_list[ip], token)
                                count_resp_ipinfo += 1
                                paragraph.text = paragraph.text.replace(ip_list[ip],
                                                                        ip_list[ip] + ' - ' + whois)
                                print(paragraph.text)
                                cur.execute(q.QUERIES['UPDATE_IP'], (whois, today, ip_list[ip],))
                                conn.commit()
                                count_update_db += 1
                            else:
                                # IP date in {DB_NAME}.db is fresh
                                whois = row[2]
                                paragraph.text = paragraph.text.replace(ip_list[ip],
                                                                        ip_list[ip] + ' - ' + whois)
                                print(paragraph.text)
                                count_resp_db += 1
        except Exception as e_db:
            print(f'DB error: {str(e_db)}')
        document.save(output_file)
        print(f'Number of responses from the database: {count_resp_db}')
        print(f'Number of responses from {c.IPINFO_URL}: {count_resp_ipinfo}')
        print(f'Number of ip inserted into the database: {count_insert_db}')
        print(f'Number of ip updated in the database: {count_update_db}')
    except Exception as e_docx:
        print(f'DOCX error: {str(e_docx)}')


if __name__ == '__main__':
    tkn = get_next_token()
    if c.LIMIT_DAY == 0:
        c.LIMIT_DAY = 1
    handler(c.IN_FILE, c.IPINFO_URL, tkn, c.OUT_FILE)
