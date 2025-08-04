import os
import json
import zipfile
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your actual token

# HTML Templates
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Online Test</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <div id="app"></div>
  <script src="script.js"></script>
</body>
</html>
'''

CSS_TEMPLATE = '''body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f5f5f5;
}
#app {
  padding: 20px;
}
'''

JS_TEMPLATE = '''const testData = REPLACE_ME;

document.getElementById("app").innerHTML = `
  <h1>Test: ${testData.title}</h1>
  <p>Total Questions: ${testData.questions.length}</p>
  <ol>
    ${testData.questions.map(q => `
      <li>
        <strong>${q.question}</strong>
        <ul>
          ${q.options.map(opt => `<li>${opt}</li>`).join("")}
        </ul>
      </li>
    `).join("")}
  </ol>
`;
'''

# Function to generate and zip HTML files
def generate_zip(json_data):
    os.makedirs("output", exist_ok=True)

    with open("output/index.html", "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)

    with open("output/style.css", "w", encoding="utf-8") as f:
        f.write(CSS_TEMPLATE)

    js_filled = JS_TEMPLATE.replace("REPLACE_ME", json.dumps(json_data, indent=2))
    with open("output/script.js", "w", encoding="utf-8") as f:
        f.write(js_filled)

    with open("output/test.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    zip_path = "portal_test.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for filename in ["index.html", "style.css", "script.js", "test.json"]:
            zipf.write(f"output/{filename}", arcname=filename)

    return zip_path

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a JSON file (test format), and I’ll send you back HTML portal files zipped!")

# Handle JSON file
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    await file.download_to_drive("received.json")

    try:
        with open("received.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        zip_path = generate_zip(data)
        await update.message.reply_document(document=open(zip_path, "rb"), filename="TestPortal.zip")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.MimeType("application/json"), handle_document))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
