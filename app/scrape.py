from app import db
from app.models import User, Report, Site, ReportUpdate, SiteUpdate, NewAction, NewDoc
from flask_login import current_user
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd 
import numpy as np
from datetime import date
from time import sleep
from sqlalchemy import create_engine
# from dotenv import load_dotenv
# import os

load_dotenv()

# GOOGLE_CHROME_BIN = os.getenv('GOOGLE_CHROME_BIN')
# CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')

today = date.today()

chrome_options = webdriver.ChromeOptions()
options.headless = True
options.add_argument("--window-size=1920,1200")
options.binary_location = GOOGLE_CHROME_BIN
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')


gt_start_url = 'https://geotracker.waterboards.ca.gov/profile_report?global_id='
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=chrome_options)

# driver = webdriver.Chrome(options=options, executable_path='/Users/fjgaughan94/Desktop/data-science/coding-temple/final-project/ideas-&-testing/selenium-test/chrome_driver/chromedriver')
engine = create_engine(os.getenv('DATABASE_URL'))

class InitialSiteScan():

    def __init__(self, sites_list, report_id):
        self.sites_list = sites_list
        self.report_id = report_id

    def start(self):
        new_report_update = ReportUpdate(report_id=self.report_id)
        db.session.add(new_report_update)
        db.session.commit()
        self.scrape_site_update(new_report_update)
        
    def scrape_site_update(self, report_update):
        for site in self.sites_list:
            # Navigating to the cleanup site page
            driver.get(gt_start_url + site[1])
            # Grabbing the site's status
            site_status = driver.find_element_by_xpath('//*[@id="main-content"]/div/main/div/div[2]/table/tbody/tr/td/table/tbody/tr[1]/td/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[5]/td/font').text
            site_status = site_status.rstrip(" - DEFINITION")
            new_site_update = SiteUpdate(report_update_id=report_update.id, site_id=site[0], site_status=site_status)
            db.session.add(new_site_update)
            db.session.commit()
            self.scrape_top_action(new_site_update)
        return

    def scrape_top_action(self, site_update):
        # Navigating to the cleanup site page
        driver.get(gt_start_url + site_update.site.gt_global_id)
        # Navigate to the Regulatory Activiaties Tag
        try:
            driver.find_element_by_link_text("Regulatory Activities").click()
            # Wait for the page to load
            xpath = "//table[@id='mytab']/tbody/tr/td/table/tbody/tr[2]/td[4]"
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            except TimeoutException:
                print("Required element still could not be found!")
            # loop through Regulatory Activity rows until it hits a row in the "New Actions" table
            action_date = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[3]/td[4]").text
            description = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[3]/td[6]").text
            action_type = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[3]/td[2]").text
            action = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[3]/td[3]").text
            received_date = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[3]/td[5]").text
            new_action_row = NewAction(site_update_id=site_update.id, action_type=action_type, action=action, 
                                        action_date=action_date, received_date=received_date, description=description)
            db.session.add(new_action_row)
            db.session.commit()
            return
        except:
            return
            # driver.find_element_by_xpath("//a[@class='tab-disabled']/span"):
            # if driver.find_element_by_xpath("//a[@class='tab-disabled']/span").text == 'Regulatory Activities':  
            #     return 

