from selenium import webdriver
from time import sleep

class hero:
    def __init__(self):
        driver = webdriver.Chrome()
        driver.get("http://lol.qq.com/web201310/info-heros.shtml")
        html = driver.find_elements_by_xpath("//ul[@id='jSearchHeroDiv']/li/a")
        i=0
        while i<len(html):
            yx=html[i]
            title = yx.get_attribute("title")
            print(title)
            yx.click()
            sleep(10)
            ht = driver.page_source
            ht = driver.find_element_by_id("DATAlore")
            print(ht)
            print(driver.current_url)
            i+=1
            driver.get("http://lol.qq.com/web201310/info-heros.shtml")
            html = driver.find_elements_by_xpath("//ul[@id='jSearchHeroDiv']/li/a")


if __name__ == '__main__':
    hero()


