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


![alt text](https://github.com/diliadis/flight_radar/blob/master/images/15_5_2018_node_size_in_degree_node_color_in_degree.png)