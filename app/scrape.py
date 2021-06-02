from app import db
from app.models import User, Report, Site, ReportUpdate, SiteUpdate, NewAction, NewDoc
from flask_login import current_user
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import date
from time import sleep
from sqlalchemy import create_engine

# Web Scraping Setup
today = date.today()
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
gt_start_url = 'https://geotracker.waterboards.ca.gov/profile_report?global_id='
driver = webdriver.Chrome(options=options, executable_path='/Users/fjgaughan94/Desktop/data-science/coding-temple/final-project/ideas-&-testing/selenium-test/chrome_driver/chromedriver')
database_uri = 'postgres://cglpswlj:PljB6Lqcs31c_WxbjZ8w77WNxJVty0zU@queenie.db.elephantsql.com:5432/cglpswlj'
engine = create_engine(database_uri)

# This class is instantiated and run when a user saves or updates a report--it locates, then saves to our database, the newest action for each site under the 
# "Regulatory Activities" tab on GeoTracker. This allows the program to determine if any updates have been posted when the user clicks the "scan for updates" button 
# for the first time.
class initial_site_scan():

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
            # Navigate to the site's page on GeoTracker using its Global ID
            driver.get(gt_start_url + site[1])
            # Get and clean the site's status
            site_status = driver.find_element_by_xpath('//*[@id="main-content"]/div/main/div/div[2]/table/tbody/tr/td/table/tbody/tr[1]/td/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[5]/td/font').text
            site_status = site_status.rstrip(" - DEFINITION")
            # Save the status to our database
            new_site_update = SiteUpdate(report_update_id=report_update.id, site_id=site[0], site_status=site_status)
            db.session.add(new_site_update)
            db.session.commit()
            self.scrape_top_action(new_site_update)
        return

    def scrape_top_action(self, site_update):
        # Navigate to the site's page on GeoTracker using its Global ID (pulled from our database).
        driver.get(gt_start_url + site_update.site.gt_global_id)
        # Navigate to the Regulatory Activities Tag
        try:
            driver.find_element_by_link_text("Regulatory Activities").click()
            # Give the page time to load
            xpath = "//table[@id='mytab']/tbody/tr/td/table/tbody/tr[2]/td[4]"
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            except TimeoutException:
                print("Required element still could not be found!")
            # Get the newest action under the Regulatory Activities Tab, and save to our database
            action_date = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[2]/td[4]").text
            description = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[2]/td[6]").text
            action_type = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[2]/td[2]").text
            action = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[3]/td[2]").text
            received_date = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[2]/td[5]").text
            new_action_row = NewAction(site_update_id=site_update.id, action_type=action_type, action=action, 
                                        action_date=action_date, received_date=received_date, description=description)
            db.session.add(new_action_row)
            db.session.commit()
            return
        except:
            return

# This class is instantiated and run when a user hits the "scan for updates" button on a report--it locates, then saves to our database, any new actions for each site under the 
# "Regulatory Activities" tab on GeoTracker. 
class report_update_scan():

    def __init__(self, report_id):
        report = Report.query.get_or_404(report_id)
        last_report_update = report.report_updates[-1]
        # Get the last site update for each site that's saved in our database
        last_site_updates = [site.site_updates[-1] for site in report.sites]
        # Create a list of lists with the site id, GeoTracker global id, and site update id for each site, drawn from last_site_updates
        self.sites_list = [[site_update.site_id, site_update.site.gt_global_id, site_update.id] for site_update in last_site_updates]
        self.last_site_updates_ids = [site_update.id for site_update in last_site_updates]
        self.report_id = report_id

    def start(self):
        new_report_update = ReportUpdate(report_id=self.report_id)
        db.session.add(new_report_update)
        db.session.commit()
        self.scrape_site_update(new_report_update)

    def scrape_site_update(self, report_update):
        for site in self.sites_list:
            # Navigate to the site's page on GeoTracker using its Global ID
            driver.get(gt_start_url + site[1])
            # Compare the site's current status with the last status saved in our database
            prev_site_status = Site.query.filter_by(id=site[0]).first().site_updates[-1].site_status
            site_status = driver.find_element_by_xpath('//*[@id="main-content"]/div/main/div/div[2]/table/tbody/tr/td/table/tbody/tr[1]/td/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[5]/td/font').text
            site_status = site_status.rstrip(" - DEFINITION")
            # Save the new site update to our database
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
        # Navigate to the site's page on GeoTracker using its Global ID
        driver.get(gt_start_url + site_update.site.gt_global_id)
        # Check if the Regulatory Activities tab is active
        if driver.find_element_by_xpath("//a[@class='tab-disabled']/span").text == 'Regulatory Activities':
            return 
        # Navigate to the Regulatory Activities tab
        driver.find_element_by_link_text("Regulatory Activities").click()
        # Give the page time to load
        xpath = "//table[@id='mytab']/tbody/tr/td/table/tbody/tr[2]/td[4]"
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            print("Required element still could not be found!")
        # Loop through Regulatory Activity rows until it hits a row that is in the "New Actions" table in our database
        last_site_update_w_action = SiteUpdate.query.filter_by(site_id=site_update.site_id).filter(SiteUpdate.new_actions.any()).all()[-1]
        last_site_action = last_site_update_w_action.new_actions[0]
        for i in range(2,10):
            # Check if action date and description in the row are in the "New Actions" table in our database
            action_date = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[4]").text
            description = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[6]").text
            if action_date == last_site_action.action_date and description == last_site_action.description:
                break
            else:
                # If the action is not in our database, get the row's data and save it to our database
                action_type = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[2]").text
                action = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[3]").text
                received_date = driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[5]").text
                new_action_row = NewAction(site_update_id=site_update.id, action_type=action_type, action=action, action_date=action_date, received_date=received_date, description=description)
                db.session.add(new_action_row)
                db.session.commit()
        self.scrape_new_docs(site_update)
        return


    def scrape_new_docs(self, site_update):
        # Navigate to the site's page on GeoTracker using its Global ID
        driver.get(gt_start_url + site_update.site.gt_global_id)
        # Navigate to the Regulatory Activities Tab
        driver.find_element_by_link_text("Regulatory Activities").click()
        # Loop through each of the new actions just appended to the site update
        for i in range(2, (len(site_update.new_actions)+2)):
            # Give the page time to load
            xpath = "//table[@id='mytab']/tbody/tr/td/table/tbody/tr[2]/td[4]"
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            except TimeoutException:
                print("Required element still could not be found!") 
            # Click on "[VIEW DOCS]" for the current new_action
            if driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[1]").text != "[VIEW DOCS]":
                continue
            else:
                driver.find_element_by_xpath(f"//table[@id='mytab']/tbody/tr/td/table/tbody/tr[{i}]/td[1]/a").click()
                # Switch the driver's window handle to the new web page (the [VIEW DOCS] page that has the pdf links)
                site_page = driver.window_handles[0]
                view_docs_page = driver.window_handles[1]
                driver.switch_to.window(view_docs_page)
                # Give the page time to load
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@href]")))
                except TimeoutException:
                    print("Required element still could not be found!")
                # Get each doc's pdf link and name, and save to our database
                pdf_links = driver.find_elements_by_xpath("//a[@href]")
                for pdf in pdf_links:
                    link = pdf.get_attribute('href')
                    name = pdf.text
                    new_doc_row = NewDoc(new_action_id=site_update.new_actions[i-2].id, doc_name=name, doc_link=link)
                    db.session.add(new_doc_row)
                    db.session.commit()
                driver.switch_to.window(site_page)     
        return  


