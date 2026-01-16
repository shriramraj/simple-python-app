#!/usr/bin/env python3
"""
Job Description and Resume Matcher
Analyzes job descriptions and resumes to provide hiring recommendations using Anthropic AI.
"""

import os
import json
from datetime import datetime, timezone
import anthropic
import boto3
from botocore.exceptions import ClientError


def parse_json_from_response(response_text: str) -> dict:
    """
    Extract and parse JSON from AI response text.
    
    Args:
        response_text: Response text that may contain JSON in code blocks
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        ValueError: If JSON cannot be extracted or parsed
    """
    try:
        # Try to extract JSON from code blocks
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text.strip()
        
        return json.loads(json_str)
    except (json.JSONDecodeError, IndexError) as e:
        raise ValueError(f"Failed to parse JSON from AI response: {e}\nResponse: {response_text[:200]}...")


def extract_job_requirements(job_description: str, api_key: str) -> dict:
    """
    Extract key skills, years of experience, and role seniority from job description.
    
    Args:
        job_description: Raw job description text
        api_key: Anthropic API key
        
    Returns:
        Dictionary with skills, experience, and seniority
    """
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""Analyze the following job description and extract:
1. Key skills required (list them)
2. Years of experience required (as a number)
3. Role seniority level (Junior, Mid-Level, Senior, or Lead)

Job Description:
{job_description}

Provide your response in JSON format with keys: "skills" (array), "years_of_experience" (number), "seniority" (string)."""
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text
    return parse_json_from_response(response_text)


def analyze_candidate_fit(job_requirements: dict, resume: str, api_key: str) -> dict:
    """
    Analyze how well a candidate's resume matches the job requirements.
    
    Args:
        job_requirements: Dictionary with job requirements
        resume: Raw resume text
        api_key: Anthropic API key
        
    Returns:
        Dictionary with fit_score, matched_skills, recommendation, and reasoning
    """
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""Analyze how well this candidate matches the job requirements.

Job Requirements:
- Skills: {', '.join(job_requirements['skills'])}
- Years of Experience: {job_requirements['years_of_experience']}
- Seniority: {job_requirements['seniority']}

Candidate Resume:
{resume}

Provide your analysis in JSON format with:
1. "fit_score": A number from 0-100 indicating overall fit
2. "matched_skills": Array of skills from the requirements that the candidate has
3. "recommendation": One of "Strong Fit", "Medium Fit", or "Weak Fit"
4. "reasoning": Array of exactly 3 bullet points explaining the recommendation"""
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text
    return parse_json_from_response(response_text)


def save_to_s3(result: dict, bucket_name: str, aws_access_key: str, aws_secret_key: str, aws_region: str) -> str:
    """
    Save the analysis result to AWS S3 with a timestamp.
    
    Args:
        result: Dictionary containing the analysis result
        bucket_name: S3 bucket name
        aws_access_key: AWS access key ID
        aws_secret_key: AWS secret access key
        aws_region: AWS region
        
    Returns:
        S3 object key (filename)
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )
    
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    object_key = f"job_match_results_{timestamp}.json"
    
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=json.dumps(result, indent=2),
            ContentType='application/json'
        )
        print(f"✓ Successfully saved to S3: s3://{bucket_name}/{object_key}")
        return object_key
    except ClientError as e:
        print(f"✗ Error saving to S3: {e}")
        raise


def main():
    """
    Main function to orchestrate the job matching workflow.
    """
    # Load configuration from environment variables
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    
    # Validate required environment variables
    if not anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    if not aws_access_key or not aws_secret_key:
        raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables are required")
    if not s3_bucket:
        raise ValueError("S3_BUCKET_NAME environment variable is required")
    
    # Sample job description (in a real application, this would be provided as input)
    job_description = """
    Senior Software Engineer - Python
    
    We are looking for an experienced Python developer to join our backend team.
    
    Requirements:
    - 5+ years of software development experience
    - Strong proficiency in Python and Django
    - Experience with AWS services (S3, Lambda, EC2)
    - Knowledge of RESTful API design
    - Experience with SQL and NoSQL databases
    - Familiarity with Docker and Kubernetes
    - Strong problem-solving skills
    - Bachelor's degree in Computer Science or related field
    """
    
    # Sample resume (in a real application, this would be provided as input)
    resume = """
    John Doe
    Software Engineer
    
    EXPERIENCE:
    Senior Software Engineer at Tech Corp (2019-Present)
    - Developed Python/Django applications for e-commerce platform
    - Built RESTful APIs serving 1M+ requests per day
    - Implemented AWS Lambda functions for serverless architecture
    - Managed PostgreSQL and MongoDB databases
    - Deployed applications using Docker and Kubernetes
    
    Software Engineer at StartupXYZ (2016-2019)
    - Built web applications using Python and Flask
    - Worked with AWS services including S3 and EC2
    - Implemented CI/CD pipelines
    
    EDUCATION:
    B.S. in Computer Science, State University (2016)
    
    SKILLS:
    Python, Django, Flask, AWS, Docker, Kubernetes, PostgreSQL, MongoDB, REST APIs
    """
    
    print("=" * 80)
    print("JOB DESCRIPTION AND RESUME MATCHER")
    print("=" * 80)
    print()
    
    # Step 1: Extract job requirements
    print("Step 1: Extracting job requirements...")
    job_requirements = extract_job_requirements(job_description, anthropic_api_key)
    print(f"✓ Extracted requirements:")
    print(f"  - Skills: {', '.join(job_requirements['skills'][:5])}...")
    print(f"  - Experience: {job_requirements['years_of_experience']} years")
    print(f"  - Seniority: {job_requirements['seniority']}")
    print()
    
    # Step 2: Analyze candidate fit
    print("Step 2: Analyzing candidate fit...")
    analysis = analyze_candidate_fit(job_requirements, resume, anthropic_api_key)
    print(f"✓ Analysis complete")
    print()
    
    # Step 3: Prepare final result
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "job_requirements": job_requirements,
        "fit_score": analysis["fit_score"],
        "matched_skills": analysis["matched_skills"],
        "recommendation": analysis["recommendation"],
        "reasoning": analysis["reasoning"]
    }
    
    # Step 4: Display results
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(json.dumps(result, indent=2))
    print()
    
    # Step 5: Save to S3
    print("Step 5: Saving results to S3...")
    save_to_s3(result, s3_bucket, aws_access_key, aws_secret_key, aws_region)
    print()
    
    print("=" * 80)
    print("PROCESS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
