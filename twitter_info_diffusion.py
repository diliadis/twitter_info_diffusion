import tweepy
import pymongo
import pandas as pd
from tweepy import OAuthHandler
from tweepy import API
import json
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import networkx as nx
import twitter_api_keys as keys


def main():
    consumer_key = keys.consumer_key
    consumer_secret = keys.consumer_secret
    access_token = keys.access_token
    access_secret = keys.access_secret

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    # api = API(auth)
    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # connect to the database
    client = pymongo.MongoClient('localhost', 27017)
    db = client['twitter_database']
    download_and_save_tweets(db, api, 'real_tweets', '@CNN')
    download_and_save_tweets(db, api, 'fake_tweets', '@breitbartnews')

    tweets_mode = 'real_tweets'
    category_dict = {'real_tweets': '@CNN', 'fake_tweets': 'breitbartnews'}
    id_dict = {'@CNN': 759251, 'breitbartnews': 457984599}

    # get a list with the n most retweeted tweets
    tweets_list = get_most_retweeted_tweets(db, collection_name=tweets_mode, n=20)

    # download all the possible retweets of the n most retweeted tweets and save them in seperate collections
    for t in tweets_list:
        collection = db[tweets_mode + str(t)]
        get_retweets_of_tweet(t, api, db, tweets_mode)

    # create a plot for every retweet
    for t in tweets_list:
        collection = db[tweets_mode + str(t)]
        plot_retweets_per_hour(t, db, tweets_mode)

    # find the relationship between the retweeters in every hop
    for t in tweets_list:
        collection = db[tweets_mode + str(t)]
        compute_hops(id_dict[category_dict[tweets_mode]], t, tweets_mode, db, api)

    # create a plot for every retweet
    for t in tweets_list:
        collection = db[tweets_mode + str(t)]
        plot_information_flow(t, tweets_mode, db)

    # graph the user network of every tweet
    for t in tweets_list:
        collection = db[tweets_mode + str(t)]
        create_graph_of_tweets(t, db, id_dict[category_dict[tweets_mode]])


# method that graphs the user network of a specific tweet
def create_graph_of_tweets(tweet_id, db, original_user_id):
    try:
        G = nx.Graph()
        G.add_node(original_user_id)
        hop_counter = 1
        #iterate all the hop_collections and retrieve the total number of distinct users in each
        while True:
            print(str(db.command('collStats', tweet_id + '_hop_' + str(hop_counter))['count']))
            collection = db[tweet_id + '_hop_' + str(hop_counter)]
            print('hop'+str(hop_counter)+' has '+str(collection.count())+' total friendships checked with '+str(collection.find({'relationship': True}).count())+' of them positive')
            for doc in collection.find({'relationship': True}):
                G.add_node(str(doc['user_id_1']))
                G.add_edge(str(doc['user_id_1']), str(doc['user_id_2']))
            hop_counter = hop_counter + 1
    except (AttributeError, pymongo.errors.OperationFailure):
        print('Creation of graph completed')
        print('The graph has '+str(G.number_of_nodes())+' nodes and '+str(G.number_of_edges())+' edges')
        plt.clf()
        nx.draw(G)
        nx.write_gexf(G, tweet_id+".gexf")
        plt.savefig(tweet_id+"_draw.png")
        '''
        plt.clf()
        nx.draw_circular(G)
        plt.savefig("draw_circular.png")
        plt.clf()
        nx.draw_spectral(G)
        plt.savefig("draw_spectral.png")
        '''


# method that plots the number of retweeters per hop
def plot_information_flow(tweet_id, collection_name, db):
    try:
        hop_counter = 1
        distinct_counter = set()
        x = []
        y = []
        my_xticks = []
        #iterate all the hop_collections and retrieve the total number of distinct users in each
        while True:
            distinct_counter.clear()
            print(str(db.command('collStats', tweet_id + '_hop_' + str(hop_counter))['count']))
            collection = db[tweet_id + '_hop_' + str(hop_counter)]
            for doc in collection.find({'relationship': True}):
                distinct_counter.add(doc['user_id_1'])
            x.append(hop_counter)
            print('hop'+str(hop_counter)+' '+str(len(distinct_counter)))
            y.append(len(distinct_counter))
            my_xticks.append('Hop_'+str(hop_counter))
            hop_counter = hop_counter + 1
    except (AttributeError, pymongo.errors.OperationFailure):
        print('This operation is over')
        plt.xticks(x, my_xticks)
        plt.plot(x, y)
        plt.show()
        plt.savefig('results_per_retweet/'+str(collection_name)+'/'+str(tweet_id)+'.png')


# returns if two users have a relationship in twitter. This is true if either of them follows them other
def search_for_relationship_in_collection(collection, user_id_1, user_id_2):
    x = collection.find_one({'$and': [{'user_id_1': str(user_id_1)}, {'user_id_2': str(user_id_2)}]}, {'relationship': '1'})
    result = 0
    if x is None:
        result = 2
    elif x['relationship']:
        result = 1
    else:
        result = 0
    return result


