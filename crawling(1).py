from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import numpy as np
import pandas as pd

# 함수 정의
# 화면 스크롤 하는 함수
def scroll_to(height):
    current_scroll_position = driver.execute_script("return window.pageYOffset;")
    new_scroll_position = current_scroll_position + height
    driver.execute_script(f'window.scrollTo(0,{new_scroll_position});')
    time.sleep(1)

# 지역 버튼 클릭하는 함수
def click_region(location_number):
    button_path = driver.find_element(By.XPATH, f'//*[@id="{location_number}"]/button')
    button_path.click()
    time.sleep(2)


tour = []

service = webdriver.chrome.service.Service('chromedriver.exe')
driver = webdriver.Chrome(service=service)

driver.get('https://korean.visitkorea.or.kr/list/travelinfo.do?service=ms#ms^0^32^All^e6875575-2cc2-43ba-9651-28d31a7b3e23,651c5b95-a5b3-11e8-8165-020027310001,c24d515f-3202-45e5-834e-1a091901aeff,d3fd4d9f-fbd4-430f-b5d5-291b4d9920be,3f36ca4b-6f45-45cb-9042-265c96a4868c,23bc02b8-da01-41bf-8118-af882436cd3c,2d4f4e06-2d37-4e54-ad5c-172add6e6680,9668f0f1-8afe-4526-8007-503bd02fd6d8,0f29b431-75ac-4ab4-a892-b247d516b31d,640d3489-8fc3-11e8-8165-020027310001,1601b0a3-144e-40b7-95b4-b946e537a25b,1c981ad4-7834-11e8-82c8-020027310001,266bf7a0-cbab-4bb4-b800-d7edd5642180,cdd12d65-1f38-4829-a1be-bf235a0fb3f2^1^^1^#%EA%B0%95%EC%9B%90')
time.sleep(5)

# 전남 클릭 ( 대구 4)
click_region(4)

# 전체 결과 수 확인
total_results = int(driver.find_element(By.XPATH,'//*[@id="totalCnt"]').text.replace(",",""))
total_pages = total_results // 10 + 1   # 페이지 수 (10개씩 보여서 +1)

# 페이지마다 반복
for _ in range(total_pages):
    contents = driver.find_elements(By.CSS_SELECTOR, 'div.box_leftType1 > ul > li')

    for idx in range(len(contents)):
        # stale element 방지 위해 항상 다시 찾음
        contents = driver.find_elements(By.CSS_SELECTOR, 'div.box_leftType1 > ul > li')
        link = contents[idx].find_element(By.TAG_NAME, 'a')
        link.click()
        time.sleep(2)

        location_data = {}
        # 장소 이름
        title = driver.find_element(By.ID, 'topTitle')
        location_data['place'] = title.text

        # 상세 정보 스크롤
        scroll_to(900)
        time.sleep(1)

        # 상세 설명
        try:
            info = driver.find_element(By.CSS_SELECTOR, 'div.inr_wrap > div.inr > p')
            location_data['info'] = info.text
        except:
            location_data['info'] = ""
        time.sleep(1)

        # 상세 항목
        scroll_to(500)
        try:
            driver.find_element(By.XPATH, '//*[@id="detailinfoview"]/div/div[2]/button').click()
        except:
            pass

        additional_contents = driver.find_elements(By.CSS_SELECTOR, 'div.wrap_contView div.inr li')
        for additional_content in additional_contents:
            try:
                key = additional_content.find_element(By.CSS_SELECTOR, 'strong').text
                value = additional_content.find_element(By.CSS_SELECTOR, 'span').text
                location_data[key] = value
            except:
                continue

        # 리뷰 데이터
        review_list = []
        # 리뷰 개수 가져오기, 빈 문자열이면 0 처리
        comment_count_text = driver.find_element(By.ID, 'commentCount').text
        # review_count = int(driver.find_element(By.ID, 'commentCount').text)
        review_count = int(comment_count_text.replace(",", "")) if comment_count_text.strip() != "" else 0

        count = min(10, review_count)
        if count == 0:
            driver.back()
            scroll_to(110)
            continue
        elif count <= 2:
            review_contents = driver.find_elements(By.CSS_SELECTOR, '#commentArea > li')
        elif count <= 7:
            scroll_to(200)
            driver.find_element(By.XPATH, '//*[@id="commentMore"]/button').click()
            time.sleep(2)
            review_contents = driver.find_elements(By.CSS_SELECTOR, '#commentArea > li')
        else:
            scroll_to(200)
            driver.find_element(By.XPATH, '//*[@id="commentMore"]/button').click()
            time.sleep(1)
            scroll_to(550)
            driver.find_element(By.XPATH, '//*[@id="commentMore"]/button').click()
            review_contents = driver.find_elements(By.CSS_SELECTOR, '.commentArea li')

        for review_content in review_contents:
            try:
                review_list.append(review_content.find_element(By.CLASS_NAME, 'review_text').text)
            except:
                continue
        reviews = " ".join(review_list)
        location_data['review'] = reviews

        tour.append(location_data)
        print(location_data)

        # 뒤로가기 후 스크롤
        driver.back()
        scroll_to(110)
        time.sleep(2)

    # 다음 페이지 이동
    scroll_to(200)
    time.sleep(1)
    page_button_path = driver.find_elements(By.CSS_SELECTOR, '.page_box > a')
    page_button_path[-2].click()
    time.sleep(3)

time.sleep(1)
driver.close()

df = pd.DataFrame(tour)
df.to_csv("tour_data.csv", index=False, encoding="utf-8-sig")