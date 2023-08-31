import shutil
import time
import pandas as pd
import requests
from tqdm import tqdm  # Used to see the progress of the loop
from bs4 import BeautifulSoup
from selenium import webdriver
import os

link = 'https://stockmages.netlify.app'  # link of the website we are using for this project
browser = webdriver.Chrome()
browser.get(link)

for i in tqdm(range(0, 500000, 1000)):  # Executing infinite scrolling
    browser.execute_script("window.scrollTo(0," + str(i) + ")")
    time.sleep(.1)

soup = BeautifulSoup(browser.page_source, 'html.parser')

data = []
for sp in tqdm(soup.find_all('div', class_='container')):
    img_link = sp.find('img').get('src')
    tags = sp.find('span', class_='tag-color').text[7:].strip()
    likes = int(sp.find('div', class_='likes-comments').find_all('span')[0].text.strip()[:-6])
    comments = int(sp.find('div', class_='likes-comments').find_all('span')[1].text.strip()[:-9])
    data.append([img_link, tags, likes, comments])

# Creating a dataframe and saving it
df = pd.DataFrame(data, columns=['img_link', 'tags', 'likes', 'comments'])
df.to_csv('images.csv', index=False)

# Remove unnecessary libraries
del df['likes']
del df['comments']

# TO find all tags
t = []
for tags in df['tags']:
    t += [tag.strip() for tag in tags.split(',')]
tags = list(set(t))

# Create folders for each tags
for tag in tqdm(tags):
    try:
        os.mkdir('Dataset/' + tag)
    except:
        pass

# Download images and save them in respective folders
for data in tqdm(df.values):
    img_link = data[0]
    tags = [tag.strip() for tag in data[1].split(',')]  # Use data[1] for tags
    for tag in tags:
        img_name = os.path.basename(img_link)
        img_path = os.path.join('Dataset', tag, img_name)  # Make sure to use 'Dataset' as the base path
        try:
            response = requests.get(img_link, stream=True)
            with open(img_path, 'wb') as file:
                shutil.copyfileobj(response.raw, file)
        except Exception as e:
            print(f"Error downloading image: {e}")


# Checking number of Images in Each Folder
folder_counts = {}
for folder in tqdm(os.listdir('Dataset')):
    try:
        folder_counts[folder] = len(os.listdir(os.path.join('Dataset', folder)))
    except:
        pass

# Removing images with less than 50 images
for folder, count in tqdm(folder_counts.items()):
    if count < 50:
        src = os.path.join('Dataset', folder)
        dst = os.path.join('Temp', folder)
        try:
            shutil.move(src, dst)
        except:
            pass

