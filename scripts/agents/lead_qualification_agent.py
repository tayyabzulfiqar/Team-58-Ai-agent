"""
Lead Scoring & Qualification Agent (Prompt 3)
Evaluates business leads and assigns qualification scores
"""
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LeadQualificationResult:
    company_name: str
    score: int
    category: str
    reason: str
    opportunity: str
    next_action: str


class LeadQualificationAgent:
    """
    Lead Scoring & Qualification Agent
    Evaluates businesses and assigns qualification scores
    """
    
    def __init__(self):
        self.weights = {
            'has_active_marketing': 20,
            'shows_lead_need': 25,
            'service_based': 15,
            'website_quality': 15,
            'monetization_potential': 25
        }
    
    def qualify_lead(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        B2B Lead Scoring AI for Digital Marketing Agency
        """
        try:
            company_name = analyzed_data.get('company_name', 'Unknown')
            positive_score = 0
            negative_score = 0
            reason_list = []
            risk_flags = []
            
            services = analyzed_data.get('services', [])
            industry = analyzed_data.get('industry', '')
            pain_points = analyzed_data.get('pain_points', [])
            intent_signals = analyzed_data.get('intent_signals', [])
            all_signals = ' '.join(pain_points + intent_signals).lower()
            service_text = ' '.join(services).lower() + ' ' + industry.lower()
            target_audience = analyzed_data.get('target_audience', '')
            target_lower = target_audience.lower()
            
            # === POSITIVE SIGNALS ===
            
            # 1. Service Fit (0-25)
            strong_fit = ['lead generation', 'paid ads', 'ppc', 'facebook ads', 'google ads', 'marketing agency']
            partial_fit = ['digital marketing', 'marketing', 'growth', 'sales', 'b2b', 'saas', 'consulting']
            
            if any(fit in service_text for fit in strong_fit):
                positive_score += 25
                reason_list.append("High alignment with lead generation/ads (+25)")
            elif any(fit in service_text for fit in partial_fit):
                positive_score += 15
                reason_list.append("Partial alignment with marketing (+15)")
            else:
                positive_score += 5
                reason_list.append("Weak relevance (+5)")
            
            # 2. Paid Ads Presence (0-15)
            running_ads = analyzed_data.get('running_ads', False)
            has_blog = analyzed_data.get('has_blog', False)
            social_links = analyzed_data.get('social_links', {})
            has_social = bool(social_links and any(social_links.values()))
            
            if running_ads:
                positive_score += 15
                reason_list.append("Actively running paid ads (+15)")
            elif has_social:
                positive_score += 8
                reason_list.append("Some marketing activity (+8)")
            else:
                reason_list.append("No ads detected (+0)")
            
            # 3. Pain Level / Problem Clarity (0-20)
            strong_pain = ['losing money', 'ads not working', 'high cac', 'low roas', 'burning budget']
            moderate_pain = ['need more leads', 'low conversion', 'scaling issues', 'growth problem', 'expensive leads']
            
            if any(pain in all_signals for pain in strong_pain):
                positive_score += 20
                reason_list.append("Clear scaling/revenue problem (+20)")
            elif any(pain in all_signals for pain in moderate_pain):
                positive_score += 12
                reason_list.append("Moderate inefficiency (+12)")
            else:
                positive_score += 3
                reason_list.append("No visible pain (+3)")
            
            # 4. ICP Match (0-10)
            icp_perfect = ['b2b', 'enterprise', 'saas', 'agencies', 'corporate', 'startups with funding']
            icp_partial = ['small business', 'local business', 'ecommerce', 'retail']
            
            if any(ind in target_lower for ind in icp_perfect):
                positive_score += 10
                reason_list.append("Perfect target industry (+10)")
            elif any(ind in target_lower for ind in icp_partial):
                positive_score += 6
                reason_list.append("Somewhat relevant (+6)")
            else:
                positive_score += 2
                reason_list.append("Not ideal (+2)")
            
            # 5. Urgency Signals (0-15)
            hiring = analyzed_data.get('hiring', False)
            strong_urgency = ['hiring marketers', 'scaling fast', 'new funding', 'series a', 'series b', 'expansion']
            mild_urgency = ['growing', 'expanding', 'new launch']
            
            if hiring or any(u in all_signals for u in strong_urgency):
                positive_score += 15
                reason_list.append("Hiring/scaling/new funding (+15)")
            elif any(u in all_signals for u in mild_urgency):
                positive_score += 7
                reason_list.append("Some activity (+7)")
            else:
                positive_score += 2
                reason_list.append("No urgency (+2)")
            
            # 6. Decision Maker Presence (0-10)
            decision_maker = analyzed_data.get('decision_maker', False)
            founder_title = analyzed_data.get('contact_title', '').lower()
            
            is_founder = any(title in founder_title for title in ['founder', 'ceo', 'owner', 'cmo', 'vp marketing'])
            is_mid = any(title in founder_title for title in ['manager', 'director', 'head'])
            
            if decision_maker and is_founder:
                positive_score += 10
                reason_list.append("Founder/CEO reachable (+10)")
            elif is_mid or decision_maker:
                positive_score += 6
                reason_list.append("Mid-level contact (+6)")
            else:
                positive_score += 2
                reason_list.append("No clear contact (+2)")
            
            # 7. Business Size / Budget Potential (0-5)
            company_size = analyzed_data.get('company_size', '')
            revenue = analyzed_data.get('revenue_range', '')
            team_size = analyzed_data.get('team_size', 0)
            
            if revenue in ['$1M+', '$5M+', '$10M+'] or company_size in ['50-200', '200+'] or team_size >= 20:
                positive_score += 5
                reason_list.append("Established revenue/business (+5)")
            elif company_size in ['10-50'] or team_size >= 5:
                positive_score += 3
                reason_list.append("Small but viable (+3)")
            else:
                positive_score += 1
                reason_list.append("Very small (+1)")
            
            # === NEGATIVE SIGNALS ===
            
            # No monetization
            if not services and not industry:
                negative_score += 20
                risk_flags.append("No monetization")
            
            # Freelancer / solo operator
            is_solo = company_size in ['solo', '1-5', '1'] or team_size == 1
            if is_solo:
                negative_score += 10
                risk_flags.append("Freelancer/solo operator")
            
            # No website / weak presence
            website_quality = analyzed_data.get('website_quality', '')
            if website_quality in ['none', 'no website'] or not analyzed_data.get('has_website', True):
                negative_score += 10
                risk_flags.append("No website/weak presence")
            
            # Wrong geography (if specified)
            geography = analyzed_data.get('geography', '')
            if geography in ['unreachable', 'wrong region']:
                negative_score += 10
                risk_flags.append("Wrong geography")
            
            # Low trust / spam signals
            spam_signals = ['make money fast', 'mlm', 'crypto', 'gambling']
            if any(spam in service_text for spam in spam_signals):
                negative_score += 20
                risk_flags.append("Low trust/spam signals")
            
            # === FINAL SCORE ===
            final_score = positive_score - negative_score
            final_score = max(0, min(100, final_score))
            
            # === CLASSIFICATION ===
            if final_score >= 85:
                color = "🔴 RED"
                priority = "Close immediately"
                action = "Contact immediately. Highly personalized outreach. Push for call within 24–48 hours"
            elif final_score >= 65:
                color = "🟠 ORANGE"
                priority = "High priority"
                action = "Send personalized proposal within 2–3 days. Focus on specific pain points"
            elif final_score >= 40:
                color = "🟡 YELLOW"
                priority = "Nurture"
                action = "Add to nurture sequence. Follow up later with value content"
            else:
                color = "⚫ BLACK"
                priority = "Ignore"
                action = "Ignore. Do not pursue"
            
            # === DEAL VALUE ESTIMATION ===
            if final_score >= 85:
                deal_value = "$5,000–$15,000/month"
            elif final_score >= 65:
                deal_value = "$3,000–$8,000/month"
            elif final_score >= 40:
                deal_value = "$1,000–$3,000/month"
            else:
                deal_value = "$0–$500/month"
            
            # === COMPETITION STATUS ===
            if running_ads:
                competition_status = "Competing in paid search - opportunity to outperform"
            elif positive_score > 60:
                competition_status = "Limited competition - first mover advantage"
            else:
                competition_status = "Unclear competitive landscape"
            
            result = {
                "company_name": company_name,
                "score": final_score,
                "color": color,
                "priority": priority,
                "action": action,
                "deal_value": deal_value,
                "decision_maker": decision_maker or is_founder,
                "competition_status": competition_status,
                "risk_flags": risk_flags if risk_flags else [],
                "reason": reason_list[:5]
            }
            
            return result
            
        except Exception as e:
            return {
                "company_name": analyzed_data.get('company_name', 'Unknown'),
                "score": 0,
                "color": "⚫ BLACK",
                "priority": "Ignore",
                "action": "Do not pursue",
                "deal_value": "$0/month",
                "decision_maker": False,
                "competition_status": "Error",
                "risk_flags": ["Processing error"],
                "reason": [f"Error: {str(e)}"]
            }
    
    def _score_marketing_activity(self, data: Dict[str, Any]) -> float:
        """Score 0-1 based on marketing activity"""
        score = 0.0
        
        # Check for social media presence
        if data.get('social_links', {}).get('linkedin') or data.get('linkedin_url'):
            score += 0.3
        if data.get('social_links', {}).get('twitter') or data.get('twitter_url'):
            score += 0.2
        
        # Check for blog/content
        if data.get('has_blog') or data.get('blog_url'):
            score += 0.3
        
        # Check for recent updates
        if data.get('website_updated_recently'):
            score += 0.2
        
        return min(1.0, score)
    
    def _score_lead_need(self, pain_points: list, intent_signals: list) -> float:
        """Score 0-1 based on signs they need leads/growth"""
        score = 0.0
        
        high_value_signals = [
            'need more clients', 'looking for customers', 'lead generation',
            'marketing help', 'growth partner', 'sales support',
            'struggling to find', 'need leads', 'customer acquisition'
        ]
        
        medium_value_signals = [
            'scale up', 'expand', 'new market', 'digital marketing',
            'online presence', 'brand awareness', 'competition'
        ]
        
        # Check pain points
        for pain in pain_points:
            pain_lower = pain.lower()
            if any(signal in pain_lower for signal in high_value_signals):
                score += 0.3
            elif any(signal in pain_lower for signal in medium_value_signals):
                score += 0.15
        
        # Check intent signals
        for signal in intent_signals:
            signal_lower = signal.lower()
            if any(s in signal_lower for s in high_value_signals):
                score += 0.2
            elif any(s in signal_lower for s in medium_value_signals):
                score += 0.1
        
        return min(1.0, score)
    
    def _score_business_type(self, services: list, industry: str) -> float:
        """Score 0-1 based on business type (service-based = higher value)"""
        service_industries = [
            'consulting', 'agency', 'services', 'software', 'saas',
            'marketing', 'legal', 'accounting', 'design', 'development'
        ]
        
        high_value_services = [
            'consulting', 'agency', 'b2b services', 'enterprise software',
            'professional services', 'marketing services'
        ]
        
        industry_lower = industry.lower()
        
        # Check industry
        if any(svc in industry_lower for svc in service_industries):
            return 0.8
        
        # Check services
        for service in services:
            service_lower = service.lower()
            if any(hv in service_lower for hv in high_value_services):
                return 1.0
            elif any(svc in service_lower for svc in service_industries):
                return 0.7
        
        return 0.4  # Default for product/ecommerce
    
    def _score_website(self, quality: str, data: Dict[str, Any]) -> float:
        """Score 0-1 based on website quality"""
        quality_scores = {
            'high': 1.0,
            'good': 0.8,
            'medium': 0.5,
            'average': 0.4,
            'poor': 0.2,
            'outdated': 0.1
        }
        
        base_score = quality_scores.get(quality.lower(), 0.5)
        
        # Boost if they have clear CTAs
        if data.get('has_cta') or data.get('has_contact_form'):
            base_score += 0.1
        
        # Penalty if very outdated
        if data.get('website_outdated') or data.get('no_https'):
            base_score -= 0.2
        
        return max(0.0, min(1.0, base_score))
    
    def _score_monetization_potential(self, data: Dict[str, Any]) -> float:
        """Score 0-1 based on monetization potential"""
        score = 0.0
        
        # Company size indicators
        if data.get('company_size') in ['50-200', '200-1000', '1000+']:
            score += 0.3
        elif data.get('company_size') in ['10-50']:
            score += 0.2
        
        # Funding/revenue indicators
        if data.get('funding_stage') or data.get('recent_funding'):
            score += 0.25
        
        if data.get('revenue_range') in ['$1M+', '$5M+', '$10M+']:
            score += 0.25
        
        # Team size
        if data.get('team_size') and int(str(data['team_size']).replace('+', '')) >= 10:
            score += 0.2
        
        # Multiple locations (growth indicator)
        if data.get('multiple_locations') or data.get('locations', 0) > 1:
            score += 0.1
        
        return min(1.0, score)
    
    def _generate_reasoning(self, components: Dict[str, float], 
                         pain_points: list, intent_signals: list) -> str:
        """Generate explanation for the score"""
        reasons = []
        
        if components['shows_lead_need'] > 0.6:
            reasons.append("Strong signals of lead generation needs")
        elif components['shows_lead_need'] > 0.3:
            reasons.append("Moderate interest in growth")
        else:
            reasons.append("Limited growth signals detected")
        
        if components['service_based'] > 0.6:
            reasons.append("Service-based business (high value)")
        
        if components['has_active_marketing'] > 0.5:
            reasons.append("Active marketing presence")
        else:
            reasons.append("Limited marketing activity")
        
        if pain_points:
            reasons.append(f"Pain points: {', '.join(pain_points[:2])}")
        
        return "; ".join(reasons)
    
    def _identify_opportunity(self, data: Dict[str, Any], score: int, risk_flags: list) -> str:
        """Identify key opportunity based on score, data, and risks"""
        pain_points = data.get('pain_points', [])
        has_blog = data.get('has_blog', False)
        website_quality = data.get('website_quality', 'average')
        running_ads = data.get('running_ads', False)
        
        opportunities = []
        
        # High-value immediate opportunities
        if score >= 85:
            opportunities.append("🔥 HOT: Immediate revenue opportunity - they need us NOW")
        elif score >= 70:
            opportunities.append("💰 High-value lead ready for proposal")
        
        # Pain point based
        if 'low conversion' in str(pain_points).lower():
            opportunities.append("Conversion optimization - our specialty")
        if 'high cost per lead' in str(pain_points).lower():
            opportunities.append("Can reduce their CAC significantly")
        
        # Activity based
        if running_ads:
            opportunities.append("Already spending on marketing = budget available")
        
        # Gap based
        if not has_blog and score >= 50:
            opportunities.append("Content marketing gap - easy win")
        
        if website_quality in ['poor', 'outdated']:
            opportunities.append("Website rebuild could 2x conversions")
        
        # Risk adjusted
        if risk_flags:
            return opportunities[0] if opportunities else "Qualified but verify: " + risk_flags[0]
        
        return opportunities[0] if opportunities else "Lead generation opportunity"


# Example usage
if __name__ == "__main__":
    import json
    agent = LeadQualificationAgent()
    
    # Example HOT lead
    hot_lead = {
        "company_name": "ScaleUp Agency",
        "industry": "Marketing Services",
        "services": ["lead generation", "appointment setting", "b2b outreach"],
        "target_audience": "SaaS companies and agencies",
        "pain_points": ["low conversion on cold outreach", "high cost per lead", "losing money on ads"],
        "intent_signals": ["actively optimizing", "wants scalable acquisition", "looking for growth partner"],
        "website_quality": "average",
        "has_blog": True,
        "running_ads": True,
        "social_links": {"linkedin": "https://linkedin.com/company/scaleup"}
    }
    
    result = agent.qualify_lead(hot_lead)
    print("=" * 60)
    print("HOT LEAD EXAMPLE")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    print()
    
    # Example COLD lead
    cold_lead = {
        "company_name": "Personal Blog",
        "industry": "",
        "services": [],
        "target_audience": "",
        "pain_points": ["want more readers"],
        "intent_signals": [],
        "website_quality": "poor",
        "has_blog": True,
        "running_ads": False
    }
    
    result2 = agent.qualify_lead(cold_lead)
    print("=" * 60)
    print("COLD LEAD EXAMPLE (should trigger filters)")
    print("=" * 60)
    print(json.dumps(result2, indent=2))
