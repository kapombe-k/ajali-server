# AJALI Project

- This is the backend repo for the Ajali project as part of the fulfillment for phase 5 completion
- The project is part of a combined effort of Michelle Muchoki, Alice Nthenge, Stephen Magiya, Dennis Soi and Eugene Kapombe
- The project employs the use of Flask, SQLAlchemy, JWT, and PostgreSQL 

# AJALI Emergency Response System

## Overview

AJALI is a comprehensive emergency reporting and response platform designed to streamline the process of reporting and managing emergency incidents. The system enables citizens to quickly report accidents, fires, and other emergencies with precise location data and multimedia evidence, while providing emergency responders with real-time access to critical information.

Built as a full-stack web application, AJALI bridges the gap between citizens and emergency services by providing an intuitive mobile-first interface for incident reporting and a robust administrative dashboard for emergency management.

## Core Features

### 🚨 Emergency Reporting
- **Real-time Incident Submission**: Users can report emergencies with detailed descriptions, incident types, and precise GPS coordinates
- **Multimedia Support**: Attach photos and videos as evidence (up to 5MB per file)
- **Location Integration**: Automatic GPS coordinate capture with manual override capability
- **Incident Categorization**: Pre-defined categories including Fire, Traffic Accidents, Infrastructure issues, and Workplace emergencies

### 👥 User Management
- **Secure Authentication**: JWT-based authentication with refresh token support
- **Role-based Access Control**: Separate interfaces for regular users and administrators
- **Profile Management**: User registration with email/phone validation and password strength requirements
- **Emergency Contacts**: Users can store emergency contact information for quick access

### 🛡️ Administrative Dashboard
- **Incident Monitoring**: Real-time view of all reported emergencies
- **Status Management**: Update incident status and track response progress
- **User Oversight**: Manage user accounts and permissions
- **Report Analytics**: Comprehensive reporting and analytics capabilities

### 🔒 Security & Performance
- **Rate Limiting**: API rate limiting to prevent abuse (1000 requests/day, 100/hour)
- **CORS Protection**: Cross-origin resource sharing configuration for secure API access
- **File Upload Security**: Strict file type and size validation for media uploads
- **Token Revocation**: Secure logout with JWT token blacklisting

## Technology Stack

### Backend Architecture
- **Framework**: Flask 3.0.2 - Lightweight Python web framework
- **Database**: SQLite with SQLAlchemy 2.0.25 ORM
- **Authentication**: Flask-JWT-Extended 4.5.3 for token-based authentication
- **Security**: Flask-Bcrypt 1.0.1 for password hashing
- **API**: Flask-RESTful 0.3.10 for REST API development
- **Migrations**: Flask-Migrate 4.0.5 with Alembic 1.13.1
- **CORS**: Flask-CORS 4.0.0 for cross-origin requests
- **Serialization**: SQLAlchemy-Serializer 1.5.0 for data serialization
- **Environment**: Python-Dotenv 1.0.0 for configuration management
- **Deployment**: Gunicorn 21.2.0 for production WSGI server

### Frontend Architecture
- **Framework**: React 19.1.0 - Modern JavaScript library for building user interfaces
- **Build Tool**: Vite 7.0.5 - Fast build tool and development server
- **Styling**: TailwindCSS 4.1.11 - Utility-first CSS framework
- **Routing**: React Router DOM 7.7.0 - Declarative routing for React
- **HTTP Client**: Axios 1.10.0 - Promise-based HTTP client
- **Forms**: React Hook Form 7.60.0 with Zod 4.0.17 validation
- **Maps**: React Leaflet 5.0.0 - Interactive maps for location selection
- **Notifications**: React Toastify 11.0.5 - Toast notifications
- **Icons**: React Hot Toast 2.5.2 - Toast notifications with icons

### Development Tools
- **Linting**: ESLint 9.30.1 with React-specific rules
- **Type Checking**: TypeScript definitions for React components
- **Code Formatting**: Prettier integration
- **Testing**: Jest and React Testing Library setup

## System Architecture

### Database Schema

The system utilizes a relational database with the following core entities:

#### Users Table
- **Primary Key**: id (Integer)
- **Fields**: first_name, last_name, email (unique), password (hashed), phone_number (unique), role, timestamps
- **Relationships**: One-to-many with Reports and EmergencyContacts

#### Reports Table
- **Primary Key**: id (Integer)
- **Fields**: user_id (FK), incident (type), details, latitude, longitude, timestamps
- **Relationships**: Belongs to User, has many MediaAttachments and StatusUpdates

#### MediaAttachments Table
- **Primary Key**: id (Integer)
- **Fields**: report_id (FK), file_url, media_type, uploaded_at
- **Features**: File storage with type validation (images/videos up to 5MB)

#### EmergencyContacts Table
- **Primary Key**: id (Integer)
- **Fields**: user_id (FK), name, relationship, phone_number, email, address
- **Purpose**: Quick access to user's emergency contacts

#### StatusUpdates Table
- **Primary Key**: id (Integer)
- **Fields**: report_id (FK), updated_by, status, timestamp
- **Purpose**: Track incident response progress

#### TokenBlocklist Table
- **Primary Key**: id (Integer)
- **Fields**: jti (JWT ID), created_at
- **Purpose**: JWT token revocation for secure logout

