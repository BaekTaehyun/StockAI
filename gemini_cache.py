import os
import json
import datetime

class GeminiCache:
    """Gemini 서비스의 캐싱 로직을 담당하는 클래스"""

    def __init__(self):
        # 캐시 디렉토리 생성
        self.cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        # 캐시 만료 시간 설정 (초 단위)
        # 메모리 캐시: 10분 (600초) - 빠른 응답용, 자주 갱신
        # 파일 캐시: 60분 (3600초) - API 비용 절감용, 길게 유지
        self.CACHE_TTL_MEMORY = 600
        self.CACHE_TTL_FILE = 3600
            
        # 메모리 캐시 초기화 (파일 I/O 감소 및 실패 대비)
        # 구조: { 'key': { 'data': ..., 'timestamp': ... } }
        self._memory_cache = {}

    def get_cache_path(self, code, analysis_type):
        """캐시 파일 경로 생성 (종목코드_타입_날짜.json)"""
        # 종목 코드 정규화 (A 접두사 제거)
        normalized_code = code.lstrip('A') if code and code.startswith('A') else code
        today = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"{normalized_code}_{analysis_type}_{today}.json"
        path = os.path.join(self.cache_dir, filename)
        return path

    def load(self, code, analysis_type, force_refresh=False):
        """
        캐시에서 데이터 로드 (메모리 -> 파일 순서)
        - force_refresh=True: 캐시 무시하고 (None, dict) 반환
        - 파일 수정 시간이 60분(3600초) 이상 지났으면 만료 처리
        Returns:
            (data, cache_info) - data는 캐싱된 데이터 또는 None, cache_info는 캐시 상태 정보
        """
        cache_info = {'cached': False, 'reason': '', 'age_seconds': 0}
        
        if force_refresh:
            cache_info['reason'] = 'force_refresh'
            return None, cache_info

        current_time = datetime.datetime.now().timestamp()
        cache_key = f"{code}_{analysis_type}"

        # 1. 메모리 캐시 확인
        if cache_key in self._memory_cache:
            mem_data = self._memory_cache[cache_key]
            age = current_time - mem_data['timestamp']
            if age <= self.CACHE_TTL_MEMORY:
                cache_info['cached'] = True
                cache_info['reason'] = 'memory_hit'
                cache_info['age_seconds'] = age
                return mem_data['data'], cache_info
            else:
                # 메모리 캐시 만료 -> 삭제
                del self._memory_cache[cache_key]

        try:
            path = self.get_cache_path(code, analysis_type)
            if os.path.exists(path):
                # 파일 캐시 만료 체크
                mtime = os.path.getmtime(path)
                age = current_time - mtime
                
                if age > self.CACHE_TTL_FILE:
                    cache_info['reason'] = f'expired ({age:.1f}s > {self.CACHE_TTL_FILE}s)'
                    cache_info['age_seconds'] = age
                    return None, cache_info
                
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 파일 캐시 적중 시 메모리 캐시에도 업데이트
                self._memory_cache[cache_key] = {
                    'data': data,
                    'timestamp': mtime
                }
                
                cache_info['cached'] = True
                cache_info['reason'] = 'hit'
                cache_info['age_seconds'] = age
                return data, cache_info
            else:
                cache_info['reason'] = 'not_found'
        except Exception as e:
            print(f"[Cache Error] Load failed: {e}")
            cache_info['reason'] = f'error: {str(e)}'
        return None, cache_info

    def save(self, code, analysis_type, data):
        """데이터를 캐시에 저장 (메모리 + 파일 Atomic Write)"""
        try:
            # 1. 메모리 캐시 저장
            cache_key = f"{code}_{analysis_type}"
            self._memory_cache[cache_key] = {
                'data': data,
                'timestamp': datetime.datetime.now().timestamp()
            }

            # 2. 파일 캐시 저장 (Atomic Write: 임시 파일 -> 이름 변경)
            path = self.get_cache_path(code, analysis_type)
            temp_path = path + ".tmp"
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 윈도우에서는 rename 시 대상 파일이 있으면 에러가 발생할 수 있으므로 replace 사용
            if os.path.exists(path):
                os.remove(path)
            os.rename(temp_path, path)
            
        except Exception as e:
            print(f"[Cache Error] Save failed: {e}")
            # 임시 파일 정리
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
