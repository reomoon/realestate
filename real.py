import requests
import json
import pandas as pd
import os
from collections import Counter
from common import *  # 쿠키 및 헤더 정보 포함

# 이전 데이터 저장 파일
previous_file = "previous.json"
template_file = "template.html"  # HTML 템플릿 파일
output_file = "articles_sorted.html"  # 최종 저장될 HTML 파일

# 가격을 억 단위로 변환하는 함수
def convert_to_number(price_str):
    price_str = price_str.replace('억', '').replace('원', '').replace(',', '')

    try:
        parts = price_str.split(' ')
        if len(parts) == 2:
            billions = int(parts[0])
            remainder = int(parts[1])
        else:
            billions = int(parts[0])
            remainder = 0

        return billions, remainder
    except ValueError:
        return 0, 0

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
                            "articleNo": article.get('articleNo'),
                            "articleName": article.get('articleName'),
                            "dealOrWarrantPrc": article.get('dealOrWarrantPrc'),
                            "buildingName": article.get('buildingName'),
                            "area2": article.get('area2'),
                            "floorInfo": article.get('floorInfo'),
                            "direction": article.get('direction'),
                            "articleConfirmYmd": article.get('articleConfirmYmd'),
                            "articleFeatureDesc": article.get('articleFeatureDesc'),
                            "premiumPrc": article.get('premiumPrc'),
                        })
            except json.JSONDecodeError:
                print(f"JSON 디코딩 실패, HTML 내용: {response.text[:500]}")
        else:
            print(f"요청 실패: {response.status_code}, URL: {url}")

    return all_data

# API URL 목록
urls = [gaeyang, bongdam1, bongdam2, homaesil, peongnae, maseok, godeok, tangjung, janghyun, mokkam, youngtong1, ssanyoung, bukbyun, peongtack1, peongtack2, peongtack3]

# 1️⃣ 이전 데이터 불러오기
if os.path.exists(previous_file):
    with open(previous_file, "r", encoding="utf-8") as f:
        previous_data = json.load(f)
else:
    previous_data = []

# 2️⃣ 데이터 가져오기
all_articles = fetch_data(urls)

# 3️⃣ 새로운 데이터 여부 확인
previous_article_numbers = {article["articleNo"] for article in previous_data}
for article in all_articles:
    article["is_new"] = article["articleNo"] not in previous_article_numbers

# 매물 개수 변화 비교를 위해 `articleName` 기준 그룹화
previous_counts = Counter(article["articleName"] for article in previous_data)
current_counts = Counter(article["articleName"] for article in all_articles)

# 📌 디버깅용 출력 (확인 후 삭제 가능)
# print("🔴 이전 매물 개수:", previous_counts)  
# print("🟢 현재 매물 개수:", current_counts)

# DataFrame 변환
df = pd.DataFrame(all_articles)

# 가격 변환 및 정렬
df[['billions', 'remainder']] = df['dealOrWarrantPrc'].apply(lambda x: convert_to_number(x)).apply(pd.Series)
df = df.sort_values(by=['articleName', 'billions', 'remainder'])

# 네이버 부동산 링크 추가
df['link'] = df['articleNo'].apply(lambda x: f'<a href="https://m.land.naver.com/article/info/{x}" target="_blank">바로가기</a>' if pd.notna(x) else '')

# 불필요한 컬럼 제거
df.drop(columns=['articleNo', 'billions', 'remainder'], inplace=True)

# 각 articleName별 매물 수 계산
article_counts = df['articleName'].value_counts().to_dict()

# HTML 테이블 생성 (articleName 그룹화)
html_content = ""
prev_article_name = None

for _, row in df.iterrows():
    new_tag = "<span class='new-tag'>NEW</span>" if row["is_new"] else ""

    # 한 칸에 두 줄로 표시
    main_info = f"""
        {row['dealOrWarrantPrc']} | {row['buildingName']} {row['area2']}㎡ {row['floorInfo']} {row['direction']} {row['articleConfirmYmd']} {new_tag}
        <br>
        {'P ' + str(row['premiumPrc']) + '만원' if pd.notna(row['premiumPrc']) else ''} {row['articleFeatureDesc']} | {row['link']}
    """
    
    # 같은 articleName 그룹의 첫 번째 항목에만 헤더 추가
    if row["articleName"] != prev_article_name:
        today_count = current_counts.get(row["articleName"], 0)
        yesterday_count = previous_counts.get(row["articleName"], 0)
        difference = today_count - yesterday_count

        # 증가/감소 여부에 따라 표시
        if difference > 0:
            change_text = f'<span class="increase">🔺{difference}</span>'
        elif difference < 0:
            change_text = f'<span class="decrease">🔻{abs(difference)}</span>'
        else:
            change_text = '<span class="no-change">-</span>'

        html_content += f"""
        <tr class="group-header">
            <td colspan="2"><strong>{row['articleName']} ({today_count}개) {change_text}</td>
        </tr>
        """
        prev_article_name = row["articleName"]

     # 한 칸에 모든 내용을 포함
    html_content += f"""
    <tr>
        <td>{main_info}</td>
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

# HTML 템플릿 불러오기 및 데이터 삽입
with open(template_file, "r", encoding="utf-8") as f:
    template_html = f.read()

final_html = template_html.replace("{dropdown_options}", dropdown_options).replace("{html_table}", html_table)

# df의 길이를 출력하여 데이터 개수 확인
article_counts = df['articleName'].value_counts()
print(article_counts)

# 저장
with open(output_file, "w", encoding="utf-8") as f:
    f.write(final_html)

print("articles_sorted.html 파일이 업데이트되었습니다.")

# 새로운 데이터를 JSON으로 저장 (다음 실행 시 비교)
with open(previous_file, "w", encoding="utf-8") as f:
    json.dump(all_articles, f, ensure_ascii=False, indent=4)

print("HTML 파일 저장 완료!")