# computes the relationship between the retweeters in every hop
def compute_hops(starting_user_id, tweet_id, col_name, db, api):
    collection = db[col_name+str(tweet_id)]
    # get the last 180 retweets. Because of the way the api returns them these retweets are also the oldest in
    #  the collection
    if(collection.count()<180):
        data = pd.DataFrame(list(collection.find()))
    else:
        data = pd.DataFrame(list(collection.find().skip(collection.count() - 180)))
    friends_list = []
    temp_friends_list = []
    rest_list = []
    temp_rest_list = []

    friends_list.append(starting_user_id)

    for i in data['user']:
        rest_list.append(i['id'])

    hop_counter = 0
    while len(friends_list) != 0 and len(rest_list) != 0:
        friendship_comp_counter = 0
        hop_counter = hop_counter + 1
        print('calculating hop: ' + str(hop_counter)+' for tweet '+str(tweet_id))
        hop_collection = db[str(tweet_id)+'_hop_'+str(hop_counter)]
        for ru in rest_list:
            lonely_user = True
            for fr in friends_list:
                friendship_comp_counter = friendship_comp_counter + 1
                collection_result = search_for_relationship_in_collection(hop_collection, ru, fr)
                print(str(friendship_comp_counter)+') source_id='+str(ru)+' | target_id='+str(fr)+' the result is '+str(collection_result))
                if collection_result == 2:
                    friendship = api.show_friendship(source_id=ru, target_id=fr)
                    if friendship[0].following or friendship[0].followed_by:
                        lonely_user = False
                        result = True
                        if ru not in temp_friends_list:
                            temp_friends_list.append(ru)
                    else:
                        result = False
                    json_obj = {
                        'user_id_1': str(ru),
                        'user_id_2': str(fr),
                        'relationship': result
                    }
                    hop_collection.insert(json_obj)
                elif collection_result == 1:
                    lonely_user = False
                    if ru not in temp_friends_list:
                        temp_friends_list.append(ru)
            if lonely_user:
                temp_rest_list.append(ru)

        friends_list = list(temp_friends_list)
        print('The friends list has:')
        print(friends_list)
        temp_friends_list.clear()
        rest_list = list(temp_rest_list)
        print('The rest list has:')
        print(rest_list)
        temp_rest_list.clear()
        print('The size of the friends list is '+str(len(friends_list)))
        print(str(friendship_comp_counter)+' friendships comparisons calculated')
    if len(rest_list) != 0:
        lonely_collection = db[str(tweet_id) + 'lonely']
        for u in rest_list:
            json_obj = {
                'user_id': u,
            }
            lonely_collection.insert(json_obj)


# method that plots the number of retweets of a tweet per hour
def plot_retweets_per_hour(tweet_id, db, collection_name):
    collection = db[collection_name+str(tweet_id)]
    data = pd.DataFrame(list(collection.find()))
    # converting the created_at field which is of string type to datetime
    dates = []
    for row in data['created_at']:
        dates.append(datetime.strptime(row, "%a %b %d %H:%M:%S +0000 %Y"))
    data['date'] = dates
    dates.clear()
    # create a new field that holds only the date and hour. This way we can group by this new field and get the total
    #  count of retweets per hour
    for row in data['date']:
        dates.append(datetime.strptime(str(row.year) + "-" + str(row.month) + "-" + str(row.day) + " " + str(row.hour)
                                       , '%Y-%m-%d %H'))
    data['custom_date'] = dates
    plot_data = data.groupby('custom_date')['custom_date'].apply(lambda x: x.count())
    y = plot_data.tolist()
    x = []
    for index, t in plot_data.items():
        x.append(index)
    # plot the data
    plt.plot(x, y)
    plt.gcf().autofmt_xdate()
    print(str(tweet_id))
    plt.savefig('results_per_retweet/'+str(collection_name)+'/'+str(tweet_id)+'.png')


# method that converts the mongodb collection to a dataframe, sorts the dataframe based on the retweet_count attribute,
# takes the n tweets with the biggest value and returs their ids in a list
def get_most_retweeted_tweets(db, collection_name='real_tweets', n='20'):
    collection = db[collection_name]
    data = pd.DataFrame(list(collection.find()))
    # return a series of the three
    l = data['retweet_count'].sort_values(ascending=False).head(n).index.tolist()
    print("These are the three most retweeted tweets in the collection")
    print(" ")
    tweets_list = list()
    for tweet_dataframe_id in l:
        # you can restrict the output to contain only original tweets and not retweets
        #if not pd.isnull(data.loc[tweet_dataframe_id].retweeted_status):
        tweets_list.append(data.loc[tweet_dataframe_id].id_str)
        print(data.loc[tweet_dataframe_id])
        print('========================================================')
    return tweets_list


# method that collects all the retweets of a tweet, 100 at a time because of the twitter api limits and stores them
# in a new collection
def get_retweets_of_tweet(tweet_id , api, db, collection_name):
    collection_name = collection_name + str(tweet_id)
    collection = db[collection_name]
    page = 0
    while True:
        retweets = api.retweets(id=int(tweet_id), page=page, count=100)
        if retweets:
            for rt in retweets:
                jsoned_data = json.dumps(rt._json)
                rtweet = json.loads(jsoned_data)
                collection.insert(rtweet)
        else:
            break
        print("retweets_size: "+str(len(retweets)))
        print("page: "+str(page))
        print(" ")
        page += 1


# method for downloading tweets from a twitter user and storing them in a mongodb collection
def download_and_save_tweets(db, api, collection_name, user_name):
    real_collection = db[collection_name]
    get_tweets_from_user(api, user_name, real_collection)


# method that user tweepy to take all the tweets of a twitter user. Then it iterates all the tweets and stores their
# json file in a mongodb collection
def get_tweets_from_user(api, users_name, collection):
    item = api.get_user(users_name)
    print(item.name)
    print(item.description)
    # take all the tweets and iterate over them
    tweets = tweepy.Cursor(api.user_timeline, screen_name=users_name).items()
    while True:
        try:
            data = tweets.next()
        except StopIteration:
            break
        # extract the json
        jsoned_data = json.dumps(data._json)
        tweet = json.loads(jsoned_data)
        # insert the json in the collection
        collection.insert(tweet)
