import pytz
from datetime import datetime, timedelta

def check_availability():
    est = pytz.timezone('US/Eastern')
    now_est = datetime.now(est)
    current_hour = now_est.hour
    current_day = now_est.weekday()

    if current_day == 1 and current_hour >= 4:  # Tuesday 4am onwards
        return True, now_est.strftime("%A")
    elif 1 < current_day < 4:  # All day Wednesday and Thursday until 7pm
        return True, now_est.strftime("%A")
    elif current_day == 4 and current_hour < 19:  # Thursday until 7pm
        return True, now_est.strftime("%A")
    else:
        return False, now_est.strftime("%A")
    

def get_current_week(current_date):
    # Updated for 2025 NFL season (first game September 4th, 2025)
    date_week_dict = {
    '9/4/2025': 1, '9/8/2025': 2, '9/15/2025': 3, '9/22/2025': 4,
    '9/29/2025': 5, '10/6/2025': 6, '10/13/2025': 7, '10/20/2025': 8,
    '10/27/2025': 9, '11/3/2025': 10, '11/10/2025': 11, '11/17/2025': 12,
    '11/24/2025': 13, '12/1/2025': 14, '12/8/2025': 15, '12/15/2025': 16,
    '12/22/2025': 17, '12/29/2025': 18
    }
    # Convert the string dates to datetime objects
    date_week_dict_converted = {datetime.strptime(date, '%m/%d/%Y'): week for date, week in date_week_dict.items()}
    
    # Sort the dates in descending order
    sorted_dates = sorted(date_week_dict_converted.keys(), reverse=True)
    
    # Iterate through the sorted dates to find the corresponding week number
    for date in sorted_dates:
        if current_date >= date:
            return date_week_dict_converted[date]
    return None  # If current date is before all the dates in the dictionary
