---
title: Todo Web Application Backend
emoji: 📝
colorFrom: blue
colorTo: yellow
sdk: docker
app_file: app.py
pinned: false
---

# Todo Web Application Backend

This is the backend API for a multi-user Todo web application built with FastAPI and SQLModel.

## API Endpoints

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/todos` - Get user's todos
- `POST /api/v1/todos` - Create a new todo
- `PUT /api/v1/todos/{id}` - Update a todo
- `DELETE /api/v1/todos/{id}` - Delete a todo
- `PATCH /api/v1/todos/{id}/complete` - Toggle completion status

## Environment Variables

- `DATABASE_URL`: PostgreSQL database URL
- `SECRET_KEY`: JWT secret key (required)
- `ALGORITHM`: JWT algorithm (defaults to HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (defaults to 30)

## Features

- Multi-user authentication with JWT
- Secure password hashing
- User-specific data isolation
- Full CRUD operations for todo tasks
- Production-ready security features
