import datetime

def get_target_date(now=None):
    if now is None:
        now = datetime.datetime.now()
    
    weekday = now.weekday() # Mon=0, Sun=6
    current_time = now.time()
    market_start_time = datetime.time(9, 0) # 09:00
    
    target_date = now
    
    if weekday == 5: # Saturday
        target_date = now - datetime.timedelta(days=1)
    elif weekday == 6: # Sunday
        target_date = now - datetime.timedelta(days=2)
    else: # Weekday
        # If before market open, use previous business day
        if current_time < market_start_time:
            if weekday == 0: # Monday
                target_date = now - datetime.timedelta(days=3) # Use Friday
            else:
                target_date = now - datetime.timedelta(days=1)
        else:
            # Market is open or closed for the day, use Today
            target_date = now
            
    return target_date.strftime("%Y%m%d")

# Test cases
print("--- Test Cases ---")
# Sunday 2025-12-01 14:00 -> Should be Friday 2025-11-29
d = datetime.datetime(2025, 12, 1, 14, 0)
print(f"Sunday 2pm: {get_target_date(d)} (Expected: 20251129)")

# Saturday 2025-11-30 10:00 -> Should be Friday 2025-11-29
d = datetime.datetime(2025, 11, 30, 10, 0)
print(f"Saturday 10am: {get_target_date(d)} (Expected: 20251129)")

# Friday 2025-11-29 15:00 -> Should be Friday 2025-11-29
d = datetime.datetime(2025, 11, 29, 15, 0)
print(f"Friday 3pm: {get_target_date(d)} (Expected: 20251129)")

# Monday 2025-12-02 08:00 -> Should be Friday 2025-11-29
d = datetime.datetime(2025, 12, 2, 8, 0)
print(f"Monday 8am: {get_target_date(d)} (Expected: 20251129)")

# Monday 2025-12-02 09:30 -> Should be Monday 2025-12-02
d = datetime.datetime(2025, 12, 2, 9, 30)
print(f"Monday 9:30am: {get_target_date(d)} (Expected: 20251202)")
