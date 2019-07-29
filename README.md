# Information diffusion of fake and real news retweets on Twitter

This is a python project that studies the differences in information diffusion of real and fake retweets. 
## Methodology

### Data Collection

For the data collection we used two different twitter accounts to represent and source of fake news (@Braitbartnews) as well as a source of real news (@CNN). Data from the real news source were collected during March of 2018 (13/3/2018 - 31/3/2018) while 
data from the fake news account during February and March of the same year (19/2/2018-31/2/2018). Communication with Twitter's API we performed using the [tweepy library](https://www.tweepy.org/).


To study the diffusion of false and real news information on Twitter, from each set of data, we analyzed the diffusion of retweets as it is the most powerful mechanism for spreading information on this platform.

The volume of data for each news category is about the same (3,231 for real news and 3,238 for fake news) and sufficient so that a good number of retweets cloud be extracted for each case). Twitter's api sets an upper limit of the tweets that someone 
can retrieve from a user's account to 3200, hence tweepy would not be able to give more that that 

Then, from each category, the three most retweeted tweets were found, while for each of them, due to time constraints, only the 180 most recent chronologically retweets were used for further analysis of information diffusion. All the data collected from twitter 
were stored in MongoDB collections. In the case of our two twitter accounts, we observed that real news tweets were retweeted much more that the fake ones.

Summary of the 3 most retweeted fake news tweets 

|  | Original Tweet ID | Retweet Count | #RT collected | #RT in our analysis | Date | 
| --- | :---: | :---: | :---: | :---: | :---: |
| `F- MRT1` | 128 | 4,811 | 3,012 | 180 | 23/2/2018 | 
| `F- MRT2` | 785 | 4,446 | 3,019 | 180 | 31/2/2018 | 
| `F- MRT3` | 777 | 3,807 | 360 | 180 |  19/2/2018 | 

Summary of the 3 most retweeted real news tweets 

|  | Original Tweet ID | Retweet Count | #RT collected | #RT in our analysis | Date | 
| --- | :---: | :---: | :---: | :---: | :---: | 
| `R- MRT1` | 888 | 48,857 | 2,776 | 180 | 13/3/2018 | 
| `R- MRT2` | 056 | 21,916 | 2,853 | 180 | 31/3/2018 | 
| `R- MRT3` | 597 | 20,104 | 2,861 | 180 |  19/3/2018 | 


## Results

### Diffusion of information over time

The retweets of every tweet we studied were grouped using the 'created_at' attribute and then sorted based on the date of creation. This info was then used to create plots of the retweet count of every tweet over time (specifically per hour)


![alt text](https://github.com/diliadis/twitter_info_diffusion/blob/master/results_per_retweet/summary/Screen%20Shot%202019-07-29%20at%201.19.04%20PM.png)

We observe that in the case of real news tweets the information diffusion shots up in the first hours of their creation but it crearly plummets from the first day.  
On average, the maximum number of retweets displayed in the first hours of a tweet's creation in our set of data is in the range of 300 retweets. In the next period of 10-15 days the rate of diffusion is significantly reduced.

On the other hand, in the case of fake news tweets of our dataset the rate is very similar with that of the real news tweets but their life cycle is clearly shorter (after 10 days the tweets stops being retweeted). 

### Diffusion of information in depth

To study the depth of information diffusion in the network of users, we first had to find the users that had a relationship (followed or being followed) with the initial user (in our case @CNN or @Braitbartnews). The set of users
that met this condition were classified in the first hop. Each user that did not met the aforementioned condition was then tested for possible relationships with users that were classified in the first hop. Again, the set of users that met this condition were classified in the second hop.

This procedure was repeated until there was no user that did not belonged in a hop or until the remaining users didn't have a relationship with other users in the network. 
These isolated users were removed and ignored as they probably received the information from users outside from the dataset that we collected and used.
The computation of the users per hop was especially resource intensive because Twitter's api only allows 450 requests per 15 minutes. These computations took hours with the majority of that time being spent just waiting for the 15 minute 
to be over. For example in the second hop of every tweet we had to check thousands of relationships (5984 friendship calls for one hop of one tweet took over 3 hours!!!)

Results of user's relationships per hop

|            |       | #friendships checked | #true friend ships | Nodes | Edges | Isolated  | 
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| R- MRT9736 | Hop 1 | 180 | 44 |  |  | | 
|            | Hop 2 | 5984 | 3 |  |  | |
|            | Hop 3 | 399 | 1 |  |  | |
|            | Hop 4 | 132 | 0 | 49 | 48 |132 |
| R- MRT9739 | Hop 1 | 180 | 54 |  |   | | 
|            | Hop 2 | 6804 | 1 |  |   | | 
|            | Hop 3 | 125 | 0 | 56 | 55 | 125 | 
| R- MRT9772 | Hop 1 | 180 | 25 |  |   | | 
|            | Hop 2 | 3875 | 0 | 26 | 25  | 155 | 


|            |       | #friendships checked | #true friend ships | Nodes | Edges | Isolated  | 
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| F- MRT9671 | Hop 1 | 180 | 111 |  |  | | 
|            | Hop 2 | 7659 | 58 |  |  | |
|            | Hop 3 | 848 | 1 |  |  | |
|            | Hop 4 | 52 | 0 | 129 | 170 |52 |
| F- MRT9758 | Hop 1 | 180 | 134 |  |   | | 
|            | Hop 2 | 6164 | 72 |  |   | | 
|            | Hop 3 | 513 | 0 | 154 | 86 | 27 | 
| F- MRT9801 | Hop 1 | 180 | 134 |  |   | | 
|            | Hop 2 | 6164 | 52 |  |   |  | 
|            | Hop 2 | 493 | 0 | 152 | 186  | 22 


plots of users per hop 

![alt text](https://github.com/diliadis/twitter_info_diffusion/blob/master/results_per_retweet/summary/Screen%20Shot%202019-07-29%20at%201.19.04%20PM.png)| 


No significant differences were found in user counts per hop and in the level of diffusion of information between the two categories of news. In the case of fake news the number of hops
was more stable since they are consistently higher than 2 in each of the most retweeted posts that were used for analysis.


In both cases, the majority of users receive the information from the starting node, which is located at the first level - hop, while as we go deeper into the network, the number of users per hop reduces significantly, especially between the first and second level.

We also used the networkx library to produce graphs of the user networks

User etwork graphs of real news tweets