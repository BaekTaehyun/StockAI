from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

class MKScraper:
    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--window-size=1920,1080')
        # User Agent 설정 (차단 방지)
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = None

    def _init_driver(self):
        if not self.driver:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)

    def get_ai_answer(self, query):
        """
        매경 AI 검색에서 쿼리에 대한 답변을 스크래핑합니다.
        """
        try:
            self._init_driver()
            url = "https://www.mk.co.kr/aisearch"
            print(f"[Scraper] Navigating to {url}...")
            self.driver.get(url)
            
            # 검색창 찾기 (ID나 클래스 확인 필요, 여기서는 일반적인 input 태그 추정)
            # 실제 사이트 구조에 맞춰 수정 필요
            # 이전 브라우저 탐색 결과: input 태그가 있음.
            wait = WebDriverWait(self.driver, 10)
            
            # 검색창 찾기
            print(f"[Scraper] Searching for '{query}'...")
            search_input = wait.until(EC.presence_of_element_located((By.ID, "ai_main_search_text")))
            search_input.clear()
            search_input.send_keys(query)
            
            # 검색 버튼 클릭
            search_btn = self.driver.find_element(By.ID, "ai_search_btn")
            search_btn.click()
                
            # 답변 컨테이너 찾기 (ID: inner_answer_cont)
            print("[Scraper] Waiting for AI answer container (#inner_answer_cont)...")
            try:
                # 답변 컨테이너가 나타날 때까지 대기
                answer_container = wait.until(EC.visibility_of_element_located((By.ID, "inner_answer_cont")))
                
                # 텍스트가 채워질 때까지 대기 (최대 20초)
                def has_text(driver):
                    element = driver.find_element(By.ID, "inner_answer_cont")
                    return len(element.text.strip()) > 0
                
                wait.until(has_text)

                # 텍스트 스트리밍 완료 대기 (길이가 더 이상 변하지 않을 때까지)
                print("[Scraper] Waiting for text streaming to complete...")
                previous_text = ""
                stable_count = 0
                max_retries = 40 # 20초 (0.5초 * 40)
                
                for _ in range(max_retries):
                    current_element = self.driver.find_element(By.ID, "inner_answer_cont")
                    current_text = current_element.text.strip()
                    
                    if current_text == previous_text and len(current_text) > 0:
                        stable_count += 1
                    else:
                        stable_count = 0
                    
                    if stable_count >= 6: # 3초 동안 변화 없으면 완료로 간주
                        break
                        
                    previous_text = current_text
                    time.sleep(0.5)
                
                # 최종 텍스트 추출
                final_element = self.driver.find_element(By.ID, "inner_answer_cont")
                result_text = final_element.text.strip()
                
                print(f"[Scraper] Extracted text length: {len(result_text)}")
                
                if result_text:
                    return result_text
                else:
                    print("[Scraper] Found container but text is empty.")
                    return None
                    
            except Exception as e:
                print(f"[Scraper] Error finding answer container: {e}")
                return None

        except Exception as e:
            print(f"[Scraper Error] {e}")
            return None

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

if __name__ == "__main__":
    import sys
    # 테스트 코드
    scraper = MKScraper(headless=True)
    result = scraper.get_ai_answer("삼성전자")
    print("\n[AI Answer Result]\n")
    
    if result:
        # 콘솔 인코딩 문제 방지를 위해 safe print
        try:
            print(result)
        except:
            sys.stdout.buffer.write(result.encode('utf-8'))
            print()
            
        # 결과 파일 저장
        with open("scraped_result.txt", "w", encoding="utf-8") as f:
            f.write(result)
    else:
        print("No result found")
        
    scraper.close()
