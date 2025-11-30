from theme_service import ThemeService

def main():
    print("=== Naver Theme Cache Manual Update ===")
    print("This script will scrape ALL themes from Naver Finance.")
    print("It may take 3-5 minutes. Please wait...")
    
    service = ThemeService()
    success = service.update_naver_cache()
    
    if success:
        print("\n✅ Naver theme cache updated successfully!")
    else:
        print("\n❌ Failed to update Naver theme cache.")

if __name__ == "__main__":
    main()
