# Deployment Instructions: Vercel + Hugging Face Spaces

This document provides step-by-step instructions for deploying the Todo Web Application using Vercel for the frontend and Hugging Face Spaces for the backend.

## Architecture

This application follows a decoupled architecture:
- **Frontend**: Next.js application hosted on Vercel
- **Backend**: FastAPI application hosted on Hugging Face Spaces
- **Database**: PostgreSQL (can be hosted on Neon, Supabase, or other providers)

## Prerequisites

- GitHub account
- Vercel account ([signup](https://vercel.com/signup))
- Hugging Face account ([signup](https://huggingface.co/join))
- Git installed locally
- Basic familiarity with environment variables

## Deployment Process

### Part 1: Deploy Backend to Hugging Face Spaces

1. **Create a Hugging Face Space**
   - Go to [huggingface.co/new-space](https://huggingface.co/new-space)
   - Choose these settings:
     - **Space name**: `your-username/todo-backend`
     - **SDK**: Docker
     - **Hardware**: CPU Basic (or higher)
     - **Visibility**: Public (or Private)

2. **Configure the Space**
   - After creation, go to your Space repository
   - Replace the contents with the backend files from `apps/backend/`
   - Make sure to include:
     - `Dockerfile.hf` (or update the default Dockerfile)
     - `requirements.txt`
     - All backend source code in `src/` directory
     - `app.py` for Hugging Face compatibility

3. **Set Environment Variables**
   In your Space settings, add these environment variables:
   ```
   DATABASE_URL=postgresql://username:password@your-db-url.com:5432/dbname
   SECRET_KEY=generate-a-very-long-random-string-for-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=production
   DEBUG=False
   ```

4. **Wait for Build**
   - The Space will automatically build when you push changes
   - Check the "Logs" tab to monitor the build process
   - Once complete, your backend API will be available at:
     `https://your-username-todo-backend.hf.space`

### Part 2: Deploy Frontend to Vercel

1. **Prepare Your Repository**
   - Make sure your frontend code is in the `apps/frontend/` directory
   - The main Next.js application should be deployable as a standalone project

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Connect to your GitHub repository containing the todo app
   - Vercel should automatically detect it's a Next.js project
   - Use these build settings:
     - **Build Command**: `npm run build`
     - **Output Directory**: (leave empty, Next.js handles this)

3. **Set Environment Variables**
   In Vercel Project Settings → Environment Variables:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-username-todo-backend.hf.space
   NODE_ENV=production
   ```

4. **Complete Deployment**
   - Vercel will build and deploy your frontend
   - Your application will be available at `https://your-project-name.vercel.app`

### Part 3: Connect Frontend to Backend

1. **Verify Connection**
   - Update `NEXT_PUBLIC_API_BASE_URL` to match your Hugging Face backend URL
   - The format should be: `https://your-username-todo-backend.hf.space`
   - Note: Hugging Face Spaces URLs follow the pattern: `https://your-username-project-name.hf.space`

2. **Test the Integration**
   - Visit your Vercel frontend URL
   - Register a new account
   - Verify that todos are properly created and managed through the backend API

## Configuration Details

### Backend Environment Variables (Hugging Face Spaces)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL database connection string | `postgresql://user:pass@ep-xyz.us-east-1.aws.neon.tech/dbname` |
| `SECRET_KEY` | JWT secret key (at least 32 chars) | `very-long-random-string-change-in-production` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `ENVIRONMENT` | Environment name | `production` |
| `DEBUG` | Debug mode | `False` |

### Frontend Environment Variables (Vercel)

| Variable | Description | Value |
|----------|-------------|-------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL | `https://your-username-todo-backend.hf.space` |
| `NODE_ENV` | Node environment | `production` |

## Security Considerations

1. **Secret Keys**: Never use default or weak secret keys in production
2. **HTTPS**: Both Vercel and Hugging Face provide HTTPS by default
3. **CORS**: The backend is configured to accept requests from your Vercel domain
4. **JWT Tokens**: Properly configured with expiration and secure signing

## Updating Deployments

### Backend Updates
1. Make changes to your backend code
2. Push changes to your Hugging Face Space repository
3. The space will automatically rebuild

### Frontend Updates
1. Make changes to your frontend code
2. Push changes to your GitHub repository
3. Vercel will automatically deploy changes

## Troubleshooting

### Common Issues

1. **API calls failing from frontend**:
   - Check that `NEXT_PUBLIC_API_BASE_URL` is set correctly in Vercel
   - Verify the backend is responding at the Hugging Face URL

2. **CORS errors**:
   - Verify your Vercel domain is in the backend's allowed origins
   - Check that your backend is properly configured

3. **Database connection issues**:
   - Verify your `DATABASE_URL` is correctly formatted
   - Check that your database allows connections from Hugging Face Spaces

4. **Authentication failures**:
   - Confirm JWT settings match between frontend and backend
   - Check that the secret key is the same in both environments

### Debugging Steps

1. Check logs in both Vercel and Hugging Face Spaces dashboards
2. Verify all environment variables are set correctly
3. Test API endpoints directly using the backend's `/docs` interface
4. Use browser developer tools to inspect network requests

## Performance Tips

- **Backend**: Use a production-ready database (PostgreSQL recommended)
- **Frontend**: Leverage Vercel's global CDN for fast asset delivery
- **Database**: Enable connection pooling and proper indexing
- **Caching**: The setup includes Redis configuration for performance

## Scaling Considerations

- **Frontend**: Vercel automatically scales based on traffic
- **Backend**: Hugging Face Spaces can scale vertically with hardware upgrades
- **Database**: Use a managed PostgreSQL service with auto-scaling
- **Caching**: Redis is configured for session and data caching

## Support

If you encounter issues:
1. Check the deployment logs in both Vercel and Hugging Face dashboards
2. Verify all environment variables are correctly set
3. Confirm your database is accessible and properly configured
4. Review the API documentation at your backend URL `/docs`

---

Your Todo Web Application is now ready for deployment on Vercel and Hugging Face Spaces! 🚀