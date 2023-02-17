IPINFO_URL = 'https://ipinfo.io/'
# for example: iter(('', '?token=token1', '?token=token2', '?token=token3'))
ITERATOR_TOKENS = iter(('', '', '', '', ''))
IN_FILE = 'example.docx'
OUT_FILE = 'result_' + IN_FILE
DB_NAME = 'ip_resolved_list.db'
# how many days to consider the 'whois' field is out of date
# and need to updated at the time of the request
LIMIT_DAY = 5
