import json
import pymysql
import argparse
import sys
import base64
import hmac
import requests
from hashlib import sha1, md5
from collections import OrderedDict
from urllib.parse import urlencode


api_key      = ''
secret_key   = ''

database_address = '127.0.0.1'
database_name = 'asterisk'
database_user = 'asterisk'
database_password = ''
zadarma_api_url = 'http://api.zadarma.com'
monthly_fee_all = 0

def sql_result(sql):
    cursor.execute(sql)
    data = cursor.fetchall()
    return data

def str_for_json(data):
    json_data = []
    for result in data:
        json_data.append(dict(zip(['{#NUMBER}'], result)))
    json_data = ({"data":json_data})
    return json.dumps(json_data)
    # return json.dumps(json_data)

def createParser():
    parser = argparse.ArgumentParser(
        prog='Zadarma for Zabbix',
        description='''Это программа предназначена для мониторинга номеров провайдера Zadarma
        и изначально задумывалась как скрипт для zabbiz агента.''',
        epilog='''(c) Июль 2018. Автор программы, как всегда,
    не несет никакой ответственности ни за что.'''
    )

    parser.add_argument('-l', '--allnumbers', action='store_true',
                        help='"Show all found phone numbers in a format suitable for zabbix. '
                             ' Running a script without parameters (or with the -f option) leads to the same result."')
    parser.add_argument('-n', '--number', help = '"Phone number and -s or -S or -g or -e or -d or -m or -a "', metavar = 'phone number')
    parser.add_argument('-S', '--status', action='store_true')
    parser.add_argument('-g', '--start_date', action='store_true')
    parser.add_argument('-e', '--stop_date', action='store_true')
    parser.add_argument('-d', '--description', action='store_true')
    parser.add_argument('-s', '--sip', action='store_true', help='"can be used in combination with "-c""')

    parser.add_argument('-m', '--monthly_fee', action='store_true', help='"The amount required to renew a phone number or all phone numbers"')
    parser.add_argument('-a', '--autorenew', action='store_true')
    parser.add_argument('-b', '--balance', action='store_true', help='All balance numbers')
    parser.add_argument('-f', '--force_API', action='store_true',default=False, help = '"Force the use of api, the database is ignored"')

    parser.add_argument('-c', '--cut', type=int, default=0, help='''Used only in conjunction with "-s"
                                                                     0 - The whole line,
                                                                     1- Part of the string before "@",
                                                                     2 - Part of the line after "@"''', metavar='[0,1,2] or none')
    return parser

def api_zapros(method,data):
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
    r.raise_for_status()
    return json.loads(r.text)

def no_sql(*args):
    number = args[0]
    parametr = args[1]
    for number_string in numbers_result['info']:
        if number_string['number'] == number:
            if number_string[parametr] == 'true' or number_string[parametr] == 'on':
                return '0'
            elif number_string[parametr] == 'false' or number_string[parametr] == 'off':
                return '1'
            else:
                return number_string[parametr]

def zapros(*args):
    if namespace.force_API:
        return no_sql(namespace.number,args[0])
    else:
        return sql_result(sql)[0][0]

parser = createParser()
namespace = parser.parse_args(sys.argv[1:])



if not namespace.force_API:
    try:
        db = pymysql.connect(database_address, database_user, database_password, database_name)
        cursor = db.cursor()
    except pymysql.Error as e:
        print('\n\t!!!!!!!!!!!SQL no connect!!!!!!!!!!!\n')
        print(e)
        exit(1)
else:
    try:
        numbers_result = api_zapros('/v1/direct_numbers/', '')
        balance_info = api_zapros('/v1/info/balance/', '')
    except Exception as e:
        print('Error connect API zadarma')
        exit(1)

# print('namespace', namespace)


if namespace.number and namespace.status:
    sql = "SELECT status FROM zadarma_numbers WHERE number = %s;" % (namespace.number)
    print(zapros('status'))

elif namespace.number and namespace.start_date:
    sql = "SELECT start_date FROM zadarma_numbers WHERE number = %s;" % (namespace.number)
    print(zapros('start_date'))

elif namespace.number and namespace.stop_date:
    sql = "SELECT stop_date FROM zadarma_numbers WHERE number = %s;" % (namespace.number)
    print(zapros('stop_date'))

elif namespace.number and namespace.autorenew:
    sql = "SELECT autorenew FROM zadarma_numbers WHERE number = %s;" % (namespace.number)
    print(zapros('autorenew'))

elif namespace.number and namespace.description:
    sql = "SELECT description FROM zadarma_numbers WHERE number = %s;" % (namespace.number)
    print(zapros('description'))

elif namespace.number and namespace.sip:
    sql = "SELECT sip FROM zadarma_numbers WHERE number = %s;" % (namespace.number)
    if namespace.cut == 0:
        print(zapros('sip'))
    if namespace.cut == 1:
        try:
            print(zapros('sip').split('@')[0])
        except IndexError:
            print(zapros('sip'))
    if namespace.cut == 2:
        try:
            print(zapros('sip').split('@')[1])
        except  IndexError:
            print(zapros('sip'))

elif namespace.number and namespace.monthly_fee:
    sql = "SELECT monthly_fee FROM zadarma_numbers WHERE number = %s;" % (namespace.number)
    print(zapros('monthly_fee'))

else:
    if namespace.number:
        # sql = "SELECT * FROM zadarma_numbers WHERE number = %s;" % (namespace.number)
        # print(zapros(namespace.number))
        print(namespace.number, 'there are not enough arguments or incorrect combination of arguments')
        sys.exit(1)

    elif namespace.balance:
        if namespace.force_API:
            balance = balance_info['balance']
            print(balance)
        else:
            print(sql_result('SELECT balance FROM zadarma_balance;')[0][0])

    elif namespace.monthly_fee:
        if namespace.force_API:
            for result in numbers_result['info']:
                monthly_fee_all = monthly_fee_all + result['monthly_fee']
            print(monthly_fee_all)
        else:
            print(sql_result('SELECT monthly_fee FROM zadarma_balance;')[0][0])

    elif namespace.allnumbers:
        if namespace.force_API:
            json_data = []
            for result in numbers_result['info']:
                print(result['number'])
                json_data.append(dict(zip(['{#NUMBER}'], [result['number']])))
            json_data = ({"data": json_data})
            print('jkgkgliuui',json.dumps(json_data))

        else:
            data = sql_result('SELECT number FROM zadarma_numbers  WHERE stop_date > date')
            print(str_for_json(data))

    else:
        if namespace.force_API:
            json_data = []
            for result in numbers_result['info']:
                json_data.append(dict(zip(['{#NUMBER}'], [result['number']])))
            json_data = ({"data": json_data})
            print(json.dumps(json_data))

        else:
            data = sql_result('SELECT number FROM zadarma_numbers  WHERE stop_date > date')
            print(str_for_json(data))
if not namespace.force_API:
    db.close()

