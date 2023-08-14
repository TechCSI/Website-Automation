import time
import datetime
import bs4
from pytz import unicode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
#get data of 2 days
def getDate() :
    start_date = datetime.date(2020, 2, 1)
    end_date = datetime.date(2020, 2, 3)
    # delta time
    delta = datetime.timedelta(days=1)
    date_data = []
    # iterate over range of dates
    while (start_date <= end_date):
        year = str(start_date.year)
        month = str(start_date.month) if start_date.month > 9 else "0" + str(start_date.month)
        day = str(start_date.day) if start_date.day > 9 else "0" + str(start_date.day)
        new_date = day + "/" + month + "/" + year
        date_data.append(new_date)
        start_date += delta
    return  date_data
def get_tables(htmldoc):
    soup = bs4.BeautifulSoup(htmldoc,"html.parser")
    return soup.find('table', {'id': 'gv0'})
def getTableHead(table):
    result = []
    header = table.find('thead').find('tr')
    cols = header.findAll('th')
    for col in cols:
        thestrings1 = [unicode(s) for s in col.findAll(text=True)]
        thetext1 = ''.join(thestrings1)
        result.append(thetext1)
    return result
def getTableData(table):
    table_head = getTableHead(table)
    result = []
    allrows = table.findAll('tr')
    for row in allrows:
        result.append([])
        allcols = row.findAll('td')
        for col in allcols:
            thestrings = [unicode(s) for s in col.findAll(text=True)]
            thetext = ''.join(thestrings)
            result[-1].append(thetext)
    return result
def navigateWebsite():
    driver = webdriver.Chrome()
    driver.get("https://fcainfoweb.nic.in/reports/report_menu_web.aspx")
    date_arr = getDate()
    dataset = []
    table_head_insert = False
    progress = 0
    for date in date_arr:
        start_time = time.strftime("%H:%M:%S", time.localtime())
        driver.find_element(By.ID, "ctl00_MainContent_Rbl_Rpt_type_0").click()
        time.sleep(0.005)
        find_daily_price = \
            driver.find_element(By.ID, "ctl00_MainContent_Ddl_Rpt_Option0")
        Select(find_daily_price).select_by_index(1)
        time.sleep(0.005)
        driver.find_element(By.ID, "ctl00_MainContent_Txt_FrmDate").send_keys(date)
        time.sleep(0.005)
        driver.find_element(By.ID, "ctl00_MainContent_btn_getdata1").click()
        time.sleep(0.005)
        table = get_tables(driver.page_source)
        data_arr = getTableData(table)
        if not table_head_insert:
            head_data = getTableHead(table)
            data_arr[0] = head_data
            table_head_insert = True
        dataset.append(pd.DataFrame(data_arr))
        time.sleep(0.005)
        driver.find_element(By.ID, "btn_back").click()
        time.sleep(0.005)
        progress += 1
        if not data_arr:
            print(":::Problem in Fetching Data:::")
        print("Fetching Data of : ",date , " Start at ", start_time, " Finish at : ",time.strftime("%H:%M:%S", time.localtime()), "Progress : ", progress,"/",len(date_arr)," ", round(progress/len(date_arr),2),"%")
    return dataset

print("Start At : ",time.strftime("%H:%M:%S", time.localtime()) )
combined_df = pd.concat(navigateWebsite())
combined_df.to_csv('combined.csv', index=False)
print("Complete At : ",time.strftime("%H:%M:%S", time.localtime()))


#driver.find_element_by_xpath('/html/body/form/div[2]/div[2]/table/tbody/tr[0]/td[1]/table/tbody/tr[0]/td/input').click()
# content = driver.page_source
# soup = BeautifulSoup(content)
# price_report = soup.find('input', attrs={'id' : 'ctl00_MainContent_Rbl_Rpt_type_0'}).click()
