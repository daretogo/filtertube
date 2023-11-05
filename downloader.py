import mysql.connector
import subprocess
import os
import time

import os
import subprocess
import glob

def move_to_plex(username):
    source_path = f'/home/aaron/filterTube/users/{username}/'
    dest_path = f'/home/aaron/J/YouTube Videos/{username}/'
    
    os.makedirs(dest_path, exist_ok=True)
    
    # Find all .mp4 files in the source directory
    mp4_files = glob.glob(os.path.join(source_path, '*.mp4'))
    
    if mp4_files:
        move_successful = True
        for file in mp4_files:
            try:
                command = ['sudo', 'mv', file, dest_path]
                result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode != 0:
                    print(f"Failed to move {file} with return code {result.returncode}")
                    print(f"stdout: {result.stdout}")
                    print(f"stderr: {result.stderr}")
                    move_successful = False
            except subprocess.CalledProcessError as e:
                print(f"Error: Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
                print(f"stdout: {e.stdout}")
                print(f"stderr: {e.stderr}")
                move_successful = False
        return move_successful
    else:
        print(f"No .mp4 files found in {source_path}")
        return False




def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="aaron",
        password="Bigdaddy",
        database="filtertube"
    )

def get_approved_request(db_connection):
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM req_history WHERE status = 'Approved' LIMIT 1")
    request = cursor.fetchone()
    cursor.close()
    return request

def update_request_status(db_connection, request_id, new_status):
    cursor = db_connection.cursor()
    cursor.execute("UPDATE req_history SET status = %s WHERE id = %s", (new_status, request_id))
    db_connection.commit()
    cursor.close()

def copy_to_history_and_remove(db_connection, request_id):
    cursor = db_connection.cursor()
    cursor.execute(
        """
        INSERT INTO req_history (date, requestor, video_name, status, URL, channel_name)
        SELECT date, requestor, video_name, status, URL, channel_name FROM req WHERE id = %s
        """,
        (request_id,)
    )
    cursor.execute("DELETE FROM req WHERE id = %s", (request_id,))
    db_connection.commit()
    cursor.close()

def download_video(video_url, username):
    command = ['youtube-dl', video_url, '-o', f'./users/{username}/%(title)s.%(ext)s']
    result = subprocess.run(command)
    return result.returncode == 0  # Returns True if download succeeded, False otherwise

def main():
    while True:
        db_connection = connect_db()
        request = get_approved_request(db_connection)
        if request:
            update_request_status(db_connection, request['id'], 'Pending Download')
            print(f'Downloading {request["URL"]} for {request["requestor"]}')
            download_successful = download_video(request['URL'], request['requestor'])
            
            if download_successful:
                update_request_status(db_connection, request['id'], 'Successfully Downloaded')
                move_successful = move_to_plex(request['requestor'])
                if move_successful:
                    update_request_status(db_connection, request['id'], 'Moved to Plex')
                    
            db_connection.close()
        else:
            db_connection.close()
        time.sleep(30)  # Sleep for 30 seconds before checking again

if __name__ == '__main__':
    main()
