import requests
import time
from datetime import datetime
from flask import Flask, jsonify, request
import threading

app = Flask(__name__)

user_data_storage = {}
blacklist = set()
date_format = "%Y-%m-%dT%H:%M"

def format_date_string(date_string):
    dash_count = 0
    formatted_date_string = ''
    for char in date_string:
        if char == '-':
            dash_count += 1
        if dash_count == 3:
            formatted_date_string += 'T'
            dash_count = 0
        else:
            formatted_date_string += char
    return formatted_date_string




def fetch_user_data(page_number):
    try:
        response = requests.get(f"https://sef.podkolzin.consulting/api/users/lastSeen?offset={page_number}")
        data = response.json()
        return data
    except Exception as e:
        print("Error when fetching user data:", repr(e))
        return None

def process_user_data(data):
    if not isinstance(data, dict) or 'data' not in data:
        print("Incorrect data format:", data)
        return

    user_list = data['data']
    for user_info in user_list:
        user_id = user_info.get('userId')
        is_online = user_info.get('isOnline')
        last_seen_str = user_info.get('lastSeenDate')
        current_time = datetime.now().strftime(date_format)

        if user_id in blacklist:
            continue
        if user_id not in user_data_storage:
            user_data_storage[user_id] = []

        last_intervals = user_data_storage[user_id]

        if is_online:
            if not last_intervals or (last_intervals and last_intervals[-1][1] is not None):
                user_data_storage[user_id].append([current_time, None])
        else:
            parts = last_seen_str.split(':')
            last_seen_str = ":".join(parts[:2])
            last_seen_datetime = datetime.strptime(last_seen_str, date_format)
            if last_intervals and last_intervals[-1][1] is None:
                last_intervals[-1][1] = last_seen_datetime
            else:
                user_data_storage[user_id].append([current_time, last_seen_datetime])

def update_user_data():
    page_number = 1
    while True:
        data = fetch_user_data(page_number)
        if data is None:

            pass
        else:
            process_user_data(data)


        if len(data.get('data', [])) > 0:
            page_number += 1
        else:
            break

        print("Waiting 30 seconds before the next attempt....")
        time.sleep(30)

@app.route('/user_intervals', methods=['GET'])
def get_user_intervals():
    return jsonify({user_id: intervals for user_id, intervals in user_data_storage.items() if user_id not in blacklist})

@app.route('/api/stats/user/total', methods=['GET'])
def get_total_user_online_time():
    user_id = request.args.get('userId')
    response = calculate_total_user_online_time(user_id)
    return jsonify(response)

@app.route('/api/stats/user/average', methods=['GET'])
def get_user_average_time():
    user_id = request.args.get('userId')
    response = calculate_user_average_time(user_id)
    return jsonify(response)

@app.route('/api/user/forget', methods=['POST'])
def forget_user():
    user_id = request.args.get('userId')
    response = forget_user_data(user_id)
    return jsonify(response)

def calculate_total_user_online_time(user_id):
    if user_id in blacklist:
        return {"error": "User ID is in the blacklist and has been forgotten."}

    user_intervals = user_data_storage.get(user_id, [])
    total_time_seconds = 0

    for interval in user_intervals:
        start_time, end_time = interval

        start_time = parse_date(start_time)
        end_time = parse_date(end_time) if end_time else datetime.now()

        if end_time <= start_time:
            total_time_seconds += (start_time - end_time).total_seconds()

    return {"totalTime": int(total_time_seconds)}

def calculate_user_average_time(user_id):
    if user_id in blacklist:
        return {"error": "User ID is in the blacklist and has been forgotten."}

    user_intervals = user_data_storage.get(user_id, [])
    total_time_seconds = 0

    for interval in user_intervals:
        start_time, end_time = interval

        start_time = parse_date(start_time)
        end_time = parse_date(end_time) if end_time else datetime.now()

        if end_time <= start_time:
            total_time_seconds += (start_time - end_time).total_seconds()

    num_intervals = len(user_intervals)

    if num_intervals > 0:
        total_days = (end_time - parse_date(user_intervals[0][0])).days + 1
        total_weeks = total_days // 7

        daily_average = total_time_seconds / num_intervals
        weekly_average = total_time_seconds / (total_weeks + 1)

        return {
            "weeklyAverage": int(weekly_average),
            "dailyAverage": int(daily_average)
        }
    else:
        return {
            "weeklyAverage": 0,
            "dailyAverage": 0
        }

def forget_user_data(user_id):
    if user_id:
        blacklist.add(user_id)
        if user_id in user_data_storage:
            del user_data_storage[user_id]
        return {"userId": user_id}
    else:
        return {"error": "Missing 'userId' parameter in the request."}

def parse_date(date_string):
    return datetime.strptime(date_string, date_format)

if __name__ == '__main__':
    data_update_thread = threading.Thread(target=update_user_data)
    data_update_thread.daemon = True
    data_update_thread.start()
    app.run(debug=True)
