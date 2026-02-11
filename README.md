# DocZen - Modern Document Management Platform

DocZen is a production-ready document management platform inspired by iLovePDF, redesigned with modern UX, high scalability, and enterprise-grade security. Built with Flutter, FastAPI, MongoDB Atlas, Redis, and containerized for cloud-native deployment.

## 🚀 Features

### Core Functionality
- **Modern UI/UX**: Glassmorphism design with Material 3 standards
- **Multi-platform**: Flutter frontend for mobile, tablet, desktop, and web
- **Secure Authentication**: JWT with refresh tokens, MFA support
- **File Management**: Upload, organize, search, and version control
- **PDF Processing**: Merge, split, compress, convert, and protect PDFs
- **OCR Support**: Extract text from images and scanned documents
- **Real-time Processing**: WebSocket updates for job progress
- **Sharing System**: Secure links with expiration and download limits

### Enterprise Features
- **Role-based Access Control**: Admin, Business, Pro, and Free tiers
- **Analytics Dashboard**: User behavior tracking with Google Analytics
- **Rate Limiting**: Redis-backed protection against abuse
- **Scalable Architecture**: Microservices with horizontal pod autoscaling
- **Security**: Encryption at rest, secure headers, and input validation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter Web   │    │  Flutter Mobile │    │  Flutter Desktop│
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │       Nginx (SSL/HTTP2)   │
                    └─────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    ┌─────▼─────┐        ┌───────▼───────┐      ┌──────▼──────┐
    │ FastAPI   │        │ Flask Workers │      │  Celery     │
    │ Backend   │        │ (PDF/OCR)     │      │  Queue      │
    └─────┬─────┘        └───────┬───────┘      └──────┬──────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   Redis (Cache/Queue)     │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   MongoDB Atlas (Data)    │
                    └───────────────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **Flutter**: Cross-platform UI framework
- **Material 3**: Modern design system
- **Glassmorphism**: Premium UI aesthetic
- **Google Analytics**: User behavior tracking

### Backend
- **FastAPI**: Async Python web framework
- **Flask**: Document processing workers
- **MongoDB Atlas**: NoSQL database
- **Redis**: Caching and message queue
- **JWT**: Authentication tokens
- **Celery**: Async task processing

### DevOps
- **Docker**: Containerization
- **Kubernetes**: Orchestration
- **GitHub Actions**: CI/CD pipeline
- **Nginx**: Reverse proxy with SSL/HTTP2
- **Pytest**: Testing framework

## 📦 Quick Start

### Prerequisites
- Docker and Docker Compose
- Flutter SDK (for local development)
- Python 3.11+ (for local development)
- Node.js 18+ (for web development tools)

### Using Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/your-org/doczen.git
cd doczen
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Workers: http://localhost:5000

### Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Workers Setup
```bash
cd workers
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### Frontend Setup
```bash
cd frontend
flutter pub get
flutter run -d web-server --web-port 3000
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Application
ENVIRONMENT=development
SECRET_KEY=your-super-secret-key
ALLOWED_HOSTS=http://localhost:3000

# Database
MONGODB_URL=mongodb://localhost:27017/doczen
REDIS_URL=redis://localhost:6379

# File Storage
UPLOAD_DIR=uploads
MAX_FILE_SIZE=104857600  # 100MB

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=doczen-files
```

#### Frontend
- Google Analytics ID in `lib/core/analytics.dart`
- API endpoints in `lib/core/config.dart`

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

### File Management
- `POST /api/v1/files/upload` - Upload file
- `GET /api/v1/files/files` - List user files
- `GET /api/v1/files/{file_id}` - Get file details
- `PUT /api/v1/files/{file_id}` - Update file metadata
- `DELETE /api/v1/files/{file_id}` - Delete file

### PDF Processing
- `POST /api/v1/files/jobs` - Create processing job
- `GET /api/v1/files/jobs` - List user jobs
- `GET /api/v1/files/jobs/{job_id}` - Get job status

### Full API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
flutter test --coverage
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚀 Deployment

### Kubernetes Deployment
```bash
# Create namespace
kubectl create namespace doczen

# Apply configurations
kubectl apply -f kubernetes.yaml

# Check deployment status
kubectl get pods -n doczen
```

### Production Environment Variables
Set the following in your production environment:
- `ENVIRONMENT=production`
- Strong `SECRET_KEY`
- Production MongoDB Atlas connection string
- Production Redis URL
- SSL certificates for Nginx

## 🔒 Security Features

- **Authentication**: JWT with refresh tokens
- **Authorization**: Role-based access control
- **Rate Limiting**: Redis-backed rate limiting
- **Input Validation**: Pydantic schemas
- **File Security**: Type validation, size limits
- **Encryption**: Data at rest encryption
- **Secure Headers**: HSTS, CSP, XSS protection
- **Password Security**: Bcrypt hashing

## 📊 Monitoring & Analytics

### Application Metrics
- Health check endpoints
- Prometheus metrics (optional)
- Custom logging

### User Analytics
- Google Analytics integration
- Event tracking for uploads, conversions
- Privacy-friendly configuration

### Error Handling
- Structured error responses
- Comprehensive logging
- Sentry integration (optional)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use Flutter/Dart style guidelines
- Write tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Open an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: support@doczen.example.com

## 🗺️ Roadmap

### Version 1.1
- [ ] Advanced OCR with multiple languages
- [ ] Batch processing improvements
- [ ] Mobile app optimizations
- [ ] Advanced search with filters

### Version 1.2
- [ ] Integration with cloud storage (Google Drive, Dropbox)
- [ ] Advanced annotation tools
- [ ] Document templates
- [ ] Workflow automation

### Version 2.0
- [ ] AI-powered document analysis
- [ ] Real-time collaboration
- [ ] Advanced security features
- [ ] Enterprise SSO integration

---

**Built with ❤️ by the DocZen Team**
#   D o c Z e n  
 