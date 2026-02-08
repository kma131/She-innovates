# Fair-Scan: Resume Anonymizer

> **Fair-Scan** is a Flask-based web application that uses AI to automatically anonymize resumes by removing identifying markers (names, addresses, graduation dates) while highlighting relevant skills and experience. Built for HR departments committed to fair and unbiased hiring practices.

## 🎯 Features

- **Smart Anonymization**: Uses Google's Gemini API with NLP to remove gender, ethnicity, age, and location identifiers
- **Skill Extraction**: Automatically extracts and categorizes technical skills, soft skills, and key achievements
- **Email Delivery**: Results sent directly to user email addresses
- **User Authentication**: Email-based sign-in with secure password hashing
- **Dashboard**: View and manage all processed resumes
- **Professional UI**: Modern, accessible, and responsive design
- **PDF Support**: Upload resumes in PDF format

## 🛠️ Tech Stack

- **Backend**: Flask (Python 3.8+)
- **Database**: SQLite (with SQLAlchemy ORM)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI/NLP**: Google Generative AI (Gemini)
- **PDF Processing**: PyPDF2
- **Email**: Flask-Mail
- **Authentication**: Flask-Login with password hashing

## 🎨 Design Aesthetic

Fair-Scan features a modern, professional design focused on **trust, fairness, and clarity**:

