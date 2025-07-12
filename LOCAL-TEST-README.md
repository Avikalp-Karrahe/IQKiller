# 🧪 Google Document AI Local Testing Suite

This test suite verifies that your Google Document AI integration is working correctly before deploying to Vercel.

## 🚀 Quick Start

### 1. Run Setup Script
```bash
node setup-test-env.js
```
This will:
- Create `.env.local` with your Google credentials
- Check for required dependencies
- Give you next steps

### 2. Install Dependencies (if needed)
```bash
npm install @google-cloud/documentai node-fetch form-data
```

### 3. Start Development Server
```bash
npm run dev
```

### 4. Run Comprehensive Test
```bash
node test-local-google-ai.js
```

## 📊 What the Test Does

### ✅ Environment Check
- Verifies all required environment variables are set
- Checks that the test PDF file exists
- Validates credentials file

### 🔍 API Status Check  
- Tests the GET `/api/extract-pdf` endpoint
- Shows configuration status
- Verifies Google Document AI client initialization

### 📄 PDF Extraction Test
- Uploads the test PDF to your local API
- Measures response time
- Verifies real text extraction (not placeholder)
- Shows extracted text preview

### 🚨 Error Scenario Tests
- Tests invalid file type rejection
- Tests missing file handling
- Tests large file rejection (>10MB)

### ⚡ Performance Test
- Runs 3 extraction attempts
- Measures average, min, max response times
- Evaluates performance rating

## 📋 Expected Output

### ✅ SUCCESS (Google Document AI Working)
```
🧪 === COMPREHENSIVE GOOGLE DOCUMENT AI LOCAL TEST ===

📋 ENVIRONMENT CHECK
✅ GOOGLE_CLOUD_PROJECT_ID: SET
✅ GOOGLE_DOCUMENT_AI_PROCESSOR_ID: SET
✅ GOOGLE_DOCUMENT_AI_LOCATION: SET
✅ GOOGLE_APPLICATION_CREDENTIALS_JSON: SET
✅ Credentials file: ./google-service-account.json EXISTS
✅ Test PDF: 🎯 IQKiller - AI Interview Preparation.pdf (179 KB)

🔍 API STATUS CHECK
✅ Development server is running
✅ API Status Response:
{
  "googleDocumentAI": {
    "configured": true,
    "projectId": "SET",
    "processorId": "SET",
    "location": "us",
    "credentials": "SET",
    "clientInitialized": "YES"
  }
}
✅ Google Document AI is properly configured

📄 PDF EXTRACTION TEST
ℹ️  Testing PDF: 🎯 IQKiller - AI Interview Preparation.pdf
ℹ️  File size: 179 KB
ℹ️  Sending PDF to extraction API...
ℹ️  Request completed in 2340ms
✅ PDF extraction completed!
ℹ️  Extracted text length: 2847 characters
✅ 🎉 SUCCESS: Real Google Document AI extraction!
🔍 Extracted text preview:
"IQKiller - AI Interview Preparation..."

📊 TEST SUMMARY
✅ 🎉 ALL CORE TESTS PASSED!
✅ Google Document AI is working correctly
ℹ️  You can now confidently deploy to Vercel with the same environment variables
```

### ❌ FAILURE (Configuration Issues)
```
📋 ENVIRONMENT CHECK
❌ GOOGLE_APPLICATION_CREDENTIALS_JSON: MISSING
⚠️  Google Document AI is NOT configured
❌ Missing: credentials

📄 PDF EXTRACTION TEST  
⚠️  Using PLACEHOLDER extraction
⚠️  This means Google Document AI is not working properly

❌ CORE TESTS FAILED
❌ - PDF extraction not working with Google Document AI
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Environment Variables Not Set
**Problem**: Missing environment variables
**Solution**: 
```bash
# Re-run setup
node setup-test-env.js

# Or manually create .env.local with:
GOOGLE_CLOUD_PROJECT_ID=big-data-msba-avi
GOOGLE_DOCUMENT_AI_PROCESSOR_ID=8659d2983b90dfde
GOOGLE_DOCUMENT_AI_LOCATION=us
GOOGLE_APPLICATION_CREDENTIALS_JSON={...your-json...}
```

#### 2. Server Not Running
**Problem**: "Development server is not running"
**Solution**:
```bash
npm run dev
# Wait for server to start, then run test again
```

#### 3. Dependencies Missing
**Problem**: "Cannot find module '@google-cloud/documentai'"
**Solution**:
```bash
npm install @google-cloud/documentai node-fetch form-data
```

#### 4. Using Placeholder Text
**Problem**: Test shows "Using PLACEHOLDER extraction"
**Solution**:
- Check environment variables are set correctly
- Verify Google Cloud credentials
- Ensure Document AI API is enabled
- Check processor ID is correct

#### 5. Timeout Errors
**Problem**: Request times out after 30 seconds
**Solution**:
- Try with a smaller PDF
- Check internet connection
- Verify Google Cloud project has proper billing

## 📂 Test Files

- `setup-test-env.js` - Creates `.env.local` with credentials
- `test-local-google-ai.js` - Comprehensive test suite
- `.env.local` - Environment variables (auto-generated)
- `🎯 IQKiller - AI Interview Preparation.pdf` - Test PDF file

## 🎯 Next Steps After Successful Test

1. **Deploy to Vercel**:
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add the same 4 environment variables from your `.env.local`
   - Ensure scope is set to: Production, Preview, Development

2. **Environment Variables for Vercel**:
   ```
   GOOGLE_CLOUD_PROJECT_ID=big-data-msba-avi
   GOOGLE_DOCUMENT_AI_PROCESSOR_ID=8659d2983b90dfde
   GOOGLE_DOCUMENT_AI_LOCATION=us
   GOOGLE_APPLICATION_CREDENTIALS_JSON={...entire-json-from-env-local...}
   ```

3. **Test Production**:
   - Upload a PDF to your live Vercel site
   - Check Vercel Function logs
   - Verify no more hanging issues

## 🛡️ Security Notes

- The `.env.local` file contains sensitive credentials
- Never commit `.env.local` to git
- The credentials are for your Google Cloud service account
- Only use these credentials for this specific project

## 📞 Support

If tests fail after following this guide:

1. Check the error messages carefully
2. Verify Google Cloud Console settings:
   - Document AI API is enabled
   - Service account has proper permissions
   - Processor ID is correct
3. Try with a smaller/different PDF file
4. Check network connectivity 