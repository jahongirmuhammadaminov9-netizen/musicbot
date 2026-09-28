# MusicBot - Render.com'ga Deploy Qilish

## 1. GitHub Desktop orqali yuklash

1. **GitHub Desktop'ni oching**
2. **File → Add Local Repository** bosing
3. **Choose...** tugmasini bosing va `C:\Users\user\MusicBot` papkasini tanlang
4. **Create a repository** tugmasini bosing (agar chiqsa)
5. Repository ma'lumotlari:
   - Name: `musicbot`
   - Description: `24/7 Telegram Music Bot`
   - ✅ Keep this code private (yoki Public - xohishingizcha)
6. **Create Repository** bosing
7. **Publish repository** tugmasini bosing
8. GitHub.com'ga yuklanadi!

## 2. Render.com'da Deploy qilish

1. **Render.com'ga kiring:** https://render.com (GitHub bilan login qiling)

2. **New → Web Service** tugmasini bosing

3. **Connect repository:**
   - GitHub'dagi `musicbot` repositoriyangizni toping
   - **Connect** bosing

4. **Service sozlamalari:**
   ```
   Name: musicbot
   Region: Oregon (US West) - yoki Frankfurt (Europe)
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python music_bot.py
   ```

5. **Instance Type:**
   - ✅ **Free** ni tanlang

6. **Environment Variables:**
   Hech narsa qo'shmaslik kerak (token kodda bor)

7. **Create Web Service** tugmasini bosing

8. **Deploy boshlandi!** 
   - 2-3 daqiqa kutish
   - Loglarni kuzatib turing

## 3. Natija

✅ Bot 24/7 ishlay boshlaydi!
✅ Har doim online bo'ladi
✅ Bepul (750 soat/oy)

## Muammolar

Agar xatolik bo'lsa:
- Render dashboard'da Logs'ni tekshiring
- Download papkasi avtomatik yaratiladi
- Bot_stats.json avtomatik yaratiladi

## Kuzatish

Render.com dashboard'da:
- 📊 Logs - bot nima qilyapti
- 🔄 Deploys - deploy tarixi
- ⚙️ Settings - sozlamalar
