# Job Description and Resume Matcher

A Python application that processes job descriptions and resumes to provide hiring recommendations using Anthropic AI and AWS S3.

## Features

- Extracts key skills, years of experience, and role seniority from job descriptions using Anthropic API
- Analyzes candidate resumes against job requirements
- Calculates a fit score (0-100) for each candidate
- Generates hiring recommendations (Strong Fit, Medium Fit, or Weak Fit)
- Provides detailed reasoning for recommendations
- Saves results to AWS S3 with timestamps
- Outputs results to console in JSON format

## Requirements

- Python 3.7 or higher
- Anthropic API key
- AWS account with S3 access
- AWS credentials (Access Key ID and Secret Access Key)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/shriramraj/simple-python-app.git
cd simple-python-app
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Setting Up Environment Variables

You need to set the following environment variables before running the application:

#### Required Variables:

1. **ANTHROPIC_API_KEY**: Your Anthropic API key
   - Get your API key from: https://console.anthropic.com/
   
2. **AWS_ACCESS_KEY_ID**: Your AWS Access Key ID
   - Get from AWS IAM Console: https://console.aws.amazon.com/iam/
   
3. **AWS_SECRET_ACCESS_KEY**: Your AWS Secret Access Key
   - Get from AWS IAM Console (same place as Access Key)
   
4. **S3_BUCKET_NAME**: Name of your S3 bucket where results will be saved
   - Create a bucket in AWS S3 Console: https://console.aws.amazon.com/s3/

#### Optional Variables:

5. **AWS_REGION**: AWS region for S3 (default: us-east-1)
   - Example: us-west-2, eu-west-1, etc.

### Setting Environment Variables

#### On Linux/macOS:
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export AWS_ACCESS_KEY_ID="your-aws-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-access-key"
export S3_BUCKET_NAME="your-s3-bucket-name"
export AWS_REGION="us-east-1"  # Optional
```

#### On Windows (Command Prompt):
```cmd
set ANTHROPIC_API_KEY=your-anthropic-api-key
set AWS_ACCESS_KEY_ID=your-aws-access-key-id
set AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
set S3_BUCKET_NAME=your-s3-bucket-name
set AWS_REGION=us-east-1
```

#### On Windows (PowerShell):
```powershell
$env:ANTHROPIC_API_KEY="your-anthropic-api-key"
$env:AWS_ACCESS_KEY_ID="your-aws-access-key-id"
$env:AWS_SECRET_ACCESS_KEY="your-aws-secret-access-key"
$env:S3_BUCKET_NAME="your-s3-bucket-name"
$env:AWS_REGION="us-east-1"
```

#### Using a .env file (recommended for development):
You can also create a `.env` file in the project directory (make sure to add it to .gitignore):
```
ANTHROPIC_API_KEY=your-anthropic-api-key
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
S3_BUCKET_NAME=your-s3-bucket-name
AWS_REGION=us-east-1
```

Then load it using python-dotenv:
```bash
pip install python-dotenv
```

And add to the top of job_matcher.py:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Usage

Run the application:
```bash
python job_matcher.py
```

The application will:
1. Process the sample job description and resume (included in the code)
2. Extract job requirements using Anthropic AI
3. Analyze candidate fit
4. Calculate a fit score and generate a recommendation
5. Save results to your S3 bucket with a timestamp
6. Display the results in the console

### Output Format

The application outputs JSON with the following structure:
```json
{
  "timestamp": "2024-01-16T12:30:45.123456",
  "job_requirements": {
    "skills": ["Python", "Django", "AWS", "..."],
    "years_of_experience": 5,
    "seniority": "Senior"
  },
  "fit_score": 85,
  "matched_skills": ["Python", "Django", "AWS", "Docker"],
  "recommendation": "Strong Fit",
  "reasoning": [
    "Candidate has 7+ years of experience exceeding the 5-year requirement",
    "Strong match on key technical skills including Python, Django, and AWS",
    "Demonstrated experience with required technologies in production environments"
  ]
}
```

## Customization

To analyze different job descriptions and resumes, modify the `job_description` and `resume` variables in the `main()` function of `job_matcher.py`.

## AWS S3 Setup

1. Create an S3 bucket in your AWS account
2. Ensure your IAM user has permissions to write to the bucket:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:PutObject",
           "s3:GetObject"
         ],
         "Resource": "arn:aws:s3:::your-bucket-name/*"
       }
     ]
   }
   ```

## Security Notes

- Never commit your API keys or AWS credentials to version control
- Use environment variables or secure credential management systems
- Rotate your API keys and AWS credentials regularly
- Use IAM roles when running on AWS infrastructure (EC2, Lambda, etc.)

## License

MIT License
