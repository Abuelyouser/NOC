from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time




driver = webdriver.Chrome(ChromeDriverManager().install())

driver.get("https://www.techwithtim.net/")

search = driver.find_element(By.NAME, 's')
search.send_keys("test")
search.send_keys(Keys.RETURN)

time.sleep(5)


"""
we can find links in a page by its name >>
link = driver.find_element_by_link_text("Python Programming")

but we need to make sure the element if exist or not by using try and except..

introduce acrion chains a set of actions that can be done like clicks for example .. after making these actions we have to call 

driver.implicity_wait(5)
//code   this code does not run util it waits a 5 sec if it exist
"""
