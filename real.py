import requests
import json
import pandas as pd
from common import *  # 쿠키 및 헤더 정보 포함

# 가격을 억 단위로 변환하는 함수
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

                # 응답 구조를 출력하여 실제 데이터를 확인
                # print(json.dumps(data, indent=4))  # JSON 전체를 출력하여 어떤 구조인지 확인(Debug)

                if 'articleList' in data:
                    for article in data['articleList']:  
                        all_data.append({
                            "articleNo": article.get('articleNo'),  # 링크용
                            "articleName": article.get('articleName'),
                            "dealOrWarrantPrc": article.get('dealOrWarrantPrc'),
                            "buildingName": article.get('buildingName'),
                            "area2": article.get('area2'),
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
urls = [gaeyang, bongdam1, bongdam2, homaesil, peongnae, maseok, godeok, tangjung, janghyun, mokkam, sanggal, youngtong1, youngtong2, youngtong3]
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
df.drop(columns=['articleNo', 'billions', 'remainder'], inplace=True)

# HTML 테이블 직접 생성 (articleName 그룹화)
html_content = ""
prev_article_name = None

for _, row in df.iterrows():
    main_info = f"{row['dealOrWarrantPrc']} | {row['buildingName']} {row['area2']}㎡ {row['floorInfo']}  {row['direction']} {row['articleConfirmYmd']}"
    
    # articleName이 바뀌었을 때, 새로운 그룹 헤더 추가
    if row["articleName"] != prev_article_name:
        html_content += f"""
        <tr class="group-header">
            <td colspan="2"><strong>{row['articleName']}</strong></td>
        </tr>
        """
        prev_article_name = row["articleName"]

    # 주요 정보와 상세 정보 추가
    html_content += f"""
    <tr>
        <td>{main_info}</td>
    </tr>
    <tr class="details-row">
        <td>{row['articleFeatureDesc']} | {row['link']}</td>
    </tr>
    """

html_table = f"""
<table id="articlesTable">
    <tbody>
        {html_content}
    </tbody>
</table>
"""

# articleName 목록을 추출하여 드롭다운 옵션 생성
article_names = df['articleName'].unique()
dropdown_options = ''.join([f'<option value="{name}">{name}</option>' for name in article_names])

# HTML + 스타일 + JS 추가
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
<div class="filter-container">
    <h2>Real Estate</h2>
    <div class="dropdown-filter">
        <!-- 검색 입력창을 감싸는 wrapper -->
        <div class="search-wrapper">
            <!-- 검색 입력창 -->
            <input type="text" id="searchInput" placeholder="검색어 입력..." onkeyup="filterTable()">
            <!-- X 버튼 -->
            <button type="button" id="clearBtn" onclick="clearSearch()" style="display: none;">x</button>
        </div>
        <!-- 드롭다운 필터 -->
        <select id="articleNameFilter" onchange="filterByArticleName()">
            <option value="">전체</option>
            {dropdown_options}
        </select>
    </div>
</div>

    <!-- 테이블 -->
    {html_table}

    <!-- JavaScript 파일 불러오기 -->
    <script src="./html_script.js"></script>

</body>
</html>
"""

# 저장
with open("articles_sorted.html", "w", encoding="utf-8") as f:
    f.write(html_with_styles)

print("HTML 파일 저장 완료!")