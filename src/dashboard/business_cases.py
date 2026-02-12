"""
Business Cases Configuration
Defines the selected business cases for analysis
"""

# Business Case Definitions
BUSINESS_CASES = {
    "case_1": {
        "id": "case_1",
        "title": "Decoding Transaction Dynamics",
        "description": "Analyze transaction patterns, growth trends, and payment category performance to understand the digital payment landscape.",
        "key_questions": [
            "What are the year-over-year transaction growth rates?",
            "Which transaction types drive the highest value?",
            "Are there seasonal patterns in digital payments?",
            "Which states show declining transaction trends?"
        ],
        "enabled": True
    },
    "case_2": {
        "id": "case_2",
        "title": "Device Dominance & User Engagement",
        "description": "Examine device brand preferences, market share distribution, and user engagement patterns across regions.",
        "key_questions": [
            "Which device brands dominate the digital payment market?",
            "How does device preference vary by region?",
            "What is the relationship between device brand and user engagement?",
            "Are there emerging device brands gaining market share?"
        ],
        "enabled": True
    },
    "case_4": {
        "id": "case_4",
        "title": "Transaction Analysis for Market Expansion",
        "description": "Identify high-performing states, emerging markets, and untapped opportunities for strategic expansion.",
        "key_questions": [
            "Which states have the highest transaction volumes?",
            "Where are the emerging high-growth markets?",
            "What is the digital payment penetration by state?",
            "Which regions offer the best expansion opportunities?"
        ],
        "enabled": True
    },
    "case_5": {
        "id": "case_5",
        "title": "User Engagement and Growth Strategy",
        "description": "Analyze user growth trends, retention patterns, and engagement metrics to inform growth strategies.",
        "key_questions": [
            "What are the user growth trends across different periods?",
            "Which states have the highest user engagement?",
            "How do user retention patterns vary?",
            "What factors drive consistent user engagement?"
        ],
        "enabled": True
    },
    "case_7": {
        "id": "case_7",
        "title": "Transaction Analysis Across States and Districts",
        "description": "Deep dive into state and district-level transaction performance, identifying top performers and growth opportunities.",
        "key_questions": [
            "Which are the top 10 states by transaction volume?",
            "How concentrated is transaction activity?",
            "What is the performance scorecard for each state?",
            "How do year-over-year comparisons look across states?"
        ],
        "enabled": True
    }
}

def get_selected_cases():
    """Return only enabled business cases"""
    return {k: v for k, v in BUSINESS_CASES.items() if v.get("enabled", False)}

def get_case_by_id(case_id):
    """Get a specific business case by ID"""
    return BUSINESS_CASES.get(case_id)

def get_all_cases():
    """Return all business cases"""
    return BUSINESS_CASES
