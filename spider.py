from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
import pymongo
import time
from config import *



#开启浏览器
browser = webdriver.Chrome()
wait = WebDriverWait(browser,TIME)
#设置窗口大小
browser.set_window_size(1400,900)

#爬取歌单歌曲
def find_music():

    #获取网页
    browser.get('https://music.163.com/')

    #点击歌单
    submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#g_nav2 > div > ul > li:nth-child(3) > a > em")))

    submit.click()

    #获取一页歌单
    get_songlists()



#获取一页歌单
def get_songlists(count=0):


    #进入iframe框架
    browser.switch_to.frame('g_iframe')
    #定位
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#m-pl-container > li:nth-child(1) > div > div > span.nb')))


    #解析网页
    html = browser.page_source
    #print(html)

    #正则获取歌单名和歌单链接
    #rule = '<a title="(.*?)".*?href="(.*?)".*?class="msk">'
    rule = '<a title="(.*?)".*?class="msk">'
    reObj = re.compile(rule)

    content = re.findall(reObj,html)
    #print(len(content))

    if count<len(content):
        #歌单名

        songlist_name = content[count]
        print(songlist_name)
        #记录歌单顺序
        count += 1
        # 爬取歌曲

        turn_to_songlist(songlist_name,count)










def turn_to_songlist(songlist_name,count):

    '''
    这个方法有时无效
    ----------------------------------------------------------
    target = browser.find_elements_by_link_text(songlist_name)
    browser.execute_script("arguments[0].scrollintoView;", target)
    ---------------------------------------------------------------
    '''
    #滚动条滚动到底部，使其能定位元素
    js = "window.scrollTo(0,document.body.scrollHeight)"
    browser.execute_script(js)

    #歌单名预处理
    '''
    --------------------------------------------------------------------------------------------
           歌单名有时是包含噪声的，如『俏皮实验室』响指&amp;口哨的清新节奏，原本的名字不包含「amp;」
           需要进行数据预处理。
    --------------------------------------------------------------------------------------------
    '''
    #预处理1：浏览器传送的特殊符号

    rule1 = '(amp;)|(&quot;)'
    reg1 = re.compile(rule1)
    title1 = re.sub(reg1,'',songlist_name)
    #预处理2：特殊字符与非特殊字符
    rule_title = '(\w+)'
    reg = re.compile(rule_title)
    title = re.findall(reg,title1)
    #print(title)
    max_length_title = title[0]
    title_length = len(title)
    for i in range(1,title_length):
        if len(title[i])>len(max_length_title):
            max_length_title = title[i]
    print(max_length_title)

    #点击某一歌单
    #-------------------------------------------------------------------------------------------------------
    # partial_link_text 只能对text的连续字串起作用。
    # 如  “我爱你”的100种表达方式，（的100种表达方式）可以识别，但是（我爱你的100种表达方式）不可以识别
    #-------------------------------------------------------------------------------------------------------
    submit = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT,max_length_title)))

    submit.click()

    #进入iframe框架
    browser.switch_to.parent_frame()
    browser.switch_to.frame('contentFrame')
    # 解析网页
    html = browser.page_source
    #print(html)

    #滚动条滚动到底部，使其能定位元素
    js = "window.scrollTo(0,document.body.scrollHeight)"
    browser.execute_script(js)

    #爬取歌单歌曲
    #歌单名
    songlist_name = songlist_name


    #创建歌单者
    rule = '<a.*?class="s-fc7">(.*?)</a>'
    reObj = re.compile(rule)
    content = re.findall(reObj, html)
    #评论者也符合这个规则
    songlist_author = content[0]
    #print(songlist_author)

    #歌单标签
    rule = '<a class="u-tag".*?>.*?<i>(.*?)</i>'
    reObj = re.compile(rule)
    songlist_tag = re.findall(reObj, html)
    #print(songlist_tag)

    # 歌单介绍
    #判断是否有介绍
    try:
        #定位 介绍
        production = browser.find_element_by_id('album-desc-more')

    except:
        #没有定位到“介绍”
        print('此歌单无介绍')
    else:
        #定位到了“介绍”

        try:
            # 判断元素是否存在
            element = browser.find_element_by_link_text('展开').is_displayed()
        except:
            # 介绍过短，不需要展开
            songlist_production = production.text
            # print(songlist_production)

        else:
            # 需要展开
            submit = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, '展开')))
            submit.click()
            time.sleep(2)

            songlist_production = production.text
            # print(songlist_production)







    #歌单歌曲数
    songlist_number = browser.find_element_by_xpath('//*[@id="playlist-track-count"]').text
    #print(songlist_number)

    #歌单播放数
    songlist_vistor = browser.find_element_by_css_selector('#play-count').text
    #print(songlist_vistor)





    #歌单歌曲信息
    #歌曲部分信息
    songs = []
    element = browser.find_elements_by_xpath('//tr/td[3]/div/span[2]')
    for i in element:
        #歌曲名
        song_name = i.get_attribute('data-res-name')
        #歌手
        song_author = i.get_attribute('data-res-author')
        #歌曲图片
        song_pic = i.get_attribute('data-res-pic')

        song = [song_name,song_author,song_pic]
        songs.append(song)
    #print(songs)

    #歌曲部分信息
    songs1 = []
    element1 = browser.find_elements_by_xpath('//tr/td[3]/span')
    for i in element1:
        song_duration = i.text
        songs1.append(song_duration)
    #print(songs1)

    #歌曲信息合并
    for i in range(len(songs)):
        songs[i].append(songs1[i])
    print(songs)

    browser.switch_to.parent_frame()
    browser.back()
    get_songlists(count)





def main():
    try:
        find_music()
    except:
        pass
    finally:
        browser.close()

if __name__=="__main__":
    main()
