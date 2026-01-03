# Deploy Telegram Discount Bot to Render

## 🚀 Quick Deployment Steps

### 1. Prepare Your Repository

First, initialize a git repository if you haven't already:

```bash
git init
git add .
git commit -m "Initial commit - Telegram Discount Bot"
```

### 2. Push to GitHub

Create a new repository on GitHub and push your code:

```bash
# Replace with your GitHub username and repo name
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 3. Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Click **"Apply"**

### 4. Configure Environment Variables

After deployment, go to your service dashboard and add these environment variables:

#### Required Variables:

| Variable | Description | How to Get |
|----------|-------------|------------|
| `TELEGRAM_API_ID` | Your Telegram API ID | Get from https://my.telegram.org |
| `TELEGRAM_API_HASH` | Your Telegram API Hash | Get from https://my.telegram.org |
| `SUPABASE_URL` | Your Supabase project URL | Already in your .env file |
| `SUPABASE_KEY` | Your Supabase anon key | Already in your .env file |

#### Optional Variables:

| Variable | Description | How to Get |
|----------|-------------|------------|
| `OPENAI_API_KEY` | OpenAI API key for LLM verification | Get from https://platform.openai.com/api-keys |

### 5. Important Notes

⚠️ **Session File Handling:**
- The first time your bot runs on Render, it will need to authenticate
- You'll need to check the Render logs for the authentication code
- Enter the code when prompted
- The session will be saved and persist across deployments

⚠️ **Free Tier Limitations:**
- Render's free tier spins down after 15 minutes of inactivity
- Your bot will restart when it receives activity
- For 24/7 operation, consider upgrading to a paid plan ($7/month)

### 6. Monitor Your Bot

- View logs: Go to your service → **Logs** tab
- Check status: Service should show as "Live"
- View metrics: Monitor resource usage in the **Metrics** tab

## 🔧 Alternative: Manual Deployment

If you prefer not to use the Blueprint, you can deploy manually:

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Background Worker"**
3. Connect your repository
4. Configure:
   - **Name:** telegram-discount-bot
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python telegram_listener.py`
5. Add environment variables (see table above)
6. Click **"Create Background Worker"**

## 📊 Verify Deployment

After deployment, check the logs to ensure:

```
✅ Successfully logged in as: [Your Name]
✅ Database initialized
✅ Image storage initialized
👂 Listening to X channels...
```

## 🐛 Troubleshooting

### Bot Not Starting
- Check logs for error messages
- Verify all environment variables are set correctly
- Ensure your Telegram API credentials are valid

### Authentication Issues
- If prompted for a code, check Render logs
- You may need to use Render's shell to enter the code
- Consider creating the session file locally first

### Database Connection Errors
- Verify SUPABASE_URL and SUPABASE_KEY are correct
- Check that your Supabase project is active
- Ensure database tables are created (run create_tables.py locally first)

## 🔄 Updating Your Bot

To update your bot after making changes:

```bash
git add .
git commit -m "Your update message"
git push
```

Render will automatically detect the changes and redeploy.

## 💡 Tips

1. **Test Locally First:** Always test changes locally before pushing
2. **Monitor Logs:** Keep an eye on logs during the first few hours
3. **Use Environment Variables:** Never hardcode credentials
4. **Set Up Alerts:** Configure Render notifications for failures
5. **Consider Paid Plan:** For reliable 24/7 operation

## 📞 Support

- Render Documentation: https://render.com/docs
- Telegram API Docs: https://core.telegram.org/api
- Supabase Docs: https://supabase.com/docs

---

**Ready to Deploy? Follow Step 1 above! 🚀**