- **Primary Color**: Deep Navy (#1a3a4a) - Professional, trustworthy
- **Accent Color**: Vibrant Teal (#00b4d8) - Represents fairness and progress
- **Success Color**: Sage Green (#06d6a0) - Calming, positive
- **Typography**: Clean sans-serif (system font stack) for readability
- **Layout**: Card-based, spacious, with generous whitespace
- **Interactions**: Smooth transitions, clear feedback on all actions

## 📋 Prerequisites

- Python 3.8 or higher
- Git (for version control)
- Google Gemini API key (free at [ai.google.dev](https://ai.google.dev))
- Gmail account with App Password (for email functionality)

## 🚀 Installation & Setup

### 1. Clone/Download the Repository

```bash
cd She-Innovates
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your configuration:

```bash
cp .env.example .env
```

Edit `.env` with:

```
FLASK_ENV=development
SECRET_KEY=generate-a-secure-random-key-here

# Gemini API Key
GEMINI_API_KEY=your-api-key-from-google
```

#### Getting Your Gemini API Key:
1. Go to [Google AI Studio](https://ai.google.dev)
2. Click "Get API Key"
3. Create a new API key
4. Copy it to your `.env` file



### 5. Initialize Database

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

### 6. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## 📦 Project Structure

```
fair-scan/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models (User, Resume)
│   ├── routes.py            # URL routes and handlers
│   ├── utils.py             # Helper functions (PDF, Gemini, Email)
│   ├── templates/           # HTML templates
│   │   ├── base.html        # Base template
│   │   ├── index.html       # Landing page
│   │   ├── login.html       # Login page
│   │   ├── signup.html      # Signup page
│   │   ├── dashboard.html   # User dashboard
│   │   ├── upload.html      # Resume upload
│   │   └── view_resume.html # Resume details
│   └── static/
│       ├── css/
│       │   └── style.css    # Main stylesheet
│       └── js/
│           └── main.js      # JavaScript functions
├── uploads/                 # Temporary storage for uploaded PDFs
├── config.py               # Configuration settings
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🔐 Security Notes

1. **Never commit `.env` file** - It contains sensitive API keys
2. **Change `SECRET_KEY`** in production - Use a strong random string
3. **Use HTTPS in production** - Set `SESSION_COOKIE_SECURE = True`
4. **Database backups** - Regularly backup your SQLite database
5. **API rate limiting** - Consider adding rate limits to prevent abuse
6. **File uploads** - PDFs are validated but consider adding virus scanning in production

## 📧 Email Configuration

### Gmail Setup (Recommended for Development)

1. Create a 16-character Gmail App Password [here](https://myaccount.google.com/apppasswords)
2. Add to `.env`:
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx
   ```

### Other Email Providers

Update `MAIL_SERVER` and `MAIL_PORT` in `.env`:
- **SendGrid**: `smtp.sendgrid.net:587`
- **AWS SES**: `email-smtp.region.amazonaws.com:587`
- **Office 365**: `smtp.office365.com:587`

## 🚀 Deployment

### Heroku Deployment

```bash
# Install Heroku CLI, then:
heroku login
heroku create fair-scan
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main

# Set environment variables
heroku config:set GEMINI_API_KEY=your-key
heroku config:set MAIL_USERNAME=your-email
```

### Docker Deployment

```bash
docker build -t fair-scan .
docker run -p 5000:5000 --env-file .env fair-scan
```

### Production Checklist

- [ ] Use a production-grade database (PostgreSQL)
- [ ] Set `FLASK_ENV=production`
- [ ] Generate a strong `SECRET_KEY`
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up error logging and monitoring
- [ ] Configure CORS if needed
- [ ] Set up automated backups
- [ ] Test email delivery
- [ ] Load test the application
- [ ] Set up monitoring and alerting

## 🧪 Testing

```bash
# Run with test data
FLASK_ENV=testing python run.py

# Test email without sending (set MAIL_SUPPRESS_SEND = True in config.py)
```

## 📝 API Endpoints

### Authentication
- `POST /auth/signup` - Create new account
- `POST /auth/login` - Login to account
- `GET /auth/logout` - Logout

### Main Features
- `GET /` - Landing page
- `GET /dashboard` - User dashboard
- `GET /upload` - Upload form
- `POST /upload` - Process resume
- `GET /resume/<id>` - View resume details
- `POST /delete/<id>` - Delete resume

## 🛠️ Customization

### Adding Custom Processing Logic

Edit `app/utils.py` `anonymize_resume()` function to add:
- Additional anonymization rules
- Custom skill detection
- Integration with other APIs

### Styling Changes

Edit `app/static/css/style.css` to modify:
- Colors (update CSS variables in `:root`)
- Typography
- Layout and spacing
- Responsive breakpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Fair-Scan is released as an open-source project. See LICENSE file for details.

## 🆘 Troubleshooting

### "ModuleNotFoundError" when starting app
```bash
# Verify virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### Emails not sending
- Verify `MAIL_USERNAME` and `MAIL_PASSWORD` in `.env`
- Check Gmail "Less secure apps" or use App Passwords
- Ensure no firewall blocks port 587 (SMTP)

### Gemini API errors
- Verify API key is valid and active
- Check [API quota](https://ai.google.dev/tutorials/setup)
- Ensure request is properly formatted

### Database errors
- Delete `fair_scan.db` to reset database
- Run db initialization again
- Check file permissions on `uploads/` folder

## 📞 Support

For issues and questions:
- Check [Troubleshooting](#-troubleshooting) section
- Review error logs in console output
- Create an issue on GitHub

## 🎯 Roadmap

Potential future enhancements:

- [ ] Support for more document formats (DOCX, TXT, LinkedIn)
- [ ] Batch processing for multiple resumes
- [ ] Advanced analytics dashboard
- [ ] Custom anonymization rules per organization
- [ ] Integration with ATS systems
- [ ] Multi-language support
- [ ] Mobile app
- [ ] API for third-party integration

## ⚖️ Ethical Considerations

Fair-Scan is designed to promote **fair and unbiased hiring**:

- **Privacy**: User data is processed securely with minimal retention
- **Fairness**: Removes unconscious bias triggers from resumes
- **Transparency**: Users control their data and can delete anytime
- **Security**: Uses industry-standard encryption and security practices

We encourage responsible use aligned with employment law and ethical hiring practices.

---

**Built with ❤️ for inclusive hiring practices**

Version: 1.0.0 | Last Updated: February 2026
