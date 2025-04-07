def calculate_brain_health_score(cognitive_score, lifestyle_data):
    # Basic scoring: just average everything for now
    lifestyle_values = list(lifestyle_data.values())
    lifestyle_average = sum(lifestyle_values) / len(lifestyle_values)
    return (cognitive_score + lifestyle_average) / 2

def generate_recommendations(score, lifestyle_data):
    # Simple mock recommendations
    recs = []
    if lifestyle_data.get('smoking', 0) > 0:
        recs.append({
            'category': 'Health',
            'title': 'Reduce Smoking',
            'description': 'Cutting back on smoking can significantly improve brain and heart health.',
            'priority': 'High'
        })
    if lifestyle_data.get('good_sleep', 0) < 3:
        recs.append({
            'category': 'Sleep',
            'title': 'Improve Sleep',
            'description': 'Try to get at least 7-8 hours of good sleep consistently.',
            'priority': 'Medium'
        })
    return recs
