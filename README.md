# yt-crawler
A YouTube crawler that fetches videos meta data. Currently supports playlist and channel pages.

## Getting Started
Run `source install.sh`

This command will:

1. Install docker
2. Install all python dependencies
2. Install mysql server
	2.1. Make sure that the **password** matches with the one in file `saver.py`
3. Initialize the DB
4. Install and run a docker for PhantomJS

To run the code simply run `python main.py [url]`
If the URL is not specified  a default YouTube channel URL will be used.

The code will run indefinitely fetching the data and updating it to the database.

## Details
- PhantomJS was used instead of a simple request because some HTML element gets loaded dynamically.
- The database table primary key was chosen to be the same as the YouTube video ID.
- The code was split into 3 modules
  - `ytcrawler.py` contains the code that fetches and crawls YouTube. 
  - `saver.py` responsible for saving data to the DB and saving images to the local storage.
  - `main.py` takes the user provided URL and run the above 2 modules
		 - a `with` statement was  used to ensure that the driver and DB connection are closed upon exit.