# YouTube-Data-Harvesting-and-Warehousing-with-SQL-Streamlit
 Comprehensive data pipeline for YouTube data using Streamlit, MongoDB, and SQL.
### YouTube Data Harvesting and Warehousing using SQL and Streamlit

#### Overview
This project provides a comprehensive solution for collecting, storing, and analyzing data from YouTube. The main components include scraping data from YouTube using the YouTube Data API, storing this data in MongoDB, migrating it to an SQL database, and querying it for analysis through a Streamlit application. This project is modular, maintainable, and portable, ensuring that it can be easily extended and deployed in different environments.

#### Project Structure
The project is organized into several modules, each responsible for different aspects of the functionality:

```
youtube-data-harvesting/
├── LICENSE
├── README.md
├── requirements.txt
├── main.py
├── config.py
├── youtube_api.py
├── mongodb_utils.py
├── sql_utils.py
└── streamlit_app.py
```

1. **`LICENSE`**: Contains the license information for the project.
2. **`README.md`**: Provides an overview of the project, installation instructions, and usage details.
3. **`requirements.txt`**: Lists all the dependencies required for the project.
4. **`main.py`**: Entry point for the project to run the Streamlit app.
5. **`config.py`**: Stores configuration constants like API keys and database connection strings.
6. **`youtube_api.py`**: Contains functions for interacting with the YouTube API.
7. **`mongodb_utils.py`**: Contains functions for interacting with MongoDB.
8. **`sql_utils.py`**: Contains functions for interacting with the SQL database.
9. **`streamlit_app.py`**: Contains the Streamlit app logic.

#### Detailed Explanation

##### `config.py`
This file stores configuration constants like the YouTube API key and database connection strings.

```python
API_KEY = "YOUR_YOUTUBE_API_KEY"
MONGO_URI = 'mongodb://localhost:27017/'
SQL_URI = 'mysql+pymysql://root:password@localhost/your_database'
```

##### `youtube_api.py`
This module handles all interactions with the YouTube API, including fetching channel details, playlist details, video IDs, video details, and comments.

- **Initialize YouTube API client**: Initializes the YouTube API client using the provided API key.
- **Get Channel Details**: Fetches details of a specified YouTube channel.
- **Get Playlist Details**: Fetches playlists associated with a specified YouTube channel.
- **Get Video IDs**: Retrieves video IDs from a specified playlist.
- **Get Video Details**: Fetches details of specified videos.
- **Get Comment Details**: Fetches comments for specified videos.

##### `mongodb_utils.py`
This module provides functions for interacting with MongoDB, including initializing the MongoDB client and storing data in MongoDB.

- **Initialize MongoDB**: Initializes the MongoDB client using the provided URI.
- **Store Data in MongoDB**: Stores data in the specified MongoDB collection.

##### `sql_utils.py`
This module provides functions for interacting with the SQL database, including initializing the SQL engine, migrating data to SQL, and querying the SQL database.

- **Initialize SQL Engine**: Initializes the SQL engine using the provided URI.
- **Migrate Data to SQL**: Migrates data to the specified SQL table.
- **Query SQL Database**: Executes SQL queries on the database and returns the results.

##### `streamlit_app.py`
This module contains the Streamlit application logic. It allows users to input a YouTube channel ID, retrieve and display channel data, store data in MongoDB, migrate data to an SQL database, and execute predefined SQL queries to analyze the data.

- **Main Function**: The main function that sets up the Streamlit app, handles user inputs, and performs the necessary data retrieval, storage, and querying operations.
- **Retrieve Data**: Fetches channel data and associated playlists, videos, and comments, then stores the data in MongoDB and migrates it to the SQL database.
- **Query SQL Database**: Allows users to select and execute predefined SQL queries on the SQL database, displaying the results in the Streamlit app.

##### `main.py`
The entry point for the project. It simply calls the main function from `streamlit_app.py`.

```python
from streamlit_app import main

if __name__ == "__main__":
    main()
```

#### Installation and Setup

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/your-username/youtube-data-harvesting.git
   cd youtube-data-harvesting
   ```

2. **Create a Virtual Environment and Activate It**:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Update Configuration**:
   Update the `config.py` file with your YouTube API key and database connection strings.

#### Running the Application
Start the Streamlit app:
```sh
streamlit run main.py
```

#### Using the Streamlit App

1. **Enter YouTube Channel ID**:
   Input a YouTube channel ID to retrieve and display channel data.

2. **Store and Migrate Data**:
   The app fetches channel details, playlists, videos, and comments, stores them in MongoDB, and migrates them to the SQL database.

3. **Execute Queries**:
   Select and execute predefined SQL queries to analyze the data. The results are displayed within the Streamlit app.

#### SQL Queries
The app provides several predefined SQL queries for analyzing the YouTube data:

1. **List video names and their corresponding channels**:
   ```sql
   SELECT video.video_name, channel.channel_name FROM video JOIN channel ON video.channel_id = channel.channel_id ORDER BY channel.channel_name
   ```

2. **Channels with the most videos**:
   ```sql
   SELECT channel.channel_name, COUNT(video.video_id) AS video_count FROM channel JOIN video ON channel.channel_id = video.channel_id GROUP BY channel.channel_name ORDER BY video_count DESC
   ```

3. **Top 10 most viewed videos and their channels**:
   ```sql
   SELECT video.video_name, channel.channel_name, video.view_count FROM video JOIN channel ON video.channel_id = channel.channel_id ORDER BY video.view_count DESC LIMIT 10
   ```

4. **Comments count per video**:
   ```sql
   SELECT video.video_name, COUNT(comment.comment_id) AS comment_count FROM video JOIN comment ON video.video_id = comment.video_id GROUP BY video.video_name ORDER BY comment_count DESC
   ```

5. **Videos with highest likes and their channels**:
   ```sql
   SELECT video.video_name, channel.channel_name, video.like_count FROM video JOIN channel ON video.channel_id = channel.channel_id ORDER BY video.like_count DESC
   ```

6. **Total likes and dislikes per video**:
   ```sql
   SELECT video.video_name, video.like_count, video.dislike_count FROM video ORDER BY (video.like_count + video.dislike_count) DESC
   ```

7. **Total views per channel**:
   ```sql
   SELECT channel.channel_name, SUM(video.view_count) AS total_views FROM channel JOIN video ON channel.channel_id = video.channel_id GROUP BY channel.channel_name ORDER BY total_views DESC
   ```

8. **Channels with videos published in 2022**:
   ```sql
   SELECT DISTINCT channel.channel_name FROM channel JOIN video ON channel.channel_id = video.channel_id WHERE YEAR(video.video_published) = 2022
   ```

9. **Average video duration per channel**:
   ```sql
   SELECT channel.channel_name, AVG(TIME_TO_SEC(video.duration)) AS avg_duration_sec FROM channel JOIN video ON channel.channel_id = video.channel_id GROUP BY channel.channel_name ORDER BY avg_duration_sec DESC
   ```

10. **Videos with highest number of comments and their channels**:
   ```sql
   SELECT video.video_name, channel.channel_name, video.comment_count FROM video JOIN channel ON video.channel_id = channel.channel_id ORDER BY video.comment_count DESC
   ```

#### License
This project is licensed under the MIT License.

#### Conclusion
This project provides a robust framework for harvesting and analyzing YouTube data using modern technologies like Streamlit, MongoDB, and SQL. It is designed to be modular, maintainable, and portable, making it an excellent tool for both learning and practical applications in data analysis and software development.

