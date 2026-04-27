# Trump 爭議言論監控系統 (Trump Controversial Statement Monitor)

這是一個自動化的 Python 腳本，透過 NewsAPI 抓取與 Donald Trump 相關的最新新聞，並透過關鍵字分析是否有潛在的爭議性言論（包含不雅字眼、侮辱、或誇張言論）。如果發現符合條件的新聞，系統將會透過 Gmail 自動發送 Email 通知。

## 系統需求

- Python 3.7+
- Gmail 帳號（用於發送通知信）
- NewsAPI 帳號（免費層級即可）

## 安裝與設定步驟

### 1. 安裝依賴套件

請在命令提示字元 (CMD) 或 PowerShell 中執行以下指令來安裝所需的 Python 套件：

```bash
pip install -r requirements.txt
```

### 2. 獲取 NewsAPI 金鑰

1. 前往 [NewsAPI 官網](https://newsapi.org/)。
2. 註冊帳號並獲取免費的 API Key。

### 3. 設定 Gmail 應用程式密碼

為了讓 Python 腳本能夠安全地透過你的 Gmail 發送信件，你必須產生一組「應用程式密碼」：

1. 登入你的 Google 帳號並前往「管理你的 Google 帳戶」。
2. 進入「安全性」分頁。
3. 確保已開啟 **兩步驟驗證 (2-Step Verification)**。
4. 在搜尋列搜尋「應用程式密碼 (App passwords)」。
5. 建立一個新的應用程式密碼（例如命名為 "Python Monitor"），並將這組 16 位數的密碼複製下來。

### 4. 設定環境變數與 `config.json`

為了保護您的帳號安全，敏感資訊將存放在 `.env` 檔案中，其他設定則保留在 `config.json` 中。

1. **建立 `.env` 檔案**：
   在專案根目錄下建立一個名為 `.env` 的檔案，並填入以下內容：
   ```env
   NEWSAPI_KEY=填入你的NewsAPI金鑰
   GMAIL_SENDER=你的Gmail地址@gmail.com
   GMAIL_APP_PASSWORD=剛剛複製的16位數應用程式密碼
   ```

2. **設定 `config.json`**：
   打開專案資料夾中的 `config.json` 檔案，設定收件者及敏感度：
   ```json
   {
     "recipient_emails": [
       "收件者1@example.com",
       "收件者2@example.com"
     ],
     "sensitivity_level": "loose"
   }
   ```
*(目前敏感度預設為 loose，只要標題或摘要中出現一個關鍵字就會觸發通知。)*

### 日誌與錯誤排解

系統會自動將執行日誌與錯誤訊息寫入到 `monitor.log` 檔案中。您可以直接打開該檔案來檢查系統是否正常執行，或是追蹤錯誤紀錄，不需透過命令列查看。

### 5. 執行腳本測試

你現在可以手動執行腳本來進行第一次測試：

```bash
python trump_monitor.py
```

### 6. 部署至 GitHub Actions (雲端自動執行)

為了讓腳本每 30 分鐘自動在雲端執行，且不需要保持電腦開機，我們可以使用 GitHub Actions。

1. **上傳專案到 GitHub**：
   將整個專案資料夾推送到您 GitHub 上的 Repository (注意：**不要**上傳 `.env` 檔案！`requirements.txt`, `trump_monitor.py`, `config.json`, `sent_articles.json` 以及 `.github` 資料夾必須上傳)。
   
2. **設定 GitHub Secrets**：
   - 前往您的 GitHub Repository 頁面。
   - 點選 **Settings** > **Secrets and variables** > **Actions**。
   - 點擊 **New repository secret**，依次新增以下三個 Secrets：
     - `NEWSAPI_KEY`: 填入您的 NewsAPI 金鑰
     - `GMAIL_SENDER`: 填入您的 Gmail 地址
     - `GMAIL_APP_PASSWORD`: 填入您的 16 位數應用程式密碼

3. **啟用 GitHub Actions**：
   專案內的 `.github/workflows/trump_monitor.yml` 檔案已經設定好排程。
   - 預設每 30 分鐘會自動執行一次。
   - 執行完畢後，如果有寄出新通知，GitHub Actions 會自動將更新後的 `sent_articles.json` commit 到您的 Repository 中，以避免重複寄送。
   - 您也可以在 GitHub 的 **Actions** 分頁中，手動點擊 "Run workflow" 來即時測試執行。

> **備註**：由於 GitHub Actions 負載原因，Cron 排程執行時間有時會有幾分鐘的延遲，這是正常現象。
