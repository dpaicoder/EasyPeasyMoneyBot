# Refer & Earn Telegram Bot

A feature-rich Telegram bot for managing referrals and task completion with rewards.

## Features

- 🎯 Task Management
  - View available tasks
  - Submit task completions
  - Track task status
  - Earn rewards for completed tasks

- 👥 Referral System
  - Unique referral codes
  - Track referrals
  - Earn referral bonuses
  - Referral statistics

- 💰 Balance & Transactions
  - View current balance
  - Transaction history
  - Withdrawal requests
  - Earnings tracking

- 📊 Statistics
  - User statistics
  - Task completion history
  - Referral tracking
  - Leaderboard

## Local Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd referral-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```bash
cp .env.example .env
```

4. Edit the `.env` file with your bot token and settings:
```
BOT_TOKEN=your_bot_token_here
ADMIN_USER_ID=your_admin_user_id_here
REFERRAL_BONUS=10.0
MIN_WITHDRAWAL=5.0
```

5. Run the bot:
```bash
python bot.py
```

## Railway Deployment

1. Create a Railway account at [Railway.app](https://railway.app)

2. Install Railway CLI (optional):
```bash
npm i -g @railway/cli
```

3. Create a new project on Railway:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub repository

4. Configure environment variables:
   - Go to your project settings
   - Add the following variables:
     ```
     BOT_TOKEN=your_bot_token_here
     ADMIN_USER_ID=your_admin_user_id_here
     REFERRAL_BONUS=10.0
     MIN_WITHDRAWAL=5.0
     ```

5. Deploy the bot:
   - Railway will automatically deploy when you push to your repository
   - Or use the Railway dashboard to trigger a manual deploy

6. Monitor your deployment:
   - Check the logs in the Railway dashboard
   - Monitor the bot's status and performance

## Usage

1. Start the bot by sending `/start` command
2. Use the inline keyboard to navigate through features:
   - 🎯 Available Tasks
   - 💰 My Balance
   - 👥 My Referrals
   - 📊 Statistics
   - ❓ Help

3. For task completion:
   - View available tasks
   - Select a task
   - Follow task instructions
   - Submit proof of completion

4. For referrals:
   - Share your referral code
   - Track your referrals
   - Earn referral bonuses

5. For withdrawals:
   - Check your balance
   - Request withdrawal
   - Track withdrawal status

## Admin Features

Admins can:
- Add new tasks
- Approve/reject task completions
- Process withdrawals
- View user statistics
- Manage referral bonuses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 