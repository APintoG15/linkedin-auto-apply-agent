import json
import os
from dotenv import load_dotenv
from linkedin_automation import LinkedInAutomation
from job_analyzer import JobAnalyzer, ApplicationLogger

load_dotenv()

class LinkedInAutoApplyAgent:
    def __init__(self):
        print("\n" + "="*100)
        print("LINKEDIN AUTO-APPLY AGENT - INITIALIZING")
        print("="*100 + "\n")
        
        self.config = self._load_config('config/config.json')
        self.analyzer = JobAnalyzer(self.config)
        self.application_logger = ApplicationLogger(os.getenv('LOG_FILE', 'logs/applications.csv'))
        self.linkedin = LinkedInAutomation(
            email=os.getenv('LINKEDIN_EMAIL'),
            password=os.getenv('LINKEDIN_PASSWORD')
        )
        self.applications_submitted = 0
    
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"✓ Configuration loaded: {config_path}")
            return config
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            raise
    
    def run(self, jobs):
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
        print(f"STEP 3: PROCESS {len(jobs)} JOBS")
        print("="*100 + "\n")
        
        for i, job in enumerate(jobs, 1):
            print(f"\n[{i}/{len(jobs)}] Processing job...")
            self._process_job(job)
        
        print("\n" + "="*100)
        print("STEP 4: SUMMARY")
        print("="*100 + "\n")
        
        print(f"Applications submitted: {self.applications_submitted}")
        
        self.linkedin.close_driver()
        print("\n✅ AGENT EXECUTION COMPLETE\n")
    
    def _process_job(self, job):
        print(f"\n📋 Job: {job['title']} @ {job['company']}")
        
        try:
            analysis = self.analyzer.analyze_job(job)
            
            if not analysis['apply']:
                print(f"   ❌ SKIP - {analysis['reason']}")
                return
            
            print(f"   ✅ APPLY - {analysis['reason']}")
            self.applications_submitted += 1
            
            self.application_logger.log_application({
                'company': job['company'],
                'title': job['title'],
                'probability': analysis['probability'],
                'tier': analysis['tier']
            })
        
        except Exception as e:
            print(f"   ❌ Error processing job: {e}")


def main():
    sample_jobs = [
        {
            'title': 'Strategy Senior Associate',
            'company': 'Bechtel Corporation',
            'location': 'Washington, DC',
            'description': 'Strategic operations role'
        }
    ]
    
    agent = LinkedInAutoApplyAgent()
    agent.run(jobs=sample_jobs)


if __name__ == '__main__':
    main()