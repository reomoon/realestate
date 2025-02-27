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

# 데이터를 가져오는 함수
def fetch_data(urls):
    all_data = []  
    
    for url in urls:
        response = requests.get(url, cookies=cookie, headers=header)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                if 'articleList' in data:
                    for article in data['articleList']:  
                        all_data.append({
                            "articleNo": article.get('articleNo'),  # 링크용
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

# API URL 목록
urls = [gaeyang, bongdam1, bongdam2]

# 데이터 가져오기
all_articles = fetch_data(urls)

# DataFrame 변환
df = pd.DataFrame(all_articles)

# 가격을 정렬할 수 있도록 변환
df[['billions', 'remainder']] = df['dealOrWarrantPrc'].apply(lambda x: convert_to_number(x)).apply(pd.Series)

# 'articleName' 그룹 내에서 가격을 낮은 순으로 정렬
df = df.sort_values(by=['articleName', 'billions', 'remainder'])

# 네이버 부동산 링크 추가
df['link'] = df['articleNo'].apply(lambda x: f'<a href="https://m.land.naver.com/article/info/{x}" target="_blank">바로가기</a>' if pd.notna(x) else '')

# 불필요한 컬럼 제거
df.drop(columns=['billions', 'remainder'], inplace=True)

# HTML 변환 (링크 포함)
html_content = df.to_html(index=False, escape=False)

# HTML 파일 생성
html_with_styles = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real Estate Articles</title>
    <link rel="stylesheet" type="text/css" href="styles.css">
</head>
<body>
    <h2>Real Estate</h2>
    {html_content}
</body>
</html>
"""

# 저장
with open("articles_sorted.html", "w", encoding="utf-8") as f:
    f.write(html_with_styles)

print("HTML 파일 저장 완료!")
