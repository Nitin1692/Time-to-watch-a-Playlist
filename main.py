import os
from dotenv import load_dotenv
import re
from datetime import timedelta
from googleapiclient.discovery import build
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/',methods=['GET'])
def hello_world():
    return render_template('index.html')

@app.route('/',methods=['POST'])
def submitbutton():
   load_dotenv()
   API_KEY = os.getenv('API_KEY')

   youtube = build('youtube', 'v3', developerKey=API_KEY)

   hours_pattern = re.compile(r'(\d+)H')
   minutes_pattern = re.compile(r'(\d+)M')
   seconds_pattern = re.compile(r'(\d+)S')

   total_seconds = 0

   play = request.form.get("input")
   nextPageToken = None
   while True:
        pl_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=play,
            maxResults=50,
            pageToken=nextPageToken
        )

        pl_response = pl_request.execute()

        vid_ids = []
        for item in pl_response['items']:
            vid_ids.append(item['contentDetails']['videoId'])

        vid_request = youtube.videos().list(
            part="contentDetails",
            id=','.join(vid_ids)
        )

        vid_response = vid_request.execute()

        for item in vid_response['items']:
            duration = item['contentDetails']['duration']

            hours = hours_pattern.search(duration)
            minutes = minutes_pattern.search(duration)
            seconds = seconds_pattern.search(duration)

            hours = int(hours.group(1)) if hours else 0
            minutes = int(minutes.group(1)) if minutes else 0
            seconds = int(seconds.group(1)) if seconds else 0

            video_seconds = timedelta(
                hours=hours,
                minutes=minutes,
                seconds=seconds
            ).total_seconds()

            total_seconds += video_seconds

        nextPageToken = pl_response.get('nextPageToken')

        if not nextPageToken:
            break

   total_seconds = int(total_seconds)

   minutes, seconds = divmod(total_seconds, 60)
   hours, minutes = divmod(minutes, 60)

   time = f'{hours}:{minutes}:{seconds}'
   return render_template('index.html', Timer=time)

if __name__ == '__main__':
    app.run(port=3000,debug=True)


       