
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import pandas as pd
import time
from datetime import datetime
import nltk
import selenium


# In[2]:


HOME = "https://www.youtube.com/user/theneedledrop/videos"


# In[3]:


def get_score(url):
    """
    get_score obtains the score and date of an Anthony Fantano review
    
    url - Str
    
    returns int
    """
    result = requests.get(url)
    c = result.content

    soup = BeautifulSoup(c)

    date = soup.find("strong", {"class": "watch-time-text"}).text
    date = datetime.strptime(date, 'Published on %b %d, %Y')
    
    child = str(soup.find("div", {"id": "watch-description-text"}))
    
    #tknizer = nltk.tokenize.ToktokTokenizer()

    #tokenized = tknizer.tokenize(child)
    tokenized = nltk.tokenize.casual_tokenize(child)

    str_score = ''
    
    for i, token in enumerate(tokenized):
        if "/10" == token:
            str_score = tokenized[i-1]
            ind = i
            break
        elif ("10" == token and '/' == tokenized[i-1]):
            str_score = tokenized[i-2]
            break
        elif ("10" == token and '/' in tokenized[i-1]):
            str_score = tokenized[i-1].split("/")[0]
            break
        elif "/10" in str(token) and len(token) < 10:
            str_score = tokenized[i].split("/")[0]
            ind = i
            break

    if str_score == '':
        score = None
    else:        
        if str_score.isdigit():
            score = int(str_score)
        else:
            score = str_score
    
    appending_fave = False
    appending_lfave = False
    fave_tracks = []
    lfave_track = []

    for i, token in enumerate(tokenized):
        if appending_fave:
            if token == '<br/>' or token == '<p/>':
                appending_fave = False
            else:
                fave_tracks.append(token)
                
        if appending_lfave:
            if token == '<br/>' or token == '<p/>':
                appending_lfave = False
                break
            else:
                lfave_track.append(token)
        
        if tokenized[i-1] == "TRACKS" and token == ":":
            appending_fave = True
        
        if tokenized[i-1] == "TRACK":
            appending_lfave = True
    
    
    if fave_tracks != []: 
        fave_tracks = ' '.join(fave_tracks)
        fave_tracks = fave_tracks.split(", ")
    else:
        fave_tracks = []
    if lfave_track != []:
        lfave_track = ' '.join(lfave_track)
    else:
        lfave_track = ''
    return score, date, fave_tracks, lfave_track


# In[4]:


def scroll():
    """
    scrolls to the bottom of the page
    
    code taken from https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
    modified slightly for YouTube
    """
    
    SCROLL_PAUSE_TIME = 0.5
    
    last_height = driver.execute_script("return window.scrollY")    
    
    tries = 0
    while True:
        down_height = last_height + 1000
        driver.execute_script("window.scrollTo(0," + str(down_height)  + ")")
        
        time.sleep(SCROLL_PAUSE_TIME)
        
        new_height = driver.execute_script("return window.scrollY")
        if new_height == last_height:
            tries += 1
            if tries == 10:
                break
        else:
            tries = 0
        last_height = new_height


# In[7]:


def scroll_update(latest_review_url):
    """
    scrolls to the point where the dataset was last updated
    
    code taken from https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
    modified slightly for YouTube
    """
    
    SCROLL_PAUSE_TIME = 0.5
    
    last_height = driver.execute_script("return window.scrollY")    
    tries = 0
    while True:
        down_height = last_height + 1000
        driver.execute_script("window.scrollTo(0," + str(down_height)  + ")")
        
        time.sleep(SCROLL_PAUSE_TIME)
        
        new_height = driver.execute_script("return window.scrollY")
        if new_height == last_height:
            tries += 1
            if tries == 10:
                break
        elif latest_review_url in driver.page_source:
            break
        else:
            tries = 0
        last_height = new_height


# In[99]:


def get_title_artist(title_element):
    """
    get_title_artist takes a title element and extracts the artist of the album an
    the title of the album
    """    
    
    
    title_token = title_element.text.split(" ")

    word = title_token.pop(0)
    artist = ''
    title = ''
    first = True
    while(title_token != [] and word != '-' and word[-1] != '-'):
        if first:
            first = False
            artist += (word)
        else:
            artist += ' '
            artist += word

        word = title_token.pop(0)
    
    if word[-1] == '-':
        word = word[:-1]
        artist += word
        
    if title_token == []:
        print("ERROR HERE: ", title_element.text)
        return None, None
    
    word = title_token.pop(0)
    first = True

    while(True):
        if first:
            first = False
            title += word
        else:
            title += ' '
            title += word
        if title_token != []:
            word = title_token.pop(0)
            if word == "ALBUM" or (word == "EP" and title_token[0] == "REVIEW"):
                break
        else:
            break
    return title, artist


# In[62]:


