# FortnitePrivateServer-PY

**FortnitePrivateServer-PY** is a custom Fortnite backend written entirely in Python, allowing you to host your own private Fortnite server. It features a complete account system, XMPP support, customizable item shop, locker management, and a Discord bot for backend control and moderation.

> ⚠️ **Disclaimer**: This project is for educational and archival purposes only. It is not affiliated with or endorsed by Epic Games.

---

## ✨ Features

### 🧠 Account System
- Create and manage user accounts
- Change username and password
- Secure session management
- One-time exchange code login system
- View your own and others’ account info

### ☁️ CloudStorage & ClientSettings
- Settings saving per user

### 🎒 Locker System
- Change and preview items
- Change banner icon and color
- Edit item styles (e.g., variants)
- Favorite items
- Mark items as seen

### 👥 Friends System
- Add, accept, and remove friends
- Block/unblock friends
- Set/remove nicknames

### 🛍️ Item Shop
- Fully customizable shop
- Buy items from the shop
- Gift items to friends
- Clear shop-purchased items

### 💬 XMPP Features
- Party support (builds 3.5 to 14.50)
- Whisper, global, and party chat
- Full friends interaction

---

## 🤖 Discord Bot Integration

Use the built-in Discord bot to manage your server via Discord commands.

### ✅ User Commands
| Command | Description |
|--------|-------------|
| `/create {email} {username} {password}` | Creates a new backend account (1 per user). |
| `/details` | Shows your account details. |
| `/lookup {username}` | Looks up a user's profile. |
| `/exchange-code` | Generates a one-time login code (expires in 5 minutes). |
| `/change-username {newUsername}` | Changes your username. |
| `/change-password {newPassword}` | Changes your password. |
| `/sign-out-of-all-sessions` | Signs you out of all current sessions. |
| `/clear-items-for-shop` | Clears purchased item shop data. |

### 🛡️ Moderator Commands
> You must be listed as a moderator in `config.json` to use these.

| Command | Description |
|--------|-------------|
| `/ban {targetUsername}` | Bans the specified user. |
| `/unban {targetUsername}` | Unbans the specified user. |
| `/kick {targetUsername}` | Kicks the user from their session. |