class ReportUpdateScan():

    def __init__(self, report_id):
        report = Report.query.get_or_404(report_id)
        last_report_update = report.report_updates[-1]
        # Get the last site update for each site - query all sites_updates matching the site_id, and grab the bottom one
        last_site_updates = [site.site_updates[-1] for site in report.sites]
        # Create a list of lists with the site id, GeoTracker global id, and site update id for each site, drawn from last_site_updates
        sites_list = [[site_update.site_id, site_update.site.gt_global_id, site_update.id] for site_update in last_site_updates]
        self.last_site_updates_ids = [site_update.id for site_update in last_site_updates]
        self.sites_list = sites_list
        self.report_id = report_id


    def start(self):
        new_report_update = ReportUpdate(report_id=self.report_id)
        db.session.add(new_report_update)
        db.session.commit()
        self.scrape_site_update(new_report_update)


    def scrape_site_update(self, report_update):
        for site in self.sites_list:
            # Navigating to the cleanup site page
            driver.get(gt_start_url + site[1])
            # Grabbing the site's status
            prev_site_status = Site.query.filter_by(id=site[0]).first().site_updates[-1].site_status
            site_status = driver.find_element_by_xpath('//*[@id="main-content"]/div/main/div/div[2]/table/tbody/tr/td/table/tbody/tr[1]/td/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[5]/td/font').text
            site_status = site_status.rstrip(" - DEFINITION")
            if site_status != prev_site_status:
                new_site_update = SiteUpdate(report_update_id=report_update.id, site_id=site[0], site_status=site_status, status_changed=True)
                db.session.add(new_site_update)
                db.session.commit()
            else:
                new_site_update = SiteUpdate(report_update_id=report_update.id, site_id=site[0], site_status=site_status)
                db.session.add(new_site_update)
                db.session.commit()
            self.scrape_new_actions(new_site_update)
        return


    def scrape_new_actions(self, site_update):
        # Navigating to the cleanup site page
        driver.get(gt_start_url + site_update.site.gt_global_id)
        # Check if the Regulatory Activities tab is active
        if driver.find_element_by_xpath("//a[@class='tab-disabled']/span").text == 'Regulatory Activities':
            return 
        # Navigate to the Regulatory Activities tab
        driver.find_element_by_link_text("Regulatory Activities").click()
        # Wait for the page to load
        xpath = "//table[@id='mytab']/tbody/tr/td/table/tbody/tr[2]/td[4]"
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            print("Required element still could not be found!")
        # loop through Regulatory Activity rows until it hits a row in the "New Actions" table
        last_site_update_w_action = SiteUpdate.query.filter_by(site_id=site_update.site_id).filter(SiteUpdate.new_actions.any()).all()[-1]
        last_site_action = last_site_update_w_action.new_actions[0]
        for i in range(2,10):
            # Check if action date and description in the row are in the "New Actions" table
            action_date = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[4]").text
            description = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[6]").text
            # I'm checking if the top action is in the last Site Update
            # The last site update will have the appropriate date to check against.
            # I need to make a list of the action dates from the last Site Update and see if action_date is in there
            # all_site_actions = NewAction.query.filter(NewAction.site_update_id.in_(site_update_ids)).all()
            if action_date == last_site_action.action_date and description == last_site_action.description:
                break
            else:
                action_type = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[2]").text
                action = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[3]").text
                received_date = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[5]").text
                new_action_row = NewAction(site_update_id=site_update.id, action_type=action_type, action=action, action_date=action_date, received_date=received_date, description=description)
                db.session.add(new_action_row)
                db.session.commit()
        self.scrape_new_docs(site_update)
        return


    def scrape_new_docs(self, site_update):
        # Navigate to the cleanup site page
        driver.get(gt_start_url + site_update.site.gt_global_id)
        # Navigate to the Regulatory Activiaties Tag
        driver.find_element_by_link_text("Regulatory Activities").click()
        # Wait for the page to load
        # Loop through each of the new actions just appended to the site update
        for i in range(2, (len(site_update.new_actions)+2)):
            # Click on "[VIEW DOCS]" for the current new_action
            # How do we get the table row number? 
            # if driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{int(i+2)}]/td[1]/a") is False:
            #     continue
            # else: 
            # THE XPATH ABSOLUTELY EXISTS. SO THIS SHOULD BE A PROBLEM WITH THE WINDOW VIEW CHANGE. 
            xpath = "//table[@id='mytab']/tbody/tr/td/table/tbody/tr[2]/td[4]"
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            except TimeoutException:
                print("Required element still could not be found!") 
            if driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[1]").text != "[VIEW DOCS]":
                continue
            else:
                driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[1]/a").click()
                # Switch the driver's window handle to the new web page (the [VIEW DOCS] page that has the pdf links)
                site_page = driver.window_handles[0]
                view_docs_page = driver.window_handles[1]
                driver.switch_to.window(view_docs_page)
                # Wait for the page to load
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@href]")))
                except TimeoutException:
                    print("Required element still could not be found!")
                # Get each doc's pdf link and name
                pdf_links = driver.find_elements_by_xpath("//a[@href]")
                for pdf in pdf_links:
                    link = pdf.get_attribute('href')
                    name = pdf.text
                    new_doc_row = NewDoc(new_action_id=site_update.new_actions[i-2].id, doc_name=name, doc_link=link)
                    db.session.add(new_doc_row)
                    db.session.commit()
                driver.switch_to.window(site_page)     
        return  


