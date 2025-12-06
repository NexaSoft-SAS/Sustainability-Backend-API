# Sustainability Backend API Contracts

## Architecture Overview
- **Framework**: FastAPI + MongoDB + Pydantic
- **Structure**: Modular organization similar to requested Node.js structure
- **Authentication**: JWT tokens for protected endpoints
- **Database**: MongoDB with motor (async driver)

## API Endpoints

### Diagnostico Verde Endpoints
```
POST   /api/diagnostico          → Create new green diagnosis request
GET    /api/diagnostico          → List all requests (protected)
GET    /api/diagnostico/{id}     → Get specific request (protected)
DELETE /api/diagnostico/{id}     → Delete request (protected)
POST   /api/auth/login          → Admin authentication
```

## Data Models

### DiagnosticoVerde
```python
{
  "id": "ObjectId", 
  "empresa": "string (required)",
  "contacto_nombre": "string (required)", 
  "contacto_email": "string (required)",
  "telefono": "string (optional)",
  "mensaje": "string (optional)",
  "sector": "string (optional)",
  "fuente_trafico": "string (default: 'web')",
  "fecha_solicitud": "datetime (auto)",
  "estado": "string (default: 'pendiente')"
}
```

### Usuario Admin
```python
{
  "id": "ObjectId",
  "email": "admin@empresa.com", 
  "password_hash": "hashed_Demo1234",
  "role": "admin",
  "created_at": "datetime"
}
```

## Frontend Integration Points

### Current Mock Data Replacement
- Remove mock form submission in `CTAComponent.jsx` 
- Connect to real POST /api/diagnostico endpoint
- Add proper error handling and loading states
- Use REACT_APP_BACKEND_URL for API calls

### Form Data Mapping
```javascript
// Frontend form data
{
  name: formData.name,           → contacto_nombre
  company: formData.company,     → empresa  
  email: formData.email,         → contacto_email
  phone: formData.phone,         → telefono
  message: formData.message      → mensaje
}
```

## Security Features
- JWT tokens for admin access
- Input validation with Pydantic
- CORS properly configured
- Rate limiting on form submission
- Admin credentials: admin@empresa.com / Demo1234

## Growth Hacking Features  
- Track traffic source in diagnostico requests
- Optional webhook integration for Slack/Discord notifications
- Analytics endpoints for dashboard metrics
- Email notifications (ready for integration)

## Environment Variables
```
MONGO_URL=existing_mongo_connection
DB_NAME=existing_db_name
JWT_SECRET=generated_secret_key
ADMIN_EMAIL=admin@empresa.com
ADMIN_PASSWORD=Demo1234
WEBHOOK_URL=optional_slack_webhook
```

## File Structure
```
/backend/
├── server.py (existing - main entry)
├── config/
│   ├── database.py (MongoDB connection)
│   └── auth.py (JWT configuration) 
├── models/
│   ├── diagnostico.py (Pydantic models)
│   └── user.py (Admin user model)
├── services/  
│   ├── diagnostico_service.py (business logic)
│   └── auth_service.py (authentication logic)
├── controllers/
│   ├── diagnostico_controller.py (route handlers)
│   └── auth_controller.py (auth handlers)
├── utils/
│   ├── validators.py (input validation)
│   └── notifications.py (webhook helpers)
└── routes/
    ├── diagnostico_routes.py (diagnostico endpoints)
    └── auth_routes.py (auth endpoints)
```