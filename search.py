import requests
import json
import pandas as pd
from common import cookie, header

# 가격을 억 단위로 변환하여 정렬할 수 있도록 하는 함수
def convert_to_number(price_str):
    # '억' 단위와 ',' 등을 처리하여 숫자로 변환
    price_str = price_str.replace('억', '').replace('원', '').replace(',', '')
    
    try:
        # '억' 단위를 기준으로 분리하여 첫 번째는 억, 두 번째는 나머지 부분으로 나누어 비교
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

# API 요청
response = requests.get(
    'https://new.land.naver.com/api/articles/complex/125101?realEstateType=APT%3AABYG%3AJGC%3APRE&tradeType=A1&tag=%3A%3A%3A%3A%3A%3A%3A%3A%3A&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000&oldBuildYears&recentlyBuildYears&minHouseHoldCount&maxHouseHoldCount&showArticle=false&sameAddressGroup=false&minMaintenanceCost&maxMaintenanceCost&page=1&complexNo=125101&buildingNos=&areaNos=1&type=list&order=rank',
    cookies = cookie,  # 요청에 필요한 쿠키와 헤더 설정(common 참조)
    headers = header,
)

# 응답 코드가 200일 경우
if response.status_code == 200:
    try:
        data = response.json()
        
        # 응답 구조를 출력하여 실제 데이터를 확인
        # print(json.dumps(data, indent=4))  # JSON 전체를 출력하여 어떤 구조인지 확인
        
        # 예시: 'articleList'라는 배열 안에 article 정보들이 포함된 경우
        if 'articleList' in data:
            processed_data = []
            for article in data['articleList']:  # articleList 배열을 순회
                processed_data.append({
                    "articleNo": article.get('articleNo'),
                    "articleName": article.get('articleName'),
                    "dealOrWarrantPrc": article.get('dealOrWarrantPrc'),
                    "buildingName": article.get('buildingName'),
                    "floorInfo": article.get('floorInfo'),
                    "direction": article.get('direction'),
                    "articleConfirmYmd": article.get('articleConfirmYmd'),
                    "articleFeatureDesc": article.get('articleFeatureDesc'),
                })
            
            # DataFrame으로 변환 후, 가격 순으로 정렬
            df = pd.DataFrame(processed_data)
            # 가격을 억 단위로 변환하여 정렬 기준을 만듬
            df[['billions', 'remainder']] = df['dealOrWarrantPrc'].apply(lambda x: convert_to_number(x)).apply(pd.Series)
            df = df.sort_values(by=['billions', 'remainder'])  # 억 단위, 나머지 단위로 정렬
            
            # 'billions'와 'remainder' 컬럼 제거
            df.drop(columns=['billions', 'remainder'], inplace=True)
            
            # HTML로 저장
            df.to_html('articles_sorted_by_price.html', index=False)
            print("HTML 파일로 저장되었습니다.")
        else:
            print("응답 데이터에 'articleList' 키가 없습니다.")
        
    except json.JSONDecodeError:
        print(f"JSON 디코딩 실패, HTML 내용: {response.text[:500]}")  # HTML 내용 일부 출력
else:
    print(f"요청 실패: {response.status_code}")
