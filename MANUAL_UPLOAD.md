# MusicBot - GitHub'ga Manual Yuklash

## 1. GitHub'da yangi repository yaratish

1. **GitHub.com'ga kiring:** https://github.com
2. **+** tugmasini bosing (o'ng yuqori burchak) → **New repository**
3. **Repository sozlamalari:**
   ```
   Repository name: musicbot
   Description: 24/7 Telegram Music Bot
   Public yoki Private: xohishingizcha
   ❌ Add a README file - belgilamang!
   ❌ Add .gitignore - belgilamang!
   ❌ Choose a license - belgilamang!
   ```
4. **Create repository** tugmasini bosing

## 2. Repository URL'ni ko'chirib oling

Yangi ochilgan sahifada quyidagi buyruqlar ko'rinadi:
```
https://github.com/SIZNING_USERNAME/musicbot.git
```

Bu URL'ni ko'chirib oling (masalan: `https://github.com/jahongir123/musicbot.git`)

## 3. Men ushbu URL bilan botni yuklayman

URL'ni menga yuboring, men avtomatik yuklayman!

---

**Yoki siz terminal orqali o'zingiz yuklashingiz mumkin:**

```powershell
cd C:\Users\user\MusicBot
git remote add origin https://github.com/SIZNING_USERNAME/musicbot.git
git branch -M main
git push -u origin main
```

Username/password so'rasa - GitHub Personal Access Token yaratishingiz kerak:
- GitHub Settings → Developer settings → Personal access tokens → Generate new token
- `repo` permission bering
- Token'ni password o'rniga kiriting
