import logging

logger = logging.getLogger(__name__)

class JobAnalyzer:
    def __init__(self, config):
        self.config = config
        self.allowed_levels = config['job_title_filter']['allowed_levels']
        self.blocked_titles = config['job_title_filter']['blocked_titles']
        self.min_probability = config['search']['min_probability']
    
    def analyze_job(self, job_posting):
        print(f"\n{'='*80}")
        print(f"ANALYZING: {job_posting['title']} @ {job_posting['company']}")
        print(f"{'='*80}")
        
        # Extract keywords
        keywords = self._extract_keywords(job_posting)
        print(f"Keywords found: {len(keywords)}")
        
        # Validate title
        title_valid = self._validate_title(job_posting['title'])
        
        if not title_valid:
            return {
                'apply': False,
                'probability': 0,
                'tier': 'BLOCKED',
                'reason': 'Job title contains blocked keywords',
                'keywords': keywords
            }
        
        # Calculate probability
        probability = self._calculate_probability(job_posting, keywords)
        print(f"Probability score: {probability}%")
        
        # Determine tier
        tier = self._get_tier(probability)
        
        # Make decision
        if probability >= self.min_probability:
            return {
                'apply': True,
                'probability': probability,
                'tier': tier,
                'reason': f'Match! {tier} level ({probability}% probability)',
                'keywords': keywords
            }
        else:
            return {
                'apply': False,
                'probability': probability,
                'tier': tier,
                'reason': f'Probability {probability}% below {self.min_probability}% threshold',
                'keywords': keywords
            }
    
    def _extract_keywords(self, job_posting):
        text = (job_posting['title'] + ' ' + job_posting.get('company', '')).lower()
        keywords = ['operations', 'strategy', 'analytics', 'supply', 'leadership']
        found = [kw for kw in keywords if kw in text]
        return found
    
    def _validate_title(self, title):
        title_lower = title.lower()
        for blocked in self.blocked_titles:
            if blocked.lower() in title_lower:
                return False
        return True
    
    def _calculate_probability(self, job_posting, keywords):
        score = 50 + (len(keywords) * 5)
        return min(score, 100)
    
    def _get_tier(self, probability):
        if probability >= 85:
            return 'SENIOR'
        elif probability >= 75:
            return 'ASSOCIATE'
        elif probability >= 65:
            return 'SPECIALIST'
        else:
            return 'SKIP'


class ApplicationLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self._init_file()
    
    def _init_file(self):
        try:
            with open(self.log_file, 'a') as f:
                if f.tell() == 0:
                    f.write('timestamp,company,title,probability,tier,status\n')
        except Exception as e:
            print(f"Error initializing log file: {e}")
    
    def log_application(self, application_data):
        try:
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            row = f"{timestamp},{application_data.get('company', '')},{application_data.get('title', '')},{application_data.get('probability', '')},{application_data.get('tier', '')},APPLIED\n"
            with open(self.log_file, 'a') as f:
                f.write(row)
            print(f"✓ Application logged: {application_data['company']}")
        except Exception as e:
            print(f"Error logging application: {e}")