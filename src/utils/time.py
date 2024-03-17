from datetime import datetime

# get current datetime
today = datetime.now()
print('Today Datetime:', today)

# Get current ISO 8601 datetime in string format
iso_date = today.isoformat()
print('ISO DateTime:', iso_date)
