# canary

canary is a sentiment analysis & visualization tool.

This application was my back end capstone for my 6-month tenure at Nashville Software School, where I spent 3 months focused on learning Python and the Django framework, primarily. 

canary utilizes Twitter's Streaming API to gather tweets based on the user's search. Each tweet that is streamed is processed and given a sentiment ranking using the TextBlob Python library sentiment analysis. Some revisions in this department lay in store. The user is displayed graphical data related to the overall sentiment of tweets based on their search, along with corresponding tweet origin (when available).

all tweets and certain data are stored in a local SQL database. 

## Application Flow

1. User enters topic or keyword.
2. canary intitializes streaming connection with Twitter API with user's keyword as query string.
3. As tweets are processed, user will be displayed graphical reflection of analyzed data.
4. After user has discontinued current stream, user can enter new topic or keyword and begin a new analysis.

## Installation

Detailed installation notes coming soon!

In the meantime, [contact me](https://www.github.com/stevenwally) with any questions you have!


## Built With

* Python
* Django
* Twitter Streaming API
* TextBlob


## Author

* **Steven Holmes** - [stevenwally](https://github.com/stevenwally)
