"""One consistent, evidence-based summary for the app and all report formats."""


def report_summary(result):
    review = result['requirement_review']
    settings = review['settings']
    missing_settings = []
    if settings['minimum_years'] is None:
        missing_settings.append('minimum experience')
    if not settings['accepted_qualifications']:
        missing_settings.append('accepted qualifications')
    missing_details = [c['requirement'] for c in review['checks'] if c['status'] == 'missing']
    required_gaps = result['missing_by_priority']['required']
    status = review['summary']
    if status == 'Meets configured checks':
        status = ('Required skill gaps to review' if required_gaps else
                  'Other skill gaps to review' if result['skills_not_found'] else
                  'Configured checks met; no detected skill gaps')
    actions = []
    if not result['matched_skills'] and not result['skills_not_found']:
        if status == 'Configured checks met; no detected skill gaps':
            status = 'Needs review: no JD skills detected'
        actions.append('Review the JD text and add missing skill names in Extra skills to check; coverage is unavailable until JD skills are detected.')
    if missing_settings:
        actions.append('Complete JD settings: ' + ', '.join(missing_settings) + '.')
    if missing_details:
        actions.append('Add or correct truthful resume details: ' + ', '.join(missing_details) + '.')
    for check in review['checks']:
        if check['status'] == 'not_met':
            actions.append('Review ' + check['requirement'].lower() + ': JD requires ' + check['expected'] + '; resume shows ' + check['observed'] + '.')
    if required_gaps:
        actions.append('Review required skill evidence first: ' + ', '.join(required_gaps) + '. Correct omissions or begin the practice plan.')
    for check in review['checks']:
        if check['status'] == 'review':
            actions.append('Confirm ' + check['requirement'].lower() + ' against the source documents.')
    if result['skills_not_found']:
        actions.append('Use the daily plan for remaining skill gaps; complete the practical self-checks.')
    actions += ['Review the evidence excerpts and correct extraction mistakes before sharing.',
                'Support matched skills with truthful project examples and measurable results.',
                'Download the report and use the JD requirements to prepare your application.']
    return {
        'status': status,
        'mandatory_status': review['summary'],
        'missing_jd_settings': missing_settings,
        'missing_resume_details': missing_details,
        'matched_count': len(result['matched_skills']),
        'job_skill_count': len(result['matched_skills']) + len(result['skills_not_found']),
        'required_gaps': required_gaps,
        'top_actions': actions[:3],
        'score_explanation': 'Skill coverage counts positive resume mentions of detected JD skills. Text similarity compares wording or meaning across the documents. They measure different things and can differ greatly; neither is a hiring probability or verified proficiency.',
        'note': 'This is a document comparison, not a final job-eligibility decision. No skill-percentage acceptance threshold is configured.',
        'input_note': result.get('input_review', {}).get('note', 'Analysis uses the supplied document text without preview corrections.'),
    }
