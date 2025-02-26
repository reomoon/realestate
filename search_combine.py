import requests
import json
import pandas as pd
from common import *  # 쿠키 및 헤더 정보 포함

# 가격을 억 단위로 변환하여 정렬할 수 있도록 하는 함수
def convert_to_number(price_str):
    price_str = price_str.replace('억', '').replace('원', '').replace(',', '')
    
    try:
        parts = price_str.split(' ')
        if len(parts) == 2:
            billions = int(parts[0])  # 억 단위
            remainder = int(parts[1])  # 나머지 (천, 백, 십 단위)
        else:
            billions = int(parts[0])  # 억 단위만 있을 경우
            remainder = 0  # 나머지는 0

        return billions, remainder
    except ValueError:
        return 0, 0  # 값 변환이 안되면 0으로 처리

# 두 개의 URL에서 데이터를 가져오는 함수
def fetch_data(urls):
    all_data = []  # 두 API의 데이터를 결합할 리스트
    
    for url in urls:
        response = requests.get(url, cookies=cookie, headers=header)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                if 'articleList' in data:
                    for article in data['articleList']:  # articleList 배열을 순회
                        all_data.append({
                            #"articleNo": article.get('articleNo'),
                            "articleName": article.get('articleName'),
                            "dealOrWarrantPrc": article.get('dealOrWarrantPrc'),
                            "buildingName": article.get('buildingName'),
                            "floorInfo": article.get('floorInfo'),
                            "direction": article.get('direction'),
                            "articleConfirmYmd": article.get('articleConfirmYmd'),
                            "articleFeatureDesc": article.get('articleFeatureDesc'),
                        })
                else:
                    print(f"응답 데이터에 'articleList' 키가 없습니다. URL: {url}")
            except json.JSONDecodeError:
                print(f"JSON 디코딩 실패, HTML 내용: {response.text[:500]}")
        else:
            print(f"요청 실패: {response.status_code}, URL: {url}")
    
    return all_data

# 두 개의 API URL을 리스트로 정의
urls = [gaeyang, bongdam1, bongdam2]

# 두 개의 URL에서 데이터를 가져옴
all_articles = fetch_data(urls)

# 데이터를 DataFrame으로 변환
df = pd.DataFrame(all_articles)

# 가격을 억 단위로 변환하여 정렬 기준을 만듬
df[['billions', 'remainder']] = df['dealOrWarrantPrc'].apply(lambda x: convert_to_number(x)).apply(pd.Series)

# 'articleName' 기준으로 그룹화한 후, 그 그룹 내에서 가격을 낮은 순으로 정렬
df = df.sort_values(by=['articleName', 'billions', 'remainder'])

# 'billions'와 'remainder' 컬럼 제거
df.drop(columns=['billions', 'remainder'], inplace=True)

# HTML로 저장 (CSS 파일을 외부에서 참조)
html_content = df.to_html(index=False, escape=False)

# 외부 CSS 파일을 링크하는 HTML 구조
html_with_styles = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real Estate Articles</title>
    <link rel="stylesheet" type="text/css" href="styles.css"> <!-- CSS 파일 링크 -->
</head>
<body>
    <h2>Real Estate</h2>
    {html_content}
</body>
</html>
"""

# HTML 파일로 저장
with open("articles_sorted_by_name_and_price_mobile.html", "w", encoding="utf-8") as f:
    f.write(html_with_styles)

print("모바일 최적화된 HTML 파일로 저장되었습니다.")