### API Architecture

The RESTful API follows RESTful conventions with the following endpoints:

#### Authentication Endpoints
- `POST /login` - User authentication
- `POST /token/refresh` - Refresh access tokens
- `POST /logout` - Secure logout with token revocation

#### User Management
- `POST /users` - User registration
- `GET /users` - List all users (admin only)
- `GET /users/<id>` - Get specific user
- `PATCH /users/<id>` - Update user profile
- `DELETE /users/<id>` - Delete user account

#### Report Management
- `POST /reports` - Submit new emergency report
- `GET /reports` - List all reports (admin only)
- `GET /reports/<id>` - Get specific report
- `PATCH /reports/<id>` - Update report details
- `DELETE /reports/<id>` - Delete report

#### Media Management
- `POST /reports/<id>/media` - Upload media files to report
- `GET /reports/<id>/media` - Retrieve media files for report
- `DELETE /reports/<id>/media` - Remove media files

#### Emergency Contacts
- `GET /emergency-contacts` - List user's emergency contacts
- `POST /emergency-contacts` - Add new emergency contact
- `PATCH /emergency-contacts/<id>` - Update emergency contact
- `DELETE /emergency-contacts/<id>` - Remove emergency contact

#### Administrative
- `GET /admin/reports` - Administrative report overview
- `PATCH /admin/reports/<id>` - Admin report updates
- `POST /reports/<id>/status` - Update report status

## User Roles and Permissions

### Regular Users
- **Registration**: Create account with email/phone validation
- **Authentication**: Login/logout with JWT tokens
- **Reporting**: Submit emergency reports with location and media
- **Profile Management**: Update personal information
- **Emergency Contacts**: Manage personal emergency contacts
- **Dashboard**: View personal reports and status updates

### Administrators
- **User Management**: View, update, and delete user accounts
- **Report Oversight**: Access all emergency reports system-wide
- **Status Updates**: Update incident status and response progress
- **System Monitoring**: Comprehensive dashboard with analytics
- **Media Review**: Access and manage all uploaded media files

## Security Implementation

### Authentication & Authorization
- **JWT Tokens**: Stateless authentication with access and refresh tokens
- **Password Security**: Bcrypt hashing with salt rounds
- **Token Expiration**: Access tokens (2 hours), refresh tokens (7 days)
- **Secure Logout**: Token blacklisting prevents token reuse

### Data Protection
- **Input Validation**: Comprehensive validation for all user inputs
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
- **XSS Protection**: Input sanitization and secure output encoding
- **File Upload Security**: Strict MIME type and size validation

### API Security
- **Rate Limiting**: Prevents API abuse with configurable limits
- **CORS Configuration**: Controlled cross-origin resource sharing
- **Error Handling**: Generic error messages prevent information leakage
- **Request Logging**: Comprehensive logging for security monitoring

## Installation and Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- SQLite (included with Python)

### Backend Setup
```bash
cd Backend-repo
pip install pipenv
pipenv install
pipenv shell
flask db upgrade
python app.py
```

### Frontend Setup
```bash
cd frontend-repo/ajali-client
npm install
npm run dev
```

### Environment Configuration
Create `.env` files in both backend and frontend directories with appropriate configuration values for database URLs, JWT secrets, and API endpoints.

## Usage Workflow

### For Citizens
1. **Registration**: Create account with personal details
2. **Login**: Authenticate to access the system
3. **Report Emergency**: Use the report form to submit incident details
4. **Attach Evidence**: Upload photos/videos of the incident
5. **Track Progress**: Monitor report status through dashboard

### For Emergency Responders
1. **Admin Login**: Access administrative dashboard
2. **Monitor Reports**: View all incoming emergency reports
3. **Assess Priority**: Review incident details and media
4. **Update Status**: Mark reports as acknowledged, in-progress, or resolved
5. **Coordinate Response**: Use location data for rapid deployment

## Performance Considerations

### Database Optimization
- **Indexing**: Strategic indexing on frequently queried fields
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Optimized SQL queries with proper joins

### API Performance
- **Caching**: Response caching for frequently accessed data
- **Pagination**: Efficient handling of large datasets
- **Async Processing**: Background processing for media uploads

### Frontend Optimization
- **Code Splitting**: Lazy loading of React components
- **Image Optimization**: Compressed media uploads
- **Progressive Loading**: Incremental content loading

## Future Enhancements

### Planned Features
- **Real-time Notifications**: Push notifications for status updates
- **Mobile App**: Native iOS/Android applications
- **Multi-language Support**: Localization for different regions
- **Integration APIs**: Connection with emergency service systems
- **Analytics Dashboard**: Advanced reporting and analytics
- **Offline Capability**: Limited functionality without internet

### Technical Improvements
- **Microservices Architecture**: Modular system components
- **Containerization**: Docker deployment support
- **CI/CD Pipeline**: Automated testing and deployment
- **Monitoring**: Comprehensive system monitoring and alerting

---

**AJALI** represents a critical infrastructure component for emergency response systems, combining modern web technologies with robust security practices to ensure reliable emergency reporting and management. The system's modular architecture and comprehensive feature set make it adaptable to various emergency response scenarios while maintaining high standards of security and performance.





