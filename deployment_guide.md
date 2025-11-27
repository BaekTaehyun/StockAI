# 웹 및 모바일 접속 가이드

## 1. 아이폰에서 즉시 접속하기 (ngrok 사용)
PC에서 실행 중인 서버를 외부(아이폰)에서 접속하려면 `ngrok`을 사용하는 것이 가장 빠릅니다.

1.  **ngrok 설치**: [ngrok 다운로드](https://ngrok.com/download) 후 설치합니다.
2.  **서버 실행**: 터미널에서 `python app.py`를 실행하여 로컬 서버를 켭니다.
3.  **ngrok 실행**: 새로운 터미널 창을 열고 다음 명령어를 입력합니다.
    ```bash
    ngrok http 5000
    ```
4.  **접속**: ngrok이 생성해준 URL (예: `https://xxxx-xxxx.ngrok-free.app`)을 아이폰 브라우저(Safari)에 입력하여 접속합니다.

## 2. 클라우드 배포 (상시 접속)
PC를 켜두지 않고 언제든 접속하려면 클라우드 호스팅이 필요합니다. (예: Render, Heroku)

### Render 배포 방법 (무료)
1.  [Render](https://render.com) 회원가입.
2.  "New +" 버튼 -> "Web Service" 선택.
3.  "Build and deploy from a Git repository" 선택 후 GitHub 리포지토리 연결.
4.  설정:
    - **Runtime**: Python 3
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `gunicorn app:app`
5.  "Create Web Service" 클릭.
6.  배포 완료 후 제공되는 URL로 접속.

> [!NOTE]
> `Procfile`과 `requirements.txt`는 이미 준비해 두었습니다. GitHub에 푸시만 하시면 됩니다.
