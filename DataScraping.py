#Importing necessary Librarires
import googleapiclient.discovery
from googleapiclient.errors import HttpError
import streamlit as st
from pymongo import MongoClient
from sqlalchemy import create_engine
import pandas as pd
import isodate
from datetime import datetime 


# YouTube API 
api_key = "AIzaSyB8uxwP3CzNNRsEUDOWIevedYspMC6TCvw"
youtube = googleapiclient.discovery.build("youtube","v3", developerKey=api_key)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['youtube_data'] # Select the Database
collection = db['data'] # Select the collection

# Setup MySQL engine
mysql_engine = create_engine('mysql+pymysql://root:karuna@localhost/mde88')


#Function to collect the channel details using channel_id
def channel_details(channel_id):
  request = youtube.channels().list(
          part="snippet,contentDetails,statistics",
          id=channel_id)
  response = request.execute()
  if response['items']:

    z = dict(channel_id = response['items'][0]['id'],
      channel_name= response['items'][0]['snippet']['title'],
      channel_description = response['items'][0]['snippet']['description'],
      channel_type = response['items'][0]['snippet'].get('type','Not available'),
      published_at = response['items'][0]['snippet']['publishedAt'],
      thumbnail_url = response['items'][0]['snippet']['thumbnails']['default']['url'],
      subscriber_count = int(response['items'][0]['statistics'].get('subscriberCount',0)), #To avoid potential error returns empt dict
      video_count = int(response['items'][0]['statistics'].get('videoCount',0)),
      view_count = int(response['items'][0]['statistics'].get('viewCount',0)),
      comment_count = int(response['items'][0]['statistics'].get('commentCount',0)),
      playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads'])
    return z
  else:
    return None


#Function to collect the playlist details created by channel
def playlist_details(channel_id):
  playlists=[]
  request = youtube.playlists().list(
          part="snippet,contentDetails",
          channelId=channel_id,
          maxResults=50
      )
  while request:
      response = request.execute()
      for i in response['items']:
       playlist = dict(channel_id = i['snippet']['channelId'],
                       channel_name = i['snippet']['channelTitle'],
                playlist_id = i['id'],
                playlist_name = i['snippet']['localized']['title'])
       playlists.append(playlist)

      request = youtube.playlists().list_next(request, response)
  return playlists


#Function to fetching video_id using upload playlist_id to fetch video_id for video details and its comment details
def video_id(playlist_id):
  all_videos=[]
  request = youtube.playlistItems().list(
          part="contentDetails",
          maxResults=50,
          playlistId=playlist_id
      )
  while request:
    response = request.execute()
    all_videos.extend(response['items'])
    request = youtube.playlistItems().list_next(request, response)

    video_ids= []
  for i in all_videos:
    video_id= i['contentDetails']['videoId']
    video_ids.append(video_id)
  return video_ids


#Function to Parse the duration into HH:MM:SS
def duration_into_hms(duration):
  #Parse the duration
  duration_parse = isodate.parse_duration(duration)
  total_sec = int(duration_parse.total_seconds())
  #Converting total seconds into hours,minutes and seconds
  hours = total_sec // 3600
  minutes = (total_sec % 3600) // 60
  seconds = total_sec % 60

  return "{:02}:{:02}:{:02}".format(hours,minutes,seconds)
  
  
#Function to get video Details using video_id
def video_details(all_video_ids):
  videos= []
  for video_id in all_video_ids:
    request = youtube.videos().list(part="snippet,contentDetails,statistics",
          id=video_id
      )
    response = request.execute()

    duration_text = response['items'][0]['contentDetails']['duration']
    durations_convert_into_hms = duration_into_hms(duration_text)
  

    y = dict(video_id = video_id,
             channel_id = response['items'][0]['snippet']['channelId'],
             playlist_id = playlist_id,
             video_name = response['items'][0]['snippet']['title'],
             video_desc = response['items'][0]['snippet']['description'],
             video_tags = response['items'][0]['snippet'].get((),['tags']),
             video_published = response['items'][0]['snippet']['publishedAt'],
             view_count =int(response['items'][0]['statistics'].get('viewCount',0)),
             like_count = int(response['items'][0]['statistics'].get('likeCount',0)),
             dislike_count = int(response['items'][0]['statistics'].get('dislikeCount',0)),
             favorite_count = int(response['items'][0]['statistics'].get('favoriteCount',0)),
             comment_count = int(response['items'][0]['statistics'].get('commentCount',0)),
             durations = durations_convert_into_hms,
             thumbnail = response['items'][0]['snippet']['thumbnails']['default']['url'],
             caption_status = response['items'][0]['contentDetails'].get('caption','Not available'))

    videos.append(y)
  return videos


#Function to get comment Details
def comment_details(all_video_ids):
  comments =[]
  for video_id in all_video_ids:
    try: # this will try to execute the code that fetches comments
      request = youtube.commentThreads().list(
                part="snippet",
                maxResults=10,
                order="time",
                videoId=video_id
            )
      response = request.execute()

      for i in response['items']:
        x = dict(
            video_id=video_id,
            comment_id = i['id'],
            comment_text = i['snippet']['topLevelComment']['snippet']['textOriginal'],
            comment_author = i['snippet']['topLevelComment']['snippet']['authorDisplayName'],
            comment_publishedAt = i['snippet']['topLevelComment']['snippet']['publishedAt'])

        comments.append(x)
    except HttpError as e: # this will handle the exception when comments are disabled
      if e.resp.status == 403 and "commentsDisabled" in str(e):
        print(f"Comments are disabled for video: {video_id}")
      else: # this will raise other errors encountered
        raise e
  return comments


# Function to migrate data from MongoDb to SQL
def migrate_data_to_sql(engine, data, table_name): 
    df = pd.DataFrame(data)
    try:
      df.to_sql(table_name, engine, if_exists='append', index=False)
    except Exception as e:
      st.write("Error migrating to",table_name)



#Title
st.title("**YouTube Data Harvesting and Warehousing using SQL and Streamlit**")

st.markdown("""Welcome to the YouTube Data Processing App! This app allows you to:
1. Scrape YouTube data and store it in MongoDB.
2. Migrate data from MongoDB to SQL.
3. Query the SQL database to get insights.""")

# Stage 1: Scrape the Youtube data and store in MongoDB
st.markdown("### 🚀 Stage 1: Scrape the YouTube Data and Store in MongoDB")
with st.expander("Enter the channel ID and click 'Scrape and store in MongoDB' to start scraping data from YouTube."):
  #Get the Channel Id from User
  channel_id = st.text_input("Enter the channel ID:",help="Enter the YouTube channel ID you want to scrape data from.")
  if st.button("Scrape and store in MongoDB"):
    if channel_id:
      channel_info = channel_details(channel_id)
      if channel_info:
        playlist_id = channel_info['playlist_id']
        all_video_ids = video_id(playlist_id)
        youtube_data_to_mongodb = dict (channel_Details = channel_info,
                                  playlist_Details = playlist_details(channel_id),
                                  Video_Details = video_details(all_video_ids),
                                  Comments = comment_details(all_video_ids))

        collection.insert_one(youtube_data_to_mongodb)
      
        st.success("Data has been scraped and stored in MongoDB!")
      else:
        st.error("Please enter the valid YouTube Channel ID")
    else:
      st.error("Please enter the valid YouTube Channel ID")

# Stage 2: Migrate data from MongoDB to SQL
st.markdown("### 📦 Stage 2: Migrate Data from MongoDB to SQL")
#Fetch all documents 
documents = list(collection.find())
channel_names = [doc['channel_Details']['channel_name']for doc in documents]

with st.expander("Select a channel to migrate its data from MongoDB to SQL."):
  # Dropdown for selecting the channel name
  selected_channel = st.selectbox("Select a channel to migrate:", channel_names)

  if st.button("Migrate Data from MongoDB to SQL"):
      for channel in documents:
          if channel['channel_Details']['channel_name'] == selected_channel:
            st.write("Migrating Document {}".format(channel['channel_Details']['channel_name']))
            migrate_data_to_sql(mysql_engine, [channel.get('channel_Details')], 'Channel')
            migrate_data_to_sql(mysql_engine, channel.get('playlist_Details',[]), 'Playlist')
            migrate_data_to_sql(mysql_engine, channel.get('Video_Details',[]), 'Video')
            migrate_data_to_sql(mysql_engine, channel.get('Comments',[]), 'Comment')
            st.success('Data for {} has been migrated to the MySQL database!'.format(selected_channel))
            break


# Stage:3 Query MySQL Database
st.markdown("### 🔍 Stage 3: Query MySQL Database")
with st.expander("Select a query to display the results from the SQL database."):
  questions= {"1.What are the names of all the videos and their corresponding channels?" : "select video.video_name, channel.channel_name from video join channel on video.channel_id = channel.channel_id", 
              "2.Which channels have the most number of videos, and how many videos do they have?" : "select channel_name,video_count from channel order by video_count desc limit 1",
              "3.What are the top 10 most viewed videos and their respective channels?":"select video.video_name,video.view_count,channel.channel_name from video join channel on video.channel_id=channel.channel_id order by view_count desc limit 10;",
              "4.How many comments were made on each video, and what are their corresponding video names?":"select comment_count,video_name from video",
              "5.Which videos have the highest number of likes, and what are their corresponding channel names?":"select video.like_count,channel.channel_name from video join channel on video.channel_id = channel.channel_id order by like_count desc",
              "6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?":"select like_count,dislike_count,video_name from video",
              "7.What is the total number of views for each channel, and what are their corresponding channel names?":"select view_count,channel_name from channel",
              "8.What are the names of all the channels that have published videos in the year 2022?":"select channel_name from channel where YEAR(published_at)= 2022",
              "9.What is the average duration of all videos in each channel, and what are their corresponding channel names?":"SELECT Channel.channel_name, sec_to_time(Floor(AVG(time_to_sec(video.durations)))) as average_duration  FROM Video JOIN Channel ON Video.channel_id = Channel.channel_id GROUP BY Channel.channel_name",
              "10.Which videos have the highest number of comments, and what are their corresponding channel names?":"select video.comment_count,channel.channel_name from video join channel on video.channel_id = channel.channel_id order by comment_count desc limit 1"}

  question = st.selectbox("Select a query to diaplay",questions.keys())

  if st.button("Execute Query"):
    query = questions.get(question)
    try:
      data = pd.read_sql(query,mysql_engine)
      st.dataframe(data)
      st.markdown("""Thank you for using the YouTube Data Processing App!""")
    except Exception as e:
      st.error("An error occured {}".format('e'))

