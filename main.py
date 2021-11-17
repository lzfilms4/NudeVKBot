import time
import shutil
from keras.backend import batch_dot
import requests
from keras.models import load_model
from tensorflow.keras.preprocessing import image_dataset_from_directory
from myconfig import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

bad = 0
good = 0

def isMine():
    if len(driver.find_elements_by_id('pv_delete')):
        return True
    else:
        print('Фото не моё. Пропускаем')
        return False

def deletePhoto(r):
    global bad
    global good
    if r:
        shutil.copy(r'./photo/class_a/img.jpg', r'./classification/bad/file'+str(bad) +'.jpg')
        bad += 1
        print("Плохо")
        driver.find_element_by_id('pv_delete').click()
        time.sleep(1)
        print("Фото удалено")
    else:
        shutil.copy(r'./photo/class_a/img.jpg', r'./classification/good/file'+str(good) +'.jpg')
        good += 1
        print("Хорошо")

def checkNude():
    print("Проверяю фото...")
    imgs = image_dataset_from_directory('photo', image_size=(img_height, img_width))
    res = model.predict(imgs)[0]
    r = True if res[0] > res[1] else False #  True - плохая картинка, False - хорошая
    deletePhoto(r)
    return r

def getCountPhoto():
    count = driver.find_element_by_class_name('pv_counter').text
    print('----------------------COUNT------------------------------')
    count = count.split(' ')
    count = count[2]
    return int(count)

def getPhoto(i = -1, count = -1):
    print("Качаю фото ", (i+1) , " из ", count)
    src = driver.find_element_by_xpath('//*[@id="pv_photo"]/img').get_attribute('src')
    r = requests.get(src)
    out = open("./photo/class_a/img.jpg", "wb")
    out.write(r.content)
    out.close()
    time.sleep(1)
    print('Фото скачано')

def NextPhoto():
    # nextButton = driver.find_element_by_xpath('//*[@id="pv_nav_btn_right"]/div')
    # area = driver.find_element_by_class_name('pv_img_area_wrap')
    # hover = ActionChains(driver).move_to_element(area).move_to_element(nextButton)
    body = driver.find_element_by_tag_name("body")
    body.send_keys(Keys.ARROW_RIGHT)
    # driver.send_keys(Keys.ARROW_RIGHT)

def parseOneMessage():
    print('Парсим диалог')
    time.sleep(5)
    #Кликаю по вложениям
    opt = driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div[3]/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[1]')
    attachmens = driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div[3]/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/a[2]')
    hover = ActionChains(driver).move_to_element(opt).move_to_element(attachmens)
    hover.click().perform()
    
    time.sleep(5)
    #Смотрю на наличие фотографий во вложениях
    photo_container = driver.find_element_by_xpath('//*[@id="wk_history_rows"]/div')
    print('--------------------------------------------------------------')
    print(photo_container.find_elements_by_tag_name('a'))
    print('--------------------------------------------------------------')
    first_photo = photo_container.find_elements_by_class_name('photos_row')[0]
    first_photo.click()
    count = getCountPhoto()
    for i in range(count-1):
        if isMine():
            getPhoto(i, count)
            time.sleep(1)
            checkNude()
            time.sleep(1)
        NextPhoto()
        time.sleep(1)
    getPhoto(count, count)
    time.sleep(1)
    #Проверили все фото
    close_btn = driver.find_element_by_class_name('pv_close_btn')
    close_btn.click()
    time.sleep(3)
    back_btn = driver.find_element_by_class_name('im-page--back-btn')
    back_btn.click()
    time.sleep(3)

    # if len(driver.find_elements_by_id('wk_history_empty')): #Если список фото не пустой
    #     first_photo = photo_container.find_elements_by_class_name('photos_row_wrap')[0]
    #     print(first_photo.find_elements_by_tag_name('a'))
    #     if len(driver.find_elements_by_id('pv_delete')): #Моя ли это фотография
    #         print('yes')
    close_button = driver.find_element_by_xpath('//*[@id="wk_history_wrap"]/div[1]/div[2]')
    close_button.click()
    time.sleep(10000)

def ScrollMessages():
    SCROLL_PAUSE_TIME = 0.5
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def start_sel():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    global driver 
    driver = webdriver.Chrome('.\Chromedriver\chromedriver.exe', chrome_options=chrome_options)
    driver.get("https://vk.com/")
    time.sleep(10) #Загрузка страниц
    login = driver.find_element_by_xpath('//*[@id="index_email"]')
    login.clear()
    login.send_keys(MYLOGIN)
    password = driver.find_element_by_xpath('//*[@id="index_pass"]')
    password.clear()
    password.send_keys(MYPASSWORD)
    time.sleep(5)
    button = driver.find_element_by_xpath('//*[@id="index_login_button"]')
    button.click()
    time.sleep(20) # Время для решения капчи
    #Вошли в аккаунт
    message_button = driver.find_element_by_xpath('//*[@id="l_msg"]/a/span[1]')
    message_button.click()
    #Зашли в сообщение
    time.sleep(5)
    ScrollMessages()
    #Пролистали все сообщения
    time.sleep(10)
    messages_ul = driver.find_element_by_xpath('//*[@id="im_dialogs"]')
    messages_list = messages_ul.find_elements_by_tag_name("li") # Список из объектов сообщений
    # print(len(messages_list))
    for i in messages_list:
        # checkBox=WebDriverWait(driver,10).until(EC.element_to_be_clickable(i))
        # ActionChains(driver).move_to_element(checkBox).click(checkBox).perform()
        driver.implicitly_wait(10)
        ActionChains(driver).move_to_element(i).click(i).perform()
        time.sleep(3)
        #Готово
        parseOneMessage()
    time.sleep(2000) #Загрузка страниц
    driver.close()
    driver.quit()

def connect_model():
    global model
    model = load_model('99Conv.h5')
    global img_height
    img_height = 200
    global img_width
    img_width = 200

connect_model()
start_sel()