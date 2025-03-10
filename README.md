# Twitter API Client

## Overview
This project is a Python script that interacts with the Twitter API. The script authenticates with Twitter API using OAuth 1.0a, likes a tweet by its ID, and handles API rate limits and authentication errors.

## Features
- **OAuth 1.0a Authentication**: Securely authenticates using API keys and tokens.
- **Like a Tweet**: Likes a tweet based on its ID.
- **Error Handling**: Manages authentication errors and API rate limits.
- **Logging**: Provides execution status logs.
- **Rate Limit Awareness**: Logs warnings for rate limits and retries for connection errors using exponential backoff.
- **Caching**: Prevents duplicate likes by maintaining a cache of liked tweets.

## Installation
### Prerequisites
Ensure you have **Python 3.12+** installed.

### Step 1: Clone the Repository
```sh
 git clone git@github.com:kirillsakh/twitter-api-client.git
```

### Step 2: Create a Virtual Environment
```sh
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### Step 3: Install Dependencies
```sh
pip install -r requirements.txt
```

## Configuration
### Step 4: Set Up API Credentials
Create a `.env` file in the project root and add the following:
```ini
CONSUMER_KEY=your_consumer_key
CONSUMER_SECRET=your_consumer_secret
ACCESS_TOKEN=your_access_token
ACCESS_TOKEN_SECRET=your_access_token_secret
```

## Usage
### Step 5: Run the Script
To like a tweet, execute:
```sh
python src/twitter/client.py
```
The script will prompt you to enter a Tweet ID:
```sh
Enter the tweet ID to like: 1234567890123456789
```
If successful, you will see:
```sh
Successfully liked tweet 1234567890123456789.
```

## License
MIT License.
