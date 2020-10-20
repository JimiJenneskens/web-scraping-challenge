from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime as dt
import time
import re

def scrape_all():
    "Call all other functions"

    # Initiate headless driver for deployment
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path)
    news_title, news_paragraph = mars_news(browser)
    

    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "main_image": featured_image(browser),
        "hemispheres": scrape_hemi(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
        }
    browser.quit()
    return data

def mars_news(browser):
    "Scrape Mars News"

    # make the url
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    # make beautiful soup
    html = browser.html
    soup = bs(html, 'html.parser')

    # get the title
    slide = soup.select_one("ul.item_list li.slide")
    news_title = slide.find('div', class_="content_title").get_text()

    # get the paragraph
    news_paragraph = soup.find('div', class_="article_teaser_body").get_text()

    return news_title, news_paragraph

def featured_image(browser):
    "JPL Mars Space Images"

    # make the url
    url="https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    # find and click the full image
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # find and click the more info
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # find the main image
    soup = bs(browser.html, 'html.parser')
    main_image = soup.body.find('img', class_="main_image")
    image_address = main_image['src']
    image = f'https://www.jpl.nasa.gov{image_address}'
    return image

def twitter_weather(browser):
    "Mars Weather"
    
    # make the url
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)
    while True:
        if not browser.is_element_not_present_by_tag('article'):
            break
    twit_html = browser.html
    soup = bs(twit_html, 'html.parser')
    tweets = soup.find('article')
    
    for tweet in tweets:
        spans = tweet.find_all("span")
        mars_weather = spans[4].get_text()
        #Replacing all paragraph breaks
        # weather = weather.replace('\n', " ")
        return mars_weather

def mars_facts():
    "Mars Facts"

    # make the URl
    url = "https://space-facts.com/mars/"

    mars_table = pd.read_html(url)
    final_table = mars_table[0]
    final_table = final_table.rename(columns={0:'Characteristic', 1: "Value"})

    return final_table.to_html(header=True, index=True)

def scrape_hemi(browser):
    "Collect Hemispheres"

    hemispheres = ['Cerberus Hemisphere Enhanced','Schiaparelli Hemisphere Enhanced','Syrtis Major Hemisphere Enhanced','Valles Marineris Hemisphere Enhanced']
    hemispheres_url = []

    for info in hemispheres: 
        url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
        browser.visit(url)
        browser.is_element_present_by_text(info, wait_time=1)
        more_info = browser.find_link_by_partial_text(info)
        more_info.click()
        full_image = browser.find_by_id('wide-image-toggle')
        full_image.click()
        soup =bs (browser.html, 'html.parser')
        wide_image = soup.body.find('img', class_='wide-image')
        image_src = wide_image['src']
        image_url = f"https://astrogeology.usgs.gov{image_src}"
        hemispheres_url.append(image_url) 

    hemisphere_image_urls = [
    {"title": "Valles Marineris Hemisphere", "img_url": hemispheres_url[0]},
    {"title": "Cerberus Hemisphere", "img_url":hemispheres_url[1]},
    {"title": "Schiaparelli Hemisphere", "img_url": hemispheres_url[2]},
    {"title": "Syrtis Major Hemisphere", "img_url": hemispheres_url[3]},]
    return hemisphere_image_urls

if __name__ == "__main__":
    print(scrape_all())
