# Deployment Guide: Vercel + Hugging Face Spaces

This guide explains how to deploy the Todo Web Application using Vercel for the frontend and Hugging Face Spaces for the backend.

## Prerequisites

- GitHub account
- Vercel account
- Hugging Face account
- Git installed locally
- Node.js and npm installed

## Deployment Steps

### 1. Prepare Your Repository

1. **Fork or clone the repository**:
   ```bash
   git clone https://github.com/your-username/your-todo-app.git
   cd your-todo-app
   ```

2. **Create separate branches for frontend and backend** (recommended):
   ```bash
   # Create backend branch
   git checkout -b backend
   # Remove frontend-specific files (optional)
   git push -u origin backend

   # Go back to main and prepare frontend
   git checkout main
   # Remove backend-specific files (optional)
   git push origin main
   ```

### 2. Deploy Backend to Hugging Face Spaces

1. **Go to your Hugging Face account**:
   - Visit [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"

2. **Configure the Space**:
   - **Name**: `your-username/todo-backend`
   - **SDK**: Docker
   - **Hardware**: CPU Basic (or higher if needed)
   - **Visibility**: Public or Private

3. **Add your repository**:
   ```bash
   # In your backend directory
   cd apps/backend

   # Create/update necessary files for Hugging Face
   # (Dockerfile.hf already created, requirements.txt updated)
   ```

4. **Set environment variables in Hugging Face Spaces settings**:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: A long, random secret key
   - `ALGORITHM`: HS256
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: 30
   - `ENVIRONMENT`: production
   - `DEBUG`: False

5. **Upload the files to Hugging Face**:
   ```bash
   # If using git-lfs
   git clone https://huggingface.co/spaces/your-username/todo-backend
   cd todo-backend

   # Copy backend files
   cp -r /path/to/your/backend/* .

   # Commit and push
   git add .
   git commit -m "Initial backend deployment"
   git push
   ```

### 3. Deploy Frontend to Vercel

1. **Go to Vercel dashboard**:
   - Visit [vercel.com](https://vercel.com)
   - Sign in with GitHub
   - Click "New Project"

2. **Import your repository**:
   - Select your todo application repository
   - Configure the project:
     - **Framework**: Next.js
     - **Build Command**: `npm run build`
     - **Output Directory**: Leave empty (Next.js handles automatically)

3. **Set environment variables in Vercel**:
   - `NEXT_PUBLIC_API_BASE_URL`: Your Hugging Face Spaces backend URL (e.g., `https://your-username-todo-backend.hf.space`)
   - `NODE_ENV`: production

4. **Deploy**:
   - Click "Deploy"
   - Vercel will automatically build and deploy your application

### 4. Configure API Communication

1. **Update the frontend API calls** to point to your backend:
   - In Vercel project settings → Environment Variables:
     - `NEXT_PUBLIC_API_BASE_URL`: `https://your-username-todo-backend.hf.space`

2. **Ensure CORS is configured** in your backend:
   - In your backend settings on Hugging Face, make sure your Vercel domain is in the allowed origins

### 5. Verify the Deployment

1. **Backend verification**:
   - Visit: `https://your-username-todo-backend.hf.space/docs` for API documentation
   - Test health endpoint: `https://your-username-todo-backend.hf.space/health`

2. **Frontend verification**:
   - Visit your Vercel deployment URL
   - Register a new account
   - Verify that authentication and todo operations work correctly

### 6. Production Configuration

#### Environment Variables

**For Hugging Face Spaces (.env file)**:
```env
DATABASE_URL=postgresql://username:password@your-postgres-url.com:5432/dbname
SECRET_KEY=your-very-long-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=False
```

**For Vercel (in dashboard)**:
```env
NEXT_PUBLIC_API_BASE_URL=https://your-username-todo-backend.hf.space
NODE_ENV=production
```

#### Security Considerations

1. **Use strong secret keys** for JWT tokens
2. **Enable HTTPS** for both deployments
3. **Set proper CORS origins** in your backend
4. **Use environment variables** for sensitive data
5. **Monitor your deployments** for unusual activity

### 7. Maintenance

#### Updating Your Applications

**Backend updates**:
1. Make changes to your backend code
2. Push to your Hugging Face Space repository
3. The space will automatically rebuild

**Frontend updates**:
1. Make changes to your frontend code
2. Push to your GitHub repository
3. Vercel will automatically deploy changes

#### Monitoring

- **Hugging Face Spaces**: Monitor logs in the Spaces interface
- **Vercel**: Use Vercel Analytics for frontend monitoring

### 8. Troubleshooting

#### Common Issues

1. **API calls failing**: Check that `NEXT_PUBLIC_API_BASE_URL` in Vercel matches your Hugging Face backend URL
2. **CORS errors**: Verify allowed origins in your backend configuration
3. **Database connection issues**: Ensure your database URL is properly configured in Hugging Face settings
4. **Authentication failures**: Confirm JWT settings match between frontend and backend

#### Debugging Steps

1. Check the logs in both Vercel and Hugging Face Spaces dashboards
2. Verify environment variables are set correctly
3. Test API endpoints directly using the backend's `/docs` interface
4. Confirm that your database is accessible and properly configured

## Architecture Overview

```
Internet
  ├── Vercel (Frontend) - your-app.vercel.app
  │   ├── Next.js application
  │   ├── React UI components
  │   └── API calls to backend
  │
  └── Hugging Face Spaces (Backend) - your-username-app.hf.space
      ├── FastAPI application
      ├── SQLModel ORM
      ├── PostgreSQL database
      ├── JWT authentication
      └── Todo management endpoints
```

This deployment configuration provides:
- ✅ Scalable frontend with Vercel's global CDN
- ✅ Robust backend with Hugging Face Spaces infrastructure
- ✅ Proper separation of concerns
- ✅ Security best practices
- ✅ Easy maintenance and updates
- ✅ Cost-effective deployment model

Your application is now ready for production deployment using Vercel and Hugging Face Spaces! 🚀