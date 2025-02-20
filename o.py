import tweepy

consumer_key = "zBvFMSNZTMCwz8gBIyvxPmai7"
consumer_secret = "kOBv2Y4uHaoMVmZkWBLZktlgJz0QnxUXGXYoymLYT2YOnisSMi"
access_token = "1623235054058221574-SFSrIQYB9Y3jXAYfo1Rzqa9M1tT5zC"
access_token_secret = "fACPwHSt196ibOjnNiRKtwYzt9Nza2wO3w6jh2NhzBxs2"


auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
)

api = tweepy.API(auth)

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)