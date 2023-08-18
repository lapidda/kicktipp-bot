import random
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from dotenv import load_dotenv


def calcMatch(home: str, away: str, quote: str):
    splitQuote = quote.split(' | ')
    qHome = float(splitQuote[0])
    qAway = float(splitQuote[2])
    qDraw = float(splitQuote[1])
    normFactor = min(qHome, qAway, qDraw)
    normHome = qHome / normFactor
    normAway = qAway / normFactor
    normDraw = qDraw / normFactor
    winProbability = normAway / normHome
    drawProbability = min(normHome / normDraw, normAway / normDraw)
    score = ""
    if winProbability >= 1.2 and drawProbability >= 0.5:
        score = scoreLoop(2,2,True, True, False)
    elif winProbability >= 1.2 and drawProbability < 0.5:
        score = scoreLoop(3,3,True,False,False)
    elif winProbability <= 0.8 and drawProbability >= 0.5:
        score = scoreLoop(2,2,False, True, False)
    elif winProbability <= 0.8 and drawProbability < 0.5:
        score = scoreLoop(3,3, False, False, False)
    else:
        score = scoreLoop(3,3,False,False,True)
    return score.split(":")

def scoreLoop(gHome: int, gAway: int, homeWins: bool, winOrDraw: bool, isRandom: bool):
    score = "0:0"
    scoreValid = False
    while scoreValid == False:
        gH = random.randint(0, gHome)
        gA = random.randint(0, gAway)
        score = "{0}:{1}".format(gH, gA)
        if isRandom:
            scoreValid = True
        if winOrDraw and gH == gA:
            scoreValid = True
        if homeWins and (gH > gA ) or (not homeWins and gH < gA) :
            scoreValid = True
    return score

def login(driver: webdriver.Chrome, user: str, password: str):
    email = driver.find_element(By.ID, "kennung")
    email.clear()
    email.send_keys(user)
    pw = driver.find_element(By.ID, "passwort")
    pw.clear()
    pw.send_keys(password)
    submit = driver.find_element(By.NAME, "submitbutton")
    submit.click()
    removeCookieBanner(driver)

def removeCookieBanner(driver: webdriver.Chrome):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'css-k8o10q')]")))
        cookie_banner = driver.find_element(By.XPATH, "//*[contains(@class, 'css-k8o10q')]")
        cookie_banner.click()
    except NoSuchElementException:
        pass

def predictMatches(driver: webdriver.Chrome, matches: list, fullRandom: bool, isTestRun: bool):
    removeCookieBanner
    for match in matches:
        t1 = match.find_element(By.CLASS_NAME, "col1").text
        t2 = match.find_element(By.CLASS_NAME, "col2").text
        t3 = match.find_element(By.CLASS_NAME, "col3")
        quoten = match.find_element(By.CLASS_NAME, "col4").text
        if fullRandom:
            score = scoreLoop(3,3,False, False, True).split(':')
        else:
            score = calcMatch(t1,t2,quoten)
        try:
            score_home = t3.find_element(By.XPATH, ".//*[contains(@id, '_heimTipp')]")
            score_home.clear()
            score_home.send_keys(str(score[0]))
            score_away = t3.find_element(By.XPATH, ".//*[contains(@id, '_gastTipp')]")
            score_away.clear()
            score_away.send_keys(str(score[1]))
            if isTestRun:
                print(t1 +  ' : ' + t2 + ' - ' + str(score[0]) + ' : ' + str(score[1]) + " -- Quote -- " + quoten)
        except NoSuchElementException:
                print("THIS ONE!")
    if not testRun:
        saveBtn = driver.find_element(By.NAME, "submitbutton")
        saveBtn.click()

def loadMatches(driver: webdriver.Chrome, user: str, pw: str):
    driver.get(os.environ['KICKTIPP_URL'])
    if "login" in driver.current_url:
        login(driver, user, pw)
        driver.implicitly_wait(15)
        driver.get(os.environ['KICKTIPP_URL'])
    if "tippabgabe" in driver.current_url:
        match_table = driver.find_element(By.ID, "tippabgabeSpiele")
        matches = match_table.find_element(By.TAG_NAME, "tbody").find_elements(By.CLASS_NAME, "datarow")
        return matches
        
if __name__ == '__main__':
    load_dotenv()
    testRun = True
    options = Options()
    options.add_argument("--headless=new")
    '''Tipps Predi'''
    print("---Tipps Predi---")
    driver = webdriver.Chrome(options)
    matches = loadMatches(driver,os.environ['KICKTIPP_USER_PREDI'], os.environ['KICKTIPP_USER_PREDI_PW'])
    predictMatches(driver, matches, False, testRun)
    driver.close()

    '''Tipps Random'''
    print("---Tipps Random---")
    driver = webdriver.Chrome(options)
    matches = loadMatches(driver,os.environ['KICKTIPP_USER_RNDM'], os.environ['KICKTIPP_USER_RNDM_PW'])
    predictMatches(driver, matches, True, testRun)
    driver.close()

