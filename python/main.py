from hashlib import sha1, md5
from collections import OrderedDict
from urllib.parse import urlencode
import hmac
import requests
import base64
import json
import pymysql



api_key      = ''
secret_key   = ''

database_address = '127.0.0.1'
database_name = 'asterisk'
database_user = 'asterisk'
database_password = ''
zadarma_api_url = 'http://api.zadarma.com'

monthly_fee_all = 0

debug = True
# debug = False

db = pymysql.connect(database_address, database_user, database_password, database_name)
cursor = db.cursor()

def sql_insert():

    sql = "REPLACE zadarma_numbers (id, date, number, number_name, description, sip, start_date, stop_date, monthly_fee, status, channels, autorenew) \
          VALUES (NULL, UTC_TIMESTAMP(), '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % \
          (number,number_name, description, sip, start_date, stop_date, monthly_fee, status, channels, autorenew)
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()

def zapros(method,data):
    if not data:
        data = {'format': 'json'}
    sorted_dict_params = OrderedDict(sorted(data.items()))
    query_string = urlencode(sorted_dict_params)
    h = md5(query_string.encode('utf8')).hexdigest()
    data = method + query_string + h
    hashed = hmac.new(secret_key.encode('utf8'), data.encode('utf8'), sha1)
    auth = api_key + ':' + base64.b64encode(bytes(hashed.hexdigest(), 'utf8')).decode()

    headers = {'User-Agent': '-', 'Authorization': auth}
    url = zadarma_api_url + method + '?' + query_string;
    r = requests.get(url, headers=headers)
    return json.loads(r.text)
    # print(r.text)
numbers = zapros('/v1/direct_numbers/', '')
if debug:
    print(numbers['info'])
for res in numbers['info']:

    description = res['description']
    number = res['number']
    number_name = res['number_name']
    start_date = res['start_date']
    stop_date = res['stop_date']
    sip = res['sip']

    if res['autorenew'] ==  'true':
        autorenew = 0
    else:
        autorenew = 1

    monthly_fee = res['monthly_fee']

    if res['status'] == 'on':
        status = 0
    else:
        status = 1
    channels = res['channels']
    monthly_fee_all = monthly_fee_all + monthly_fee
    if debug:
        print('number', number)
        print('description', description)
        print('sip',sip)
        print('number_name', number_name)
        print('start_date', start_date)
        print('stop_date', stop_date)
        print('monthly_fee',monthly_fee)
        print('status', status)
    # print('monthly_fee_all',monthly_fee_all)
    if autorenew != 0:
        if debug:
            print('!!!!!!!!!!!!!!!\nautorenew OFF\n!!!!!!!!!!!!!!!\n')
    if debug:
        print()

    sql_insert()


balance_info = zapros('/v1/info/balance/','')
balance = balance_info['balance']

if debug:
    print('balance', balance)
    print('monthly_fee_all',monthly_fee_all)

sql = "REPLACE zadarma_balance (id, date, balance, monthly_fee) VALUES (NULL, UTC_TIMESTAMP(), '%s', '%s');" % (balance, monthly_fee_all)
try:

    cursor.execute(sql)
    db.commit()
except:
    db.rollback()
if debug:
    print('doplata -->', balance - monthly_fee_all )
    print('monthly_fee_all', monthly_fee_all)
db.close()