def get_captions(link, driver):
    """ Gets the youtube auto-generated captions to a link
    """
    caption_link = 'http://www.diycaptions.com/php/start.php?id='
    
    key = link.split("=")[1]
    driver.get(caption_link + key)
    caption = ''
    i = 0
    time.sleep(4)
    while(True):
        i += 1
        try:
            text = driver.find_element_by_id(str(i)).text
        except selenium.common.exceptions.NoSuchElementException:
            return caption
        caption += text + ' '  
    all_captions.append({'url': link, 'caption': caption})


# ## fantano_reviews scrapers

# In[ ]:


#run to scrape fantano_reviews.csv from beginning

driver = webdriver.Chrome()

driver.get(HOME)

scroll()

element_titles = driver.find_elements_by_id("video-title")

#regular scraper
list_of_rows = []
i = 0
for e in element_titles:
    title = e.text
    if "ALBUM REVIEW" in title:
        review_type = "Album"
    elif "EP REVIEW" in title:
        review_type = "EP"
    else:
        continue
        
    i += 1
    link = e.get_attribute("href")
    score, review_date, best_tracks, worst_track = get_score(link)
    
    if isinstance(score, str):
        word_score = score
        score = None
    else:
        word_score = None
    
    title, artist = get_title_artist(e)

    if title == None:
        continue
    
    row_dict = {"title": title, "artist": artist,
                "score": score, "word_score": word_score,
                "link": str(link), "review_type": review_type,
                "review_date": review_date, "best_tracks": best_tracks,
                "worst_track": worst_track}
    if i % 10 == 0:
        print("\n\n", str(i), "th Review\n")
        print("row: ", row_dict)

    list_of_rows.append(row_dict)

df = pd.DataFrame(list_of_rows)
cols = ['title', 'artist', 'review_date', 'review_type', 'score', 'word_score', 'best_tracks', 'worst_track', 'link']
df = df[cols]
df.to_csv("fantano_reviews.csv")


# In[ ]:


#run to scrape fantano_reviews.csv from last_updated

pd.read_csv("fantano_reviews.csv")
driver = webdriver.Chrome()

driver.get(HOME)

scroll_update()

element_titles = driver.find_elements_by_id("video-title")

#regular scraper
list_of_rows = []
i = 0
for e in element_titles:
    title = e.text
    if "ALBUM REVIEW" in title:
        review_type = "Album"
    elif "EP REVIEW" in title:
        review_type = "EP"
    else:
        continue
        
    i += 1
    link = e.get_attribute("href")
    score, review_date, best_tracks, worst_track = get_score(link)
    
    if isinstance(score, str):
        word_score = score
        score = None
    else:
        word_score = None
    
    title, artist = get_title_artist(e)

    if title == None:
        continue
    
    row_dict = {"title": title, "artist": artist,
                "score": score, "word_score": word_score,
                "link": str(link), "review_type": review_type,
                "review_date": review_date, "best_tracks": best_tracks,
                "worst_track": worst_track}
    if i % 10 == 0:
        print("\n\n", str(i), "th Review\n")
        print("row: ", row_dict)

    list_of_rows.append(row_dict)

df = pd.DataFrame(list_of_rows)
cols = ['title', 'artist', 'review_date', 'review_type', 'score', 'word_score', 'best_tracks', 'worst_track', 'link']
df = df[cols]
df.to_csv("anthony_fantano.csv")


# ## captions.csv scraper

# In[65]:


# run to scrape
all_captions = []
for i, link in enumerate(links):
    caption = get_captions(link, driver)
    all_captions.append({'url': link, 'caption': caption})
    if i % 100 == 0:
        print(i)
caption_df = pd.DataFrame(all_captions)
caption_df.to_csv('captions.csv')


# In[32]:


df = pd.read_csv("anthony_fantano.csv", encoding='latin-1')


# In[33]:


df = df.iloc[:, 1:]


# In[54]:


links = df['link'].tolist()


# In[39]:


links


# In[47]:


pd.DataFrame(all_captions)


# In[59]:


driver1 = webdriver.Chrome()
driver2 = webdriver.Chrome()
driver3 = webdriver.Chrome()


# In[66]:


len(links)


# In[67]:


caption_df


# In[4]:


captions_df = pd.read_csv('captions.csv', encoding='latin-1')


# In[8]:


captions_df.iloc[105,1]


# In[ ]:


all_captions = []

while(links != []):
    


# In[298]:


from matplotlib import pyplot as plt


# In[302]:


plt.plot(df.review_date,df.score)
plt.show()


# In[303]:


df[df['score'] > 10]


# In[258]:


soup = BeautifulSoup(requests.get('https://www.youtube.com/watch?v=tLWPSqE0DC4').content)


# In[264]:


soup.prettify


# In[266]:


soup.find("strong", {"class": "watch-time-text"}).text


# In[94]:


r = requests.get("http://video.google.com/timedtext?lang=en&v=toQEov2nWas")


# In[95]:


r.content

