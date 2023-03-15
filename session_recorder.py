import datetime as dt
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser
import json
import os

print('Enter "h" to see the list of commands.')
ongoing_sessions_file = 'ongoing_sessions.txt'
session_list_file = 'session_list.txt'

def write_txt(filetxt, lst):
    with open(filetxt, 'w') as f:
        f.writelines(line + '\n' for line in lst)

def dump_json(filejson, dictionary):
    with open(filejson, 'w') as f:
        json.dump(dictionary, f)

def to_iso(datetime):
    return dt.datetime.isoformat(datetime)

def to_dt(string):
    return dt.datetime.fromisoformat(string)

def to_timedelta(list):
    for duration_str in list:
        duration = dt.datetime.strptime(duration_str, '%H:%M:%S.%f')
        duration_timedelta = timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second, microseconds=duration.microsecond)
    return duration_timedelta

def detail_timeparse(date_string):
    try:
        parsed_input = parser.parse(date_string)
    except ValueError:
        print('Invalid date.' + '\n')
    return parsed_input



cmd = ''
while cmd != 'k':
    # Takes user input
    user_inputs = input('> ').split()
    cmd = user_inputs[0]
    if cmd not in ['k', 'a', 'r', 's', 'e', 'l', 'h', 'p', 'd']:
        print('Invalid command.' + '\n')
        continue


    # Creates session_list and ongoing_session_list from files
    if cmd in ['a', 'r', 's', 'e', 'p', 'l', 'd']:
        session_list = [line.strip() for line in open(session_list_file) if line.strip() != ""]
        ongoing_sessions_list = [line.strip() for line in open(ongoing_sessions_file)]
    # Creates session_name and file_name if command has session_name argument
    if cmd in ['a', 'r', 's', 'e', 'p', 'd']:
        try:
            session_name = user_inputs[1]
            log_file = 'log/log_' + session_name + '.json'
        except IndexError:
            print('Missing arguments' + '\n')
            continue
    if cmd in ['r', 's', 'e', 'p', 'd']:
        with open(log_file) as f:
            session_dict = json.load(f)


    # Add command
    if cmd == 'a':
        # Checks if session exists
        if session_name in session_list:
            print('A session with the same name already exists.' + '\n')
            continue

        # Appends new session to session list file
        session_list.append(session_name)
        write_txt(session_list_file, session_list)

        # Creates new log.json file
        create = {}
        dump_json(log_file, create)
        print('Created session with log file: ' + log_file + '\n')
    

    # Start command
    if cmd == 's':
        # Checks if session exists
        if session_name not in session_list:
            print('That session does not exist.' + '\n')
            continue
        # Checks if session is ongoing
        elif session_name in ongoing_sessions_list:
            print('That session is already ongoing.' + '\n')
            continue

        # Grabs session key
        session_keys = [key for key in session_dict.keys()]
        session_key = 0 if session_keys == [] else len(session_keys)
        
        # Appends new session data to session log
        session_start_dt = dt.datetime.now()
        session_start_str = session_start_dt.isoformat()
        session_dict[session_key] = {"start":session_start_str, "end":0, "duration":0}
        dump_json(log_file, session_dict)

        # Appends ongoing session to ongoing session list
        ongoing_sessions_list.append(session_name)
        write_txt(ongoing_sessions_file, ongoing_sessions_list)

        print(f'Started session {session_name} at {session_start_str}' + '\n')


    # End command
    if cmd == 'e':
        # Checks if session exists
        if session_name not in session_list:
            print('That session does not exist.' + '\n')
            continue
        # Checks if session is ongoing
        elif session_name not in ongoing_sessions_list:
            print('That session have not been started.' + '\n')
            continue

        # Grabs session key
        session_keys = [key for key in session_dict.keys()]
        session_key = str(len(session_keys) - 1)

        # Modifies new session data from session log
        session_end_dt = dt.datetime.now()
        session_end_str = session_end_dt.isoformat()

        session_start_str = session_dict[session_key]['start']
        session_start_dt = to_dt(session_start_str)

        session_duration_dt = session_end_dt - session_start_dt
        session_duration_str = str(session_duration_dt)

        session_dict[session_key]['end'] = session_end_str
        session_dict[session_key]['duration'] = session_duration_str

        dump_json(log_file, session_dict)

        # Removes ongoing session from ongoing session list
        ongoing_sessions_list.remove(session_name)
        write_txt(ongoing_sessions_file, ongoing_sessions_list)

        print(f'Ended session {session_name} at {session_end_str}')
        print(f'Session lasted for {session_duration_str}' + '\n')


    # Remove command
    if cmd == 'r':
        # Checks if session exists
        if session_name not in session_list:
            print('That session does not exist.' + '\n')
            continue
        # Checks if session ongoing
        elif session_name in ongoing_sessions_list:
            print('That session is currently ongoing, end the session first before removing.' + '\n')
            continue

        # Removes session from session list file
        session_list.remove(session_name)
        write_txt(session_list_file, session_list)
        print('Session removed.')
        # Removes session json log
        remove_log = input('Do you want to remove the log file as well? Y/N\n> ')
        if remove_log == 'Y':
            if os.path.exists(log_file):
                os.remove(log_file)
                print("File deleted successfully." + '\n')
            else:
                print("The file does not exist." + '\n')


    # Pop command
    if cmd == 'p':
        # Checks if session exists
        if session_name not in session_list:
            print('That session does not exist.' + '\n')
            continue
        # Checks if session is ongoing
        elif session_name in ongoing_sessions_list:
            print('That session is currently ongoing, end the session first before removing.' + '\n')
            continue

        # Grab the session key
        session_keys = [key for key in session_dict.keys()]
        if session_keys == []:
            print(f'Log for {session_name} is empty.' + '\n')
        else:
            session_key = str(len(session_keys) - 1)
            session_dict.pop(session_key)
            dump_json(log_file, session_dict)
            print(f"Removed most recent session log of {session_name}." + '\n')

    
    # Details command
    if cmd == 'd':
        # Checks if session exists
        if session_name not in session_list:
            print('That session does not exist.' + '\n')
            continue
        # Checks if session is ongoing
        elif session_name in ongoing_sessions_list:
            print('That session is currently ongoing, end the session first before checking the details.' + '\n')
            continue
        # Grabs inputs
        try: 
            if user_inputs[2] in ['daily', 'weekly', 'monthly', 'yearly']:
                time_until = dt.datetime.now()
                delta_map = {'daily': {'days':1}, 'weekly': {'weeks': 1}, 'monthly': {'months': 1}, 'yearly': {'years': 1}}
                time_delta = relativedelta(**delta_map[user_inputs[2]])
                time_from = time_until - time_delta
            else: 
                time_from = detail_timeparse(user_inputs[2])
                time_until = detail_timeparse(user_inputs[3])
        except IndexError:
            print('Missing argument.' + '\n')
            continue

        # time_now = dt.datetime.now()
        session_logs = [[v['start'], v['end'], v['duration']] for k, v in session_dict.items()]
        durations_list = [log[2] for log in session_logs if (to_dt(log[0]) > time_from or to_dt(log[1]) < time_until)]
        duration_timedelta_list = []
        for duration_str in durations_list:
            duration = dt.datetime.strptime(duration_str, '%H:%M:%S.%f')
            duration_timedelta = timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second, microseconds=duration.microsecond)
            duration_timedelta_list.append(duration_timedelta)
        duration_total = sum(duration_timedelta_list, timedelta())
        print(f'You have {duration_total} logged on {session_name}.' + '\n')

    

    # List command
    if cmd == 'l':
        if len(session_list) == 0:
            print('Session list is empty.' + '\n')
            continue

        print('List of sessions:')
        for session in session_list:
            print(session)
        print('\n' + 'List of ongoing sessions:')
        for session in ongoing_sessions_list:
            print(session)
        print()


    # Help command
    if cmd == 'h':
        print("""====================
h : Returns command list
l : Returns a list of sessions
a {session_name} : Adds a session to session list
s {session_name} : Starts a session
e {session_name} : Ends a started session
r {session_name} : Removes a session
p {session_name} : Removes most recent log of a session
d {session_name} {date_from} {date_until} : Returns the total duration inside a date range
k : Stops the program
====================
""")