# ChemEng Toolbox: Deployment Guide (Cost-Optimized)

## Overview

This guide covers deploying ChemEng Toolbox with **zero ongoing costs** using free tier services. Two deployment options:

1. **Static Site Only** (Recommended) — $0/month
2. **With Optional Backend** — $0-5/month (AWS free tier)

---

## Option 1: Static Site Deployment (FREE)

### Prerequisites

- GitHub account (free)
- Node.js 20+ installed
- Git installed

### Step 1: Fork Repository

```bash
# Fork on GitHub, then clone
git clone https://github.com/yourusername/chemeng-toolbox.git
cd chemeng-toolbox
```

### Step 2: Build Web Application

```bash
cd web
npm install
npm run build
npm run export  # Generates static files in ./out
```

### Step 3: Deploy to GitHub Pages

**Option A: Via GitHub Actions (Automatic)**

1. Go to repository Settings → Pages
2. Source: GitHub Actions
3. Push to main branch triggers deployment

```yaml
# .github/workflows/deploy.yml (already configured)
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: |
          cd web
          npm ci
          npm run build
          npm run export
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./web/out
```

**Option B: Manual Deploy**

```bash
cd web
npm run deploy  # Uses gh-pages package
```

### Step 4: Access Your Site

Your site is now live at:
```
https://yourusername.github.io/chemeng-toolbox
```

### Custom Domain (Optional, $12/year)

1. Buy domain from Namecheap/Google Domains
2. Add CNAME file to web/public:
   ```
   chemeng.yourdomain.com
   ```
3. Configure DNS:
   ```
   CNAME chemeng.yourdomain.com yourusername.github.io
   ```
4. Enable HTTPS in GitHub Pages settings

**Total Cost: $0/month (or $12/year with custom domain)**

---

## Option 2: With Backend API (AWS Free Tier)

### Prerequisites

- AWS account (free tier)
- AWS CLI configured
- SAM CLI installed
- Python 3.11+

### Step 1: Configure AWS Credentials

```bash
aws configure
# AWS Access Key ID: [your-key]
# AWS Secret Access Key: [your-secret]
# Default region: us-east-1
# Default output format: json
```

### Step 2: Deploy Backend with SAM

```bash
cd backend

# First time deployment
sam build
sam deploy --guided

# Follow prompts:
# Stack Name: chemeng-toolbox
# AWS Region: us-east-1
# Confirm changes before deploy: Y
# Allow SAM CLI IAM role creation: Y
# Save arguments to config file: Y
```

### Step 3: Note Your API Endpoint

After deployment, SAM outputs:
```
CloudFormation outputs:
ApiEndpoint: https://abc123.execute-api.us-east-1.amazonaws.com/
```

### Step 4: Update Frontend Configuration

```bash
cd web
# Edit .env.production
echo "NEXT_PUBLIC_API_URL=https://abc123.execute-api.us-east-1.amazonaws.com" > .env.production

# Rebuild and deploy
npm run build
npm run deploy
```

### Step 5: Test API

```bash
# Test thermodynamics endpoint
curl -X POST https://abc123.execute-api.us-east-1.amazonaws.com/v1/thermo/eos/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "peng_robinson",
    "compound": "methane",
    "temperature": 300,
    "pressure": 1000000
  }'
```

**Expected Response:**
```json
{
  "compressibility_factor": 0.9876,
  "fugacity": 987600,
  "calculation_time_ms": 12
}
```

---

## Infrastructure Details

