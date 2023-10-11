import requests
import time
from datetime import datetime
from flask import Flask, jsonify, request
import threading


user_data_storage = {}
date_format = "%Y-%m-%dT%H:%M"
app = Flask(__name__)


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



date_format = "%Y-%m-%dT%H:%M"
user_data_storage = {}

def update_user_data():
    while True:
        try:
            response = requests.get("https://sef.podkolzin.consulting/api/users/lastSeen?offset=0")
            data = response.json()

            if isinstance(data, dict) and 'data' in data:
                user_list = data['data']
                for user_info in user_list:
                    if isinstance(user_info, dict):
                        user_id = user_info.get('userId')
                        is_online = user_info.get('isOnline')
                        last_seen_str = user_info.get('lastSeenDate')

                        current_time = datetime.now().strftime(date_format)

                        if user_id not in user_data_storage:
                            user_data_storage[user_id] = []

                        last_intervals = user_data_storage[user_id]

                        if is_online:
                            if not last_intervals or (last_intervals and last_intervals[-1][1] is not None):
                                user_data_storage[user_id].append([current_time, None])
                        else:

                            parts = last_seen_str.split(':')
                            last_seen_str = ":".join(parts[:2])


                            last_seen_datetime = datetime.strptime(last_seen_str, "%Y-%m-%dT%H:%M")
                            if last_intervals and last_intervals[-1][1] is None:
                                last_intervals[-1][1] = last_seen_datetime
                            else:
                                user_data_storage[user_id].append([current_time, last_seen_datetime])

            else:
                print("Incorrect data format:", data)

            print("Waiting 30 seconds before the next attempt....")
            time.sleep(30)
        except Exception as e:
            print("Error when updating data:", repr(e))


@app.route('/user_intervals', methods=['GET'])
def get_user_intervals():
    return jsonify(user_data_storage)


@app.route('/api/stats/user/total', methods=['GET'])
def get_total_user_online_time():
    user_id = request.args.get('userId')


    user_intervals = user_data_storage.get(user_id, [])

    total_time_seconds = 0

    for interval in user_intervals:
        start_time, end_time = interval

        if not isinstance(start_time, datetime):
            start_time = datetime.strptime(start_time, date_format)
        if end_time and not isinstance(end_time, datetime):
            end_time = datetime.strptime(end_time, date_format)

        end_time = end_time or datetime.now()

        if end_time <= start_time:
            total_time_seconds += (start_time - end_time).total_seconds()


    return jsonify({"totalTime": int(total_time_seconds)})





if __name__ == '__main__':

    data_update_thread = threading.Thread(target=update_user_data)
    data_update_thread.daemon = True
    data_update_thread.start()



    app.run(debug=True)
