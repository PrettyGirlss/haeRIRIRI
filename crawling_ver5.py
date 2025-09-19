from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import pandas as pd

# 함수 정의
# 화면 스크롤 하는 함수
def scroll_to(height):
    current_scroll_position = driver.execute_script("return window.pageYOffset;")       # 현재 위치 가져오기
    new_scroll_position = current_scroll_position + height          # 지금 위치에서 height 추가한 새로운 스크롤 위치
    driver.execute_script(f'window.scrollTo(0,{new_scroll_position});')     # 새로운 스크롤 위치로 이동
    time.sleep(1)

# 지역 버튼 클릭하는 함수
def click_region(location_number):
    # 강원 (32) / 충북 (33) / 울산 (7) / 대전(3) / 각자 지역 참고하세요
    button_path = driver.find_element(By.XPATH, f'//*[@id="{location_number}"]/button')
    button_path.click()
    time.sleep(2)

# 리뷰 카드 내부 본문 '더보기'가 있으면 펼치기
def expand_review_if_truncated(review_el):
    try:
        # '더보기' 텍스트 기반 후보(버튼/링크)
        more_btns = review_el.find_elements(
            By.XPATH,
            ".//button[contains(., '더보기')] | .//a[contains(., '더보기')]"
        )
        # 클래스 기반 공통 후보(사이트에 따라 다를 수 있음)
        more_btns += review_el.find_elements(By.CSS_SELECTOR, ".btn_more, .more, .expand, .read_more")

        for btn in more_btns:
            try:
                if not btn.is_displayed():
                    continue
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                driver.execute_script("arguments[0].click();", btn)  # 안전 클릭
                # 펼쳐질 시간 잠깐 대기(aria-expanded가 true가 되거나 텍스트가 바뀌면 OK)
                try:
                    wait.until(
                        lambda d: (btn.get_attribute("aria-expanded") == "true") or ("더보기" not in btn.text)
                    )
                except TimeoutException:
                    pass
                break
            except Exception:
                continue
    except Exception:
        pass



tour = []

service=webdriver.chrome.service.Service('chromedriver.exe')
driver=webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)


driver.get('https://korean.visitkorea.or.kr/list/travelinfo.do?service=ms#ms^0^32^All^e6875575-2cc2-43ba-9651-28d31a7b3e23,651c5b95-a5b3-11e8-8165-020027310001,c24d515f-3202-45e5-834e-1a091901aeff,d3fd4d9f-fbd4-430f-b5d5-291b4d9920be,3f36ca4b-6f45-45cb-9042-265c96a4868c,23bc02b8-da01-41bf-8118-af882436cd3c,2d4f4e06-2d37-4e54-ad5c-172add6e6680,9668f0f1-8afe-4526-8007-503bd02fd6d8,0f29b431-75ac-4ab4-a892-b247d516b31d,640d3489-8fc3-11e8-8165-020027310001,1601b0a3-144e-40b7-95b4-b946e537a25b,1c981ad4-7834-11e8-82c8-020027310001,266bf7a0-cbab-4bb4-b800-d7edd5642180,cdd12d65-1f38-4829-a1be-bf235a0fb3f2^1^^1^#%EA%B0%95%EC%9B%90')
time.sleep(5)

# 지역 번호 바꾸세요!!!!
region_num = 3    # 강원
click_region(region_num)

# 전체 결과 수 확인하고 총 페이지 수 확인
total_results = int(driver.find_element(By.XPATH,'//*[@id="totalCnt"]').text.replace(",",""))
total_pages = total_results//10 + (1 if total_results%10!=0 else 0 )     # 한 페이지당 10개씩 나와요 그래서 총 페이지 수 total_results // 10 + 1 해줘야함

contents_path = '#contents > div:nth-child(2) > div:nth-child(1) > ul > li'

