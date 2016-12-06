# DailyDevTalk

## Introduction
A Twitter bot to help foster discussion among the development community. By tweeting with the hashtag #DevTalk, you can be matched up with another member of the #DevTalk community for discussion.

## How It Works
Every time the system receives a tweet, it looks at the last 100 tweets using the hashtag #DevTalk and finds the [cosine simularity](http://stackoverflow.com/questions/15173225/how-to-calculate-cosine-similarity-given-2-sentence-strings-python) between the new tweet and the tweet found. It finds the tweet with the highest similarity score, and then connects the two users.

## Improvements
The system is currently very much a work-in-progress and is very inefficient. Here is a (continuously updated) list of improvements to be made:
 - Store old tweets every hour
 - Create hashmap of tweets on retrieval with vector sum
 - Remove usernames and links from counters
 - Create new status objects that strip unnecessary information to reduce server load

I also eventually hope to implement a system that measures semantic similarity (as opposed to just surface similarity) through natural language processing.

## Documentation
Coming soon!