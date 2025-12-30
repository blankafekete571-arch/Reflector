# Reflektor — Structured Self-Reflection Exercise

Reflektor is a conversational AI assistant that guides you through a CBT-style (Cognitive Behavioral Therapy) self-reflection exercise. The assistant helps you explore a specific situation by asking questions about what happened, your physical sensations, thoughts, emotions, and perspectives.

## What This App Does

The assistant will guide you through 8 structured steps:
1. **Situation** – What happened?
2. **Physical sensations** – What bodily sensations did you notice?
3. **Automatic thoughts** – What thoughts went through your mind?
4. **Emotions** – What emotions were present?
5. **Meaning/interpretation** – What did this mean to you?
6. **Alternative perspective** – Is there another possible interpretation?
7. **Next-step intention** (optional) – Is there a small next step you might take?
8. **Closure** – Final thoughts and summary

The assistant follows strict rules:
- Asks one question at a time
- Does not give advice or judge
- Does not make diagnoses
- Maintains a compassionate, neutral tone

---

## Setup Instructions (Beginner-Friendly)

### Step 1: Install Python

First, you need Python installed on your computer.

**Check if you already have Python:**
1. Open Terminal (on Mac) or Command Prompt (on Windows)
2. Type: `python3 --version` and press Enter
3. If you see something like "Python 3.11.x", you're good! Skip to Step 2.
4. If not, download Python from: https://www.python.org/downloads/
   - Download version 3.8 or newer
   - Run the installer and follow the instructions
   - **Important:** On Windows, check the box that says "Add Python to PATH"

### Step 2: Get an OpenAI API Key

This app uses OpenAI's GPT model to power the conversational assistant.

1. Go to: https://platform.openai.com/
2. Sign up or log in to your account
3. Click on your profile icon (top right) → "API keys"
4. Click "Create new secret key"
5. **Important:** Copy this key immediately and save it somewhere safe! You won't be able to see it again.
6. Note: Using the OpenAI API costs money, but it's very inexpensive for personal use (usually a few cents per conversation).

### Step 3: Download the Project

1. Download this project folder to your computer
2. Remember where you saved it (for example: `Downloads/reflektor`)

### Step 4: Open Terminal in the Project Folder

**On Mac:**
1. Open Terminal (you can find it in Applications → Utilities)
2. Type `cd ` (that's "cd" followed by a space)
3. Drag the `reflektor` folder into the Terminal window
4. Press Enter

**On Windows:**
1. Open the `reflektor` folder in File Explorer
2. Click on the address bar at the top
3. Type `cmd` and press Enter
4. A Command Prompt window will open in the right location

### Step 5: Create a Virtual Environment (Recommended)

A virtual environment keeps this project's dependencies separate from other Python projects.

Type these commands one at a time, pressing Enter after each:

```bash
python3 -m venv reflektor
```

Wait for it to finish, then activate the virtual environment:

**On Mac/Linux:**
```bash
source reflektor/bin/activate
```

**On Windows:**
```bash
reflektor\Scripts\activate
```

You should see `(reflektor)` appear at the beginning of your command line. This means it worked!

### Step 6: Install Required Packages

Now install the packages this app needs:

```bash
pip install -r requirements.txt
```

This will install:
- `openai` - to communicate with OpenAI's API
- `python-dotenv` - to manage your API key securely

### Step 7: Set Up Your API Key

1. In the `reflektor` folder, create a new file called `.env` (note the dot at the beginning)
2. Open `.env` in a text editor (like Notepad or TextEdit)
3. Add this line, replacing `your-api-key-here` with your actual OpenAI API key:

```
OPENAI_API_KEY=your-api-key-here
```

4. Save the file

**Example:**
```
OPENAI_API_KEY=sk-proj-abc123xyz456...
```

**Important:** Never share this `.env` file or commit it to version control!

### Step 8: Run the App!

You're ready to go! In Terminal/Command Prompt, type:

```bash
python reflektor_app.py
```

The assistant will greet you and start asking the first question. Just type your responses and press Enter.

To exit at any time, type: `stop`, `quit`, or `exit`

---

## Usage Tips

- **Be honest and specific:** The more detailed your answers, the more helpful the reflection.
- **Take your time:** There's no rush. Think about each question before answering.
- **You can skip:** If you don't want to answer a question, you can type "skip" or move on.
- **Type 'stop' to pause:** You can stop the session at any time by typing `stop`.
- **Your data is saved:** After completing the exercise, your responses will be saved as a JSON file with a timestamp.

---

## Troubleshooting

### "OPENAI_API_KEY is not set"
- Make sure your `.env` file is in the same folder as `reflektor_app.py`
- Check that there are no spaces around the `=` sign in your `.env` file
- Make sure the file is actually named `.env` and not `.env.txt`

### "No module named 'openai'"
- Make sure you activated the virtual environment (see Step 5)
- Try running `pip install -r requirements.txt` again

### "python3: command not found"
- Try using `python` instead of `python3`
- On Windows, make sure you checked "Add Python to PATH" during installation

### The assistant's responses seem strange
- Check your internet connection
- Make sure your OpenAI API key is valid and has credits
- Try lowering the `temperature` parameter in the code (line 95) to 0.3 for more consistent responses

---

## Safety Note

This app is **not a replacement for professional mental health care**. It's a tool for structured self-reflection. If you're experiencing a mental health crisis, please contact:
- **Emergency services:** 911 (US) or your local emergency number
- **Crisis Text Line:** Text HOME to 741741 (US)
- **National Suicide Prevention Lifeline:** 988 (US)

---

## Questions?

If you run into issues, check that:
1. Python 3.8+ is installed
2. You're in the correct folder
3. The virtual environment is activated
4. Your `.env` file has the correct API key
5. You have internet connection
