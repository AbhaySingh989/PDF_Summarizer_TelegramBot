
# 🤖 PDF Summarizer Bot for Telegram

## 👤 Author

**Abhay Singh**
- 📧 Email: [abhay.rkvv@gmail.com]
- 🐙 GitHub: [AbhaySingh989]
- 💼 LinkedIn: [[Abhay Singh](https://www.linkedin.com/in/abhay-pratap-singh-905510149/)]


---

## 📖 About

PDF Summarizer Bot is a powerful Telegram bot that leverages Google's Gemini 2.0 Flash AI model to automatically generate intelligent summaries of your PDF documents. Whether you're dealing with research papers, financial reports, technical documentation, or any other PDF content, this bot makes information digestible and accessible.

## ✨ Features

### 🚀 **Core Functionality**
- 📄 **PDF Processing**: Upload any PDF file (up to 20MB) and get instant AI summaries
- 🤖 **Advanced AI**: Powered by Google Gemini 2.0 Flash for high-quality content analysis
- 📊 **Smart Chunking**: Handles large documents by intelligently breaking them into manageable sections

### 🎨 **User Experience**
- 💬 **Telegram Integration**: Native Telegram bot interface with inline keyboards
- 🔘 **Interactive Buttons**: Easy-to-use buttons for all functions (no typing commands!)
- 📱 **Mobile Friendly**: Works seamlessly on all devices
- 🎯 **Progress Tracking**: Beautiful real-time progress updates with emojis

### 🛠️ **Customization**
- ✏️ **Custom Prompts**: Set personalized summarization instructions
- 🎛️ **Flexible Styles**: Adapt summaries for different document types
- 💾 **Prompt Management**: Save, view, and reset custom prompts easily
- 🔄 **Summary Preservation**: All summaries remain visible when using buttons

### 🔒 **Security & Reliability**
- 🔐 **Secure Configuration**: API keys stored safely in environment variables
- 🧹 **Auto Cleanup**: Temporary files automatically deleted after processing
- ❌ **Error Handling**: Robust error handling with user-friendly messages
- 📝 **Comprehensive Logging**: Detailed logs for monitoring and debugging

## 🛠️ Installation

### Prerequisites

Before you begin, ensure you have:
- 🐍 Python 3.8 or higher installed
- 📱 A Telegram account
- 🔑 Access to Google AI Studio for API keys

### Step 1: Clone the Repository
```
git clone https://github.com/AbhaySingh989/PDF_Summarizer_TelegramBot
cd PDF_Summarizer_TelegramBot
```

### Step 2: Install Dependencies

```
pip install -r requirements.txt
```

### Step 3: Create Environment File

Update `.env` file in the project root:


## ⚙️ Setup

### 🤖 Getting Your Telegram Bot Token

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather
3. **Send** `/newbot` command
4. **Choose a name** for your bot (e.g., "My PDF Summarizer")
5. **Choose a username** for your bot (must end in 'bot', e.g., "my_pdf_summarizer_bot")
6. **Copy the API token** provided by BotFather

### 🔑 Getting Your Google API Key

1. **Visit** [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Sign in** with your Google account
3. **Click** "Create API Key"
4. **Copy the generated API key**

### 📝 Configure Environment Variables

Edit your `.env` file:

```
# Telegram Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Google AI API Key (from Google AI Studio)  
GOOGLE_API_KEY=your_google_api_key_here
```

> ⚠️ **Important**: Never share or commit your API keys to version control!

## 🚀 Usage

### Starting the Bot

```
python bot.py
```

You should see:
```
INFO - PDFSummarizerBot initialized successfully
INFO - PDF Summarizer Bot with Summary Preservation starting...
```

### 📱 Using the Bot

1. **Start the Bot**
   - Find your bot on Telegram
   - Send `/start` to begin
   - You'll see a welcome message with buttons

2. **Upload a PDF**
   - Simply send any PDF file to the bot
   - Wait for the beautiful progress tracking
   - Receive your AI-generated summary!

3. **Customize Your Experience**
   - 🔧 **Custom Prompt**: Set personalized summarization instructions
   - 👀 **View Prompt**: See your current active prompt
   - 🔄 **Reset Prompt**: Return to default settings
   - ❓ **Help**: Get detailed assistance

### 📊 Progress Tracking

The bot shows real-time progress through these stages:
- 🚀 **Starting Processing** - Initialization
- 📥 **Downloading** - Getting your file  
- 📄 **Reading PDF** - Extracting text content
- ⚙️ **Processing** - Analyzing pages and content
- 🤖 **AI Analysis** - Creating intelligent summary
- 📝 **Almost Done** - Finalizing your results

## 🎯 Demo

### Example Custom Prompts

**For Research Papers:**
```
"Focus on methodology, key findings, and implications for future research. Use bullet points for clarity."
```

**For Business Documents:**
```
"Extract key business decisions, financial implications, and action items. Format as structured paragraphs."
```

**For Technical Documentation:**
```
"Highlight main technical concepts, implementation details, and troubleshooting information."
```

## 📁 Project Structure

```
pdf-summarizer-bot/
├── 📜 bot.py                 # Main bot application
├── 📋 requirements.txt       # Python dependencies
├── 🔧 .env_example          # Environment variables template
├── 📁 downloads/            # Temporary file storage (auto-created)
├── 📖 README.md            # This file
└── 📄 LICENSE              # MIT license
```

## 🐛 Troubleshooting

### Common Issues

**❌ Bot not responding**
- Check if your `TELEGRAM_BOT_TOKEN` is correct
- Ensure the bot is running (`python bot.py`)
- Verify bot privacy settings

**❌ AI processing fails**
- Confirm your `GOOGLE_API_KEY` is valid
- Check your Google AI Studio quota/billing
- Ensure stable internet connection

**❌ PDF upload issues**
- File must be in PDF format
- Maximum file size is 20MB
- Ensure PDF contains readable text (not just images)

**❌ Installation problems**
- Update pip: `pip install --upgrade pip`
- Use virtual environment: `python -m venv venv`
- Check Python version: `python --version` (needs 3.8+)

### 🔍 Debugging

Enable detailed logging by modifying the logging level in `bot.py`:

```
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **🍴 Fork** the repository
2. **🌿 Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **💾 Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **📤 Push** to the branch (`git push origin feature/amazing-feature`)
5. **🔄 Open** a Pull Request


## 🙏 Acknowledgments

- 🤖 **Google AI** for providing the powerful Gemini 2.0 Flash model
- 🔗 **LangChain** for the excellent document processing framework
- 📱 **python-telegram-bot** for the robust Telegram bot API wrapper
- 🌟 **Open Source Community** for continuous inspiration and support

## ⭐ Star History

If this project helped you, please consider giving it a star! ⭐

---



**Made with ❤️ by [Abhay Singh](https://github.com/AbhaySingh989)**

*Turn any PDF into actionable insights with the power of AI!*

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Abhay Singh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```


```