# 페이지마다 결과물 10개씩 나옴
# 그거 다 받아서 for 문으로 돌리면서 하나씩 들어가서 정보 crawling
for _ in range(total_pages):
    # 해당 페이지에 보여지는 결과물 10개 contents에 저장
    # 결과물 나올 때까지 기다리기
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, contents_path)))
    location_counts = len(driver.find_elements(By.CSS_SELECTOR, contents_path))

    # 결과물 1개씩 클릭해서 정보 크롤링
    for idx in range(location_counts):
        # 정보 저장할 딕셔너리 초기화
        location_data = {}
        # 장소 이름 클릭할 수 있도록 button 찾아주고 클릭
        locations = driver.find_elements(By.CSS_SELECTOR, contents_path)
        # 목록이 리로드되었더라도 전체가 다 나올 때까지 대기
        try:
            wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, contents_path)) == location_counts)
        except TimeoutException:
            print('로드가 안되는데요...긁적')
            break  # 더 이상 아이템이 안 보이면 이 페이지 종료

        link = locations[idx].find_element(By.TAG_NAME, 'a')
        link.click()
        time.sleep(2)

        # 페이지로 이동한 후 데이터 얻기
        # 장소 이름 저장
        title = driver.find_element(By.ID, 'topTitle')
        location_data['place'] = title.text

        # 상세 정보 보이는 쪽으로 스크롤
        scroll_to(900)
        time.sleep(1)

        # 상세정보 찾아서 text 저장
        info = driver.find_element(By.CSS_SELECTOR, 'div.inr_wrap > div.inr > p')
        location_data['info'] = info.text
        time.sleep(1)

        # 상세 항목 저장
        # 아래쪽으로 이동
        scroll_to(600)
        # 더보기 있으면 클릭
        try:
            driver.find_element(By.XPATH, '//*[@id="detailinfoview"]/div/div[2]/button').click()
        except:
            pass
        
        # 장소 상세 정보 다운로드
        additional_contents = driver.find_elements(By.CSS_SELECTOR, 'div.wrap_contView div.inr li')
        for additional_content in additional_contents:
            key = additional_content.find_element(By.CSS_SELECTOR, 'strong').text
            value = additional_content.find_element(By.CSS_SELECTOR, 'span').text
            location_data[key] = value
        
        # 리뷰 데이터 크롤링
        review_list = []    # 리뷰 담을 변수 초기화
        scroll_to(600)
        wait.until(EC.presence_of_all_elements_located((By.ID, 'commentCount')))
        try:
            review_count = int(driver.find_element(By.ID, 'commentCount').text)

            # 리뷰 개수 세기
            count = min( 10, review_count)
            # 리뷰 개수 0개이면 뒤로가기 
            if count == 0 :
                location_data['review'] = ''
                driver.back()
                continue
            # 리뷰 2개 이하면 리뷰 추출 (더보기 안 눌러도 다 보여서 굳이 더보기 누를 필요 없음)
            elif count <=2:
                review_contents = driver.find_elements(By.CSS_SELECTOR, '#commentArea > li')
            # 리뷰 3개이상 7개 이하면 더보기 한 번 눌러야함
            elif count <=7:
                scroll_to(300)
                driver.find_element(By.XPATH, '//*[@id="commentMore"]/button').click() # 더보기 버튼 누르기     # 리뷰 더보기 클릭
                time.sleep(2)
                review_contents = driver.find_elements(By.CSS_SELECTOR, '#commentArea > li')
            # 리뷰 8개 이상이면 더보기 2번 눌러야함
            else:
                scroll_to(300)
                driver.find_element(By.XPATH, '//*[@id="commentMore"]/button').click()      # 리뷰 더보기 클릭
                time.sleep(1)
                scroll_to(700)
                try:
                    driver.find_element(By.XPATH, '//*[@id="commentMore"]/button').click()      # 리뷰 더보기 클릭
                except:
                    pass
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#commentArea > li')))
                review_contents = driver.find_elements(By.CSS_SELECTOR, '#commentArea > li')
            
            scroll_to(200)

            # 리뷰 컨텐츠들을 하나씩 꺼내어서 review_text 추출
            for review_content in review_contents:
                scroll_to(187)
                expand_review_if_truncated(review_content)
                review_list.append(review_content.find_elements(By.CLASS_NAME, 'review_text')[-1].text)
            reviews = " ".join(review_list)

            # 리뷰 정보 딕셔너리에 저장
            location_data['review'] = reviews

        except: # 오류 발생시 오류라고 저장하고 넘어가게 해줌
            location_data['review']= '오류'

        finally:
            # 투어 리스트에 location_data 전체 저장
            tour.append(location_data)
            print(location_data)

            # 정보 다 크롤링한 후 뒤로 가기
            driver.back()
            scroll_to(120)
            time.sleep(3)

    # 아래로 내려가기
    scroll_to(200)
    time.sleep(1)

    # 다음 페이지 버튼 누르기
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.page_box > a')))
    page_button_path = driver.find_elements(By.CSS_SELECTOR, '.page_box > a')
    if len(page_button_path) >= 2:
        try:
            # '다음' 또는 '>'가 있으면 우선 클릭, 없으면 기존 방식(-2)로
            next_btn = None
            for a in reversed(page_button_path):
                t = a.text.strip()
                if t in ('다음', '>', '›', 'Next'):
                    next_btn = a
                    break
            if next_btn is None:
                next_btn = page_button_path[-2]
            next_btn.click()
            # wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, contents_path)))
        except Exception:
            break
    else:
        break
    time.sleep(3)

pd.DataFrame(tour).to_csv(f'{region_num}번 지역 데이터')
time.sleep(1)
driver.close()