### AWS Resources Created

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AWS FREE TIER RESOURCES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  API Gateway HTTP API                                                       │
│  ├── Endpoint: /v1/thermo/*                                                 │
│  ├── Endpoint: /v1/fluids/*                                                 │
│  └── Endpoint: /v1/heat/*                                                   │
│  Free: 1M requests/month (12 months)                                        │
│  After 12 months: $1.00 per million requests                                │
│                                                                             │
│  Lambda Functions                                                           │
│  ├── chemeng-thermo (512MB, ARM64)                                          │
│  ├── chemeng-fluids (256MB, ARM64)                                          │
│  └── chemeng-heat (256MB, ARM64)                                            │
│  Free: 1M requests/month, 400K GB-seconds                                   │
│  Estimated usage: ~25K calculations/month = FREE                            │
│                                                                             │
│  DynamoDB Table: calculations                                               │
│  ├── Partition Key: user_id                                                 │
│  ├── Sort Key: calc_id                                                      │
│  └── Billing: On-demand                                                     │
│  Free: 25GB storage, 25 RCU/WCU                                             │
│  Estimated usage: ~1GB = FREE                                               │
│                                                                             │
│  S3 Bucket: chemeng-reports-{AccountId}                                     │
│  └── Storage: PDF exports, CSV data                                         │
│  Free: 5GB storage, 20K GET, 2K PUT                                         │
│  Estimated usage: ~500MB = FREE                                             │
│                                                                             │
│  CloudWatch Logs                                                            │
│  └── Log retention: 7 days                                                  │
│  Free: 5GB logs/month                                                       │
│  Estimated usage: ~100MB = FREE                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

TOTAL MONTHLY COST: $0 (within free tier)
```

### Cost Monitoring Setup

**Set Budget Alerts:**

```bash
# Create budget alert at $5
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget file://budget.json

# budget.json
{
  "BudgetName": "chemeng-monthly-budget",
  "BudgetLimit": {
    "Amount": "5",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

**Check Current Costs:**
```bash
# View month-to-date costs
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

---

## SAM Template Configuration

### backend/template.yaml

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: ChemEng Toolbox Serverless API

Globals:
  Function:
    Timeout: 30
    Runtime: python3.11
    Architectures:
      - arm64  # 20% cheaper than x86
    MemorySize: 512  # Optimized for cost
    Environment:
      Variables:
        POWERTOOLS_SERVICE_NAME: chemeng
        LOG_LEVEL: INFO

Resources:
  # API Gateway
  ChemEngApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      StageName: v1
      CorsConfiguration:
        AllowOrigins:
          - "https://yourusername.github.io"
          - "http://localhost:3000"
        AllowMethods:
          - GET
          - POST
          - OPTIONS
        AllowHeaders:
          - Content-Type

  # Thermodynamics Function
  ThermoFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: functions/thermo/
      Handler: handler.lambda_handler
      Events:
        ThermoApi:
          Type: HttpApi
          Properties:
            ApiId: !Ref ChemEngApi
            Path: /thermo/{proxy+}
            Method: ANY

  # Fluids Function
  FluidsFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: functions/fluids/
      Handler: handler.lambda_handler
      MemorySize: 256  # Lighter calculations
      Events:
        FluidsApi:
          Type: HttpApi
          Properties:
            ApiId: !Ref ChemEngApi
            Path: /fluids/{proxy+}
            Method: ANY

  # DynamoDB Table
  CalculationsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: chemeng-calculations
      BillingMode: PAY_PER_REQUEST  # No minimum cost
      AttributeDefinitions:
        - AttributeName: user_id
          AttributeType: S
        - AttributeName: calc_id
          AttributeType: S
      KeySchema:
        - AttributeName: user_id
          KeyType: HASH
        - AttributeName: calc_id
          KeyType: RANGE
      TimeToLiveSpecification:
        Enabled: true
        AttributeName: ttl  # Auto-delete old calculations

  # S3 Bucket
  ReportsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub chemeng-reports-${AWS::AccountId}
      LifecycleConfiguration:
        Rules:
          - Id: DeleteOldReports
            Status: Enabled
            ExpirationInDays: 30  # Auto-delete after 30 days

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ChemEngApi}.execute-api.${AWS::Region}.amazonaws.com"
```

---

## Lambda Function Structure

### backend/functions/thermo/handler.py

```python
import json
import time
from typing import Dict, Any
from chemeng_thermo.eos import PengRobinson

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for thermodynamics calculations.
    
    Cost optimization:
    - ARM64 architecture (20% cheaper)
    - Minimal cold start dependencies
    - Efficient memory usage
    """
    start_time = time.time()
    
    try:
        # Parse input
        body = json.loads(event.get('body', '{}'))
        model = body['model']
        compound = body['compound']
        T = body['temperature']
        P = body['pressure']
        
        # Perform calculation
        if model == 'peng_robinson':
            eos = PengRobinson(compound)
            result = eos.calculate(T=T, P=P)
            
            response_body = {
                'compressibility_factor': result.Z,
                'fugacity': result.fugacity,
                'calculation_time_ms': int((time.time() - start_time) * 1000)
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response_body)
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unknown model: {model}'})
            }
            
    except Exception as e:
        print(f"ERROR: {str(e)}")  # CloudWatch logs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### backend/functions/thermo/requirements.txt

```txt
# Core dependencies only (minimize cold start)
numpy==1.24.4
scipy==1.11.4
pint==0.23

# Local package (deployed as Lambda Layer)
# chemeng-core is in a separate layer
```

---

## Deployment Automation

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend to AWS

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: aws-actions/setup-sam@v2
      
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: SAM Build
        run: |
          cd backend
          sam build
      
      - name: SAM Deploy
        run: |
          cd backend
          sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
```

### Makefile for Local Development

```makefile
# backend/Makefile

.PHONY: build deploy local test clean

build:
	sam build

deploy: build
	sam deploy --no-confirm-changeset

local: build
	sam local start-api --port 3001

test:
	pytest tests/ -v

clean:
	rm -rf .aws-sam

# Quick commands
dev: local
push: deploy
```

**Usage:**
```bash
cd backend
make dev     # Start local API
make test    # Run tests
make push    # Deploy to AWS
```

---

## Monitoring (Free Tier)

### CloudWatch Dashboard

**Create Simple Dashboard:**

```bash
aws cloudwatch put-dashboard \
  --dashboard-name ChemEngMetrics \
  --dashboard-body file://dashboard.json
```

**dashboard.json:**
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Invocations", {"stat": "Sum"}],
          [".", "Errors", {"stat": "Sum"}],
          [".", "Duration", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "Lambda Metrics"
      }
    }
  ]
}
```

### Cost-Free Monitoring

**CloudWatch Logs Insights Queries:**

```bash
# Find slow calculations
fields @timestamp, duration
| filter ispresent(duration)
| sort duration desc
| limit 10

# Error rate
fields @timestamp
| filter @message like /ERROR/
| stats count() as errors by bin(5m)

# Most popular calculations
fields @timestamp, compound
| stats count() by compound
| sort count desc
```

**Cost:** $0 (within free tier 5GB logs)

---

## Scaling & Optimization

### When You Exceed Free Tier

**Signs you're approaching limits:**
- API Gateway: approaching 1M requests/month
- Lambda: approaching 400K GB-seconds
- DynamoDB: frequent throttling

### Optimization Strategies

**1. Add Caching (Still Free)**

Use Upstash Redis (free tier: 10K requests/day)

```python
import redis

# Connect to Upstash Redis
r = redis.from_url(os.environ['REDIS_URL'])

def lambda_handler(event, context):
    # Check cache
    cache_key = f"calc:{hash(event['body'])}"
    cached = r.get(cache_key)
    if cached:
        return {'statusCode': 200, 'body': cached}
    
    # Calculate
    result = calculate(event)
    
    # Cache for 1 hour
    r.setex(cache_key, 3600, json.dumps(result))
    return result
```

**2. Optimize Lambda Memory**

```bash
# Test different memory settings
for mem in 256 512 1024; do
  sam deploy --parameter-overrides MemorySize=$mem
  # Run load test
  # Measure cost vs performance
done
```

**3. Use Lambda Layers**

```yaml
# Reduce deployment package size
Layers:
  ChemEngCore:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: chemeng-core
      ContentUri: layers/core/
      CompatibleRuntimes:
        - python3.11
```

**4. Enable DynamoDB Point-in-Time Recovery**

Only if you need it (costs ~$0.20/GB/month)

---

## Backup & Disaster Recovery

### Free Backup Strategy

**1. Code Backup**
- Already on GitHub (automatic)

**2. DynamoDB Backup**

```bash
# Export to S3 (free within AWS)
aws dynamodb export-table-to-point-in-time \
  --table-arn arn:aws:dynamodb:us-east-1:123456789:table/chemeng-calculations \
  --s3-bucket chemeng-backups-123456789 \
  --export-format DYNAMODB_JSON
```

**3. Infrastructure as Code**
- SAM template in git (automatic)

### Disaster Recovery Plan

**RTO (Recovery Time Objective):** 1 hour
**RPO (Recovery Point Objective):** 24 hours

**Recovery Steps:**
```bash
# 1. Restore from git
git clone backup-repo
cd chemeng-toolbox

# 2. Redeploy infrastructure
cd backend
sam deploy

# 3. Restore DynamoDB data (if needed)
aws dynamodb import-table --input-format DYNAMODB_JSON ...

# 4. Verify
curl https://new-api-id.execute-api.us-east-1.amazonaws.com/v1/health
```

---

## Teardown (Cleanup)

### Remove All AWS Resources

```bash
# Delete CloudFormation stack
sam delete

# Confirm deletion
# This removes:
# - Lambda functions
# - API Gateway
# - DynamoDB table
# - S3 bucket (if empty)
# - CloudWatch logs (after retention period)
```

### Remove GitHub Pages Deployment

```bash
# Remove gh-pages branch
git push origin --delete gh-pages

# Disable GitHub Pages in repo settings
```

**Result:** $0/month, no resources running

---

## Troubleshooting

### Common Issues

**1. SAM Deploy Fails**

```bash
# Error: Unable to upload artifact
# Solution: Reduce package size

# Check function size
du -sh functions/thermo/

# Remove unnecessary files
rm -rf functions/thermo/__pycache__
rm -rf functions/thermo/.pytest_cache
```

**2. Lambda Cold Starts**

```bash
# Monitor cold starts
aws logs tail /aws/lambda/chemeng-thermo --follow

# If >1s cold starts, consider:
# - Reduce dependencies
# - Use Lambda layers
# - Optimize imports (lazy loading)
```

**3. API Gateway CORS Errors**

```yaml
# Update template.yaml
CorsConfiguration:
  AllowOrigins:
    - "https://yourusername.github.io"
    - "http://localhost:3000"
  AllowMethods:
    - GET
    - POST
    - OPTIONS
  AllowHeaders:
    - Content-Type
    - Authorization
```

**4. DynamoDB Throttling**

```bash
# Check for throttling
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name UserErrors \
  --dimensions Name=TableName,Value=chemeng-calculations \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-31T23:59:59Z \
  --period 3600 \
  --statistics Sum

# Solution: Already using on-demand billing (auto-scales)
```

---

## Production Checklist

Before making backend publicly available:

- [ ] Set up budget alerts
- [ ] Enable CloudWatch alarms
- [ ] Configure API rate limiting
- [ ] Add authentication (if needed)
- [ ] Set up monitoring dashboard
- [ ] Document API endpoints
- [ ] Add health check endpoint
- [ ] Test disaster recovery
- [ ] Review IAM permissions
- [ ] Enable AWS CloudTrail

---

## Cost Summary

### Static Site Only

| Service | Cost |
|---------|------|
| GitHub Pages | $0 |
| Domain (optional) | $12/year |
| **Total** | **$0-1/month** |

### With Backend API

| Service | Free Tier | Expected Usage | Cost |
|---------|-----------|----------------|------|
| Lambda | 1M requests/month | ~25K/month | $0 |
| API Gateway | 1M requests/month | ~25K/month | $0 |
| DynamoDB | 25GB, 25 RCU/WCU | ~1GB, <5 RCU/WCU | $0 |
| S3 | 5GB, 20K GET | ~500MB, <1K GET | $0 |
| CloudWatch | 5GB logs | ~100MB | $0 |
| **Total** | | | **$0/month** |

**After 12 months (API Gateway free tier ends):**
- 25K requests/month = 0.025M requests
- Cost: 0.025M × $1.00/M = **$0.03/month**

**Even at 100K requests/month:**
- Cost: 0.1M × $1.00/M = **$0.10/month**

---

## Next Steps

1. **Deploy static site first** (zero risk, zero cost)
2. **Test locally** before deploying backend
3. **Monitor costs** with budget alerts
4. **Scale gradually** as usage grows
5. **Accept contributions** to reduce solo workload

**Recommended Path:** Start with static-only, add backend later if needed
