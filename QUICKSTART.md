# Quick Start Guide for Fair-Scan

## ⚡ 5-Minute Setup

### Windows

```batch
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file with your API keys
copy .env.example .env
# Then edit .env with your:
# - GEMINI_API_KEY
# - MAIL_USERNAME and MAIL_PASSWORD

# 4. Run the app
python run.py
```

### macOS/Linux

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file with your API keys
cp .env.example .env
# Then edit .env with your:
# - GEMINI_API_KEY
# - MAIL_USERNAME and MAIL_PASSWORD

# 4. Run the app
python run.py
```

## 🔑 Getting API Keys

### Step 1: Google Gemini API Key (Free)

1. Visit https://ai.google.dev
2. Click "Get API Key"
3. Select your project and create key
4. Copy the key to `.env` as `GEMINI_API_KEY`

### Step 2: Gmail Setup for Emails

1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication
3. Create an "App password" for Mail
4. Add to `.env`:
   ```
   MAIL_USERNAME=youremail@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx
   ```

## ✅ Verify Setup

After running `python run.py`, visit:
- Landing page: http://localhost:5000
- Sign up: http://localhost:5000/auth/signup
- Dashboard: http://localhost:5000/dashboard

## 📝 First Test

1. Sign up with your email
2. Go to "Upload Resume"
3. Drag & drop a sample PDF resume
4. Check your email for results!

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run: `pip install -r requirements.txt` |
| Email not working | Check `.env` MAIL settings & Enable 2FA on Gmail |
| API errors | Verify GEMINI_API_KEY is valid at ai.google.dev |
| Port 5000 in use | Change PORT in `.env` or run: `python run.py --port 5001` |

## 📚 Next Steps

1. Read [README.md](README.md) for full documentation
2. Customize the email template in `app/utils.py`
3. Modify styling in `app/static/css/style.css`
4. Deploy using Docker or Heroku

## 💡 Tips

- Test with a sample resume to ensure everything works
- Keep your `.env` file secure - never commit it
- Use App Passwords (not your regular Gmail password)
- Check the console for error messages if something fails

---

**Questions?** Check the [Troubleshooting](README.md#-troubleshooting) section in README.md
