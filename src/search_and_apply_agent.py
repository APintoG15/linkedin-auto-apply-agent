import json
import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from linkedin_automation import LinkedInAutomation
from job_analyzer import JobAnalyzer, ApplicationLogger

load_dotenv()

class LinkedInJobSearchAgent:
    """Advanced agent that searches and applies to jobs automatically"""
    
    def __init__(self):
        print("\n" + "="*100)
        print("LINKEDIN JOB SEARCH & AUTO-APPLY AGENT - STARTING")
        print("="*100 + "\n")
        
        self.config = self._load_config('config/config.json')
        self.analyzer = JobAnalyzer(self.config)
        self.application_logger = ApplicationLogger(os.getenv('LOG_FILE', 'logs/applications.csv'))
        
        self.linkedin = LinkedInAutomation(
            email=os.getenv('LINKEDIN_EMAIL'),
            password=os.getenv('LINKEDIN_PASSWORD')
        )
        
        self.applications_submitted = 0
        self.jobs_found = 0
    
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"✓ Configuration loaded: {config_path}")
            return config
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            raise
    
    def search_and_apply(self):
        """Main method: search jobs and apply automatically"""
        
        print("\n" + "="*100)
        print("STEP 1: INITIALIZE BROWSER")
        print("="*100 + "\n")
        
        if not self.linkedin.initialize_driver():
            print("❌ Failed to initialize browser")
            return
        
        print("\n" + "="*100)
        print("STEP 2: LOGIN TO LINKEDIN")
        print("="*100 + "\n")
        
        if not self.linkedin.login_to_linkedin():
            print("❌ Failed to login")
            self.linkedin.close_driver()
            return
        
        print("\n" + "="*100)
        print("STEP 3: SEARCH FOR JOBS")
        print("="*100 + "\n")
        
        jobs = self._search_jobs_on_linkedin()
        
        if not jobs:
            print("❌ No jobs found matching your criteria")
            self.linkedin.close_driver()
            return
        
        print(f"✓ Found {len(jobs)} jobs matching criteria\n")
        
        print("\n" + "="*100)
        print(f"STEP 4: ANALYZE & APPLY TO JOBS")
        print("="*100 + "\n")
        
        for i, job in enumerate(jobs, 1):
            print(f"\n[{i}/{len(jobs)}] Processing job...")
            self._process_and_apply_to_job(job)
            
            # Rate limiting
            if i < len(jobs):
                rate_limit = self.config['application_limits']['rate_limit_seconds']
                print(f"   Waiting {rate_limit} seconds before next job...")
                time.sleep(rate_limit)
        
        print("\n" + "="*100)
        print("STEP 5: SUMMARY")
        print("="*100 + "\n")
        
        print(f"Jobs found: {self.jobs_found}")
        print(f"Applications submitted: {self.applications_submitted}")
        print(f"Success rate: {self.applications_submitted}/{self.jobs_found}")
        
        self.linkedin.close_driver()
        print("\n✅ JOB SEARCH & APPLICATION COMPLETE\n")
    
    def _search_jobs_on_linkedin(self):
        """Search for jobs on LinkedIn matching criteria"""
        try:
            # Navigate to LinkedIn jobs page
            self.linkedin.driver.get("https://www.linkedin.com/jobs/search/")
            time.sleep(3)
            
            # Build search query from config
            keywords = self.config['search']['keywords']
            location = self.config['search']['location']
            
            search_query = f"{keywords[0]} {location}"
            print(f"Searching for: {search_query}")
            
            # Find search box and search
            search_box = self.linkedin.driver.find_element(By.XPATH, "//input[@placeholder='Search by title, skill, or company']")
            search_box.clear()
            search_box.send_keys(search_query)
            search_box.send_keys("\n")
            
            time.sleep(5)
            
            # Extract job URLs from search results
            job_links = self.linkedin.driver.find_elements(By.XPATH, "//a[@data-job-id]")
            jobs = []
            
            for link in job_links[:10]:  # Limit to first 10 results
                try:
                    job_url = link.get_attribute('href')
                    if job_url and '/jobs/view/' in job_url:
                        jobs.append({
                            'url': job_url,
                            'title': 'Job from LinkedIn',
                            'company': 'Company'
                        })
                except:
                    pass
            
            self.jobs_found = len(jobs)
            return jobs
            
        except Exception as e:
            print(f"❌ Error searching jobs: {e}")
            return []
    
    def _process_and_apply_to_job(self, job):
        """Process a single job and apply if it matches criteria"""
        print(f"📋 Job URL: {job['url']}")
        
        try:
            # Open job
            self.linkedin.driver.get(job['url'])
            time.sleep(2)
            
            # Extract job details
            try:
                title_elem = self.linkedin.driver.find_element(By.XPATH, "//h1[contains(@class, 'jobs-details')]")
                title = title_elem.text
            except:
                title = job.get('title', 'Unknown')
            
            try:
                company_elem = self.linkedin.driver.find_element(By.XPATH, "//a[contains(@href, '/company/')]")
                company = company_elem.text
            except:
                company = job.get('company', 'Unknown')
            
            job['title'] = title
            job['company'] = company
            
            print(f"   Title: {title}")
            print(f"   Company: {company}")
            
            # Analyze job
            analysis = self.analyzer.analyze_job(job)
            
            if not analysis['apply']:
                print(f"   ❌ SKIP - {analysis['reason']}")
                return
            
            print(f"   ✅ APPLYING - {analysis['reason']}")
            
            # Look for Easy Apply button
            try:
                easy_apply_btn = WebDriverWait(self.linkedin.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Easy Apply')]"))
                )
                easy_apply_btn.click()
                print("   ✓ Clicked Easy Apply")
                time.sleep(2)
                
                # Submit application (skip form filling for now)
                try:
                    submit_btn = WebDriverWait(self.linkedin.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Submit') or contains(., 'Send')]"))
                    )
                    submit_btn.click()
                    print("   ✅ Application submitted!")
                    
                    self.applications_submitted += 1
                    self.application_logger.log_application({
                        'company': company,
                        'title': title,
                        'probability': analysis['probability'],
                        'tier': analysis['tier']
                    })
                except:
                    print("   ⚠ Could not find submit button")
            except:
                print("   ❌ Easy Apply button not found")
        
        except Exception as e:
            print(f"   ❌ Error processing job: {e}")


def main():
    agent = LinkedInJobSearchAgent()
    agent.search_and_apply()


if __name__ == '__main__':
    main()