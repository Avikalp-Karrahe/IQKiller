# Deployment Guide

## Vercel Deployment Setup

The application requires several environment variables to be configured in Vercel for successful deployment.

### Required Environment Variables

#### 1. Supabase Configuration
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 2. OpenAI Configuration
```
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini-2024-07-18
```

#### 3. Stripe Configuration
```
STRIPE_SECRET_KEY=sk_live_... # or sk_test_... for testing
STRIPE_WEBHOOK_SECRET=whsec_...
```

#### 4. Application Configuration
```
NEXT_PUBLIC_BASE_URL=https://your-app.vercel.app
```

### Optional Environment Variables

#### SerpAPI (for job search functionality)
```
SERPAPI_KEY=your_serpapi_key
```

#### Firecrawl API (for web scraping)
```
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

#### Google Cloud Document AI (for PDF processing)
```
GOOGLE_CLOUD_PROJECT_ID=your_project_id
GOOGLE_DOCUMENT_AI_PROCESSOR_ID=your_processor_id
GOOGLE_DOCUMENT_AI_LOCATION=us
```

## Setting Environment Variables in Vercel

1. Go to your Vercel dashboard
2. Select your project
3. Navigate to **Settings** → **Environment Variables**
4. Add each variable with its corresponding value
5. Make sure to set the environment to **Production**, **Preview**, and **Development** as needed

## Current Build Error

The deployment is failing because `STRIPE_SECRET_KEY` is not configured. This is a **required** environment variable for the billing system to work.

### Quick Fix

1. Add the `STRIPE_SECRET_KEY` environment variable in Vercel
2. Redeploy the application

## Database Setup

Make sure to run the Supabase migrations:

```sql
-- Run these in your Supabase SQL editor
-- Files are located in /supabase/migrations/
```

## Stripe Webhook Configuration

1. In your Stripe dashboard, create a webhook endpoint pointing to:
   `https://your-app.vercel.app/api/billing/webhook`

2. Select the following events:
   - `checkout.session.completed`
   - `payment_intent.succeeded`

3. Copy the webhook secret and add it as `STRIPE_WEBHOOK_SECRET` in Vercel

## Testing the Deployment

After setting up all environment variables:

1. Trigger a new deployment in Vercel
2. Check the build logs for any remaining errors
3. Test the authentication flow
4. Test the credit purchase flow (in test mode)

## Troubleshooting

- **Build fails with "Neither apiKey nor config.authenticator provided"**: Missing `STRIPE_SECRET_KEY`
- **Authentication not working**: Check Supabase configuration
- **OpenAI features not working**: Verify `OPENAI_API_KEY`
- **Webhook errors**: Ensure `STRIPE_WEBHOOK_SECRET` matches your Stripe webhook configuration