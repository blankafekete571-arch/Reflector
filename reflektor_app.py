"""
Structured self-reflection exercise (CBT-style) — Reflektor

This application contains a simple OpenAI-backed chatbot that guides the user 
through a structured self-reflection exercise (CBT-style).

Exercise steps (short):
1. Situation – What happened?
2. Physical sensations – What bodily sensations appeared?
3. Automatic thoughts – What thoughts went through your mind?
4. Emotions – What emotions were present?
5. Meaning / interpretation – What did this mean to you?
6. Alternative perspective – Is there another possible interpretation?
7. Next-step intention (optional)
8. Closure

Important assistant rules (the system follows):
- Ask one question at a time and wait for the user's answer.
- Do not give advice.
- Do not judge.
- Do not make diagnoses.
"""

import os
import json
import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# SYSTEM_PROMPT (English)
# This prompt defines the assistant behavior and the structured self-reflection exercise rules.
SYSTEM_PROMPT = """
You are a structured, safe self-reflection assistant. Your task is to guide the user, step-by-step, through a CBT-style self-reflection exercise about a specific situation. Strictly follow the rules below:

- Ask only one question at a time and wait for the user's answer before proceeding.
- Do not give advice, do not propose solutions, do not judge, and do not make diagnoses.
- Keep a compassionate, neutral, and non-directive tone.
- If the user indicates immediate danger (e.g., self-harm, abuse), ask about safety in a calm way and recommend contacting local emergency services or a crisis line — do not provide therapeutic instructions.

Follow these exercise steps in order (allow the user to skip any step they prefer not to answer):
1) Situation — "What happened?" (ask for a short, concrete description)
2) Physical sensations — "What bodily sensations did you notice?"
3) Automatic thoughts — "What thoughts went through your mind?"
4) Emotions — "What emotions were present?"
5) Meaning / interpretation — "What did this mean to you?"
6) Alternative perspective — "Can you see another possible interpretation?"
7) Next-step intention (optional) — "Is there a small next step you might take?"
8) Closure — brief summary, closing and thank you

After each user answer:
- Provide a brief, neutral one-sentence summary of the user's answer (reflective, not evaluative).
- Then ask the next question if applicable.

Always follow the rules: do not diagnose, do not give therapy, and ask only one question at a time.
"""

# Steps and questions (English)
STEPS = [
    {"id": 1, "title": "Situation", "question": "Briefly: what happened? Please describe a specific situation."},
    {"id": 2, "title": "Physical sensations", "question": "What physical sensations did you notice in that situation? (e.g., tightness in chest, sweating, tension)"},
    {"id": 3, "title": "Automatic thoughts", "question": "What thoughts ran through your mind during the situation?"},
    {"id": 4, "title": "Emotions", "question": "What emotions were present? Name them briefly."},
    {"id": 5, "title": "Meaning / interpretation", "question": "What did this mean to you? What interpretation did you give to the events?"},
    {"id": 6, "title": "Alternative perspective", "question": "Can you identify another possible interpretation of the situation? (Try to name at least one alternative)"},
    {"id": 7, "title": "Next-step intention (optional)", "question": "Is there a small next step you might take related to this situation? (optional)"},
    {"id": 8, "title": "Closure", "question": "Briefly: is there anything else you want to add before we finish the exercise?"}
]


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


def get_openai_client():
    """Create and return an OpenAI client instance.
    Make sure OPENAI_API_KEY is set in the environment.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Please set it as an environment variable.")
    return OpenAI(api_key=api_key)


def call_openai_chat(messages, model=DEFAULT_MODEL, temperature=0.4, max_tokens=500):
    """Simple wrapper for OpenAI ChatCompletion using the latest API.
    Make sure OPENAI_API_KEY is set in the environment.
    """
    client = get_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content


def run_reflection_session(auto_save=False, save_path=None):
    """Simple command-line session for the structured self-reflection exercise.

    Behavior:
    - The assistant guides the conversation naturally through the exercise steps.
    - Steps are tracked internally to ensure the conversation follows the structure.
    - The assistant only moves to the next step when the user provides a relevant answer.
    """
    history = []  # list of {step_id, title, question, answer, assistant_response}
    current_step_index = 0
    
    # base system message with enhanced instructions
    enhanced_system_prompt = SYSTEM_PROMPT + f"""

You are currently guiding the user through step {STEPS[current_step_index]['id']}: {STEPS[current_step_index]['title']}.
Your goal for this step is: {STEPS[current_step_index]['question']}

Your first message should ask this question naturally in your own words - start immediately with the question in a warm, welcoming tone.

After the user responds:
- Provide a brief, empathetic acknowledgment of their answer (1-2 sentences)
- Only move to the next step if their answer addresses the current step's focus
- If their answer is off-topic or unclear, gently guide them back to the current question
- When ready to move to the next step, naturally transition to the next question
"""
    
    system_msg = {"role": "system", "content": enhanced_system_prompt}
    messages = [system_msg]
    
    # Start the conversation - assistant asks first question
    try:
        # Use an empty user message to trigger the assistant's first response
        messages.append({"role": "user", "content": "Hi"})
        assistant_response = call_openai_chat(messages)
        messages.append({"role": "assistant", "content": assistant_response})
        print(f"\n[Step {current_step_index + 1}/{len(STEPS)}: {STEPS[current_step_index]['title']}]")
        print(f"\nAssistant: {assistant_response}\n")
    except Exception as e:
        print(f"Error starting session: {e}")
        return history

    # Main conversation loop
    while current_step_index < len(STEPS):
        user_input = input("> ").strip()
        
        if user_input.lower() in ("stop", "quit", "exit"):
            print("\nAssistant: Thank you for your time. The session has been paused. Take care.")
            break
            
        if not user_input:
            print("(Please provide a response, or type 'stop' to exit)")
            continue
        
        # Add user message
        messages.append({"role": "user", "content": user_input})
        
        # Update system message with current step context
        current_step = STEPS[current_step_index]
        is_last_step = (current_step_index == len(STEPS) - 1)
        
        # Build context instruction for the assistant
        context_instruction = f"""
Current step: {current_step['id']} - {current_step['title']}
Goal: {current_step['question']}

Evaluate if the user's response addresses this step adequately.
- If yes: Acknowledge their answer briefly and empathetically, then move to the next step by asking the next question naturally. END your response with the marker: [ADVANCE]
- If no: Gently guide them back to the current question without being pushy. Do NOT include the [ADVANCE] marker.

{'This is the final step. After acknowledging, provide a warm closure and summary. Include [ADVANCE] to mark completion.' if is_last_step else f"Next step will be: {STEPS[current_step_index + 1]['title']}" if current_step_index < len(STEPS) - 1 else ''}

IMPORTANT: Only include [ADVANCE] at the very end of your message if the user's answer genuinely addressed the current step's question.
"""
        
        # Temporarily add instruction (won't be saved to messages permanently)
        temp_messages = messages + [{"role": "system", "content": context_instruction}]
        
        try:
            assistant_response = call_openai_chat(temp_messages)
            
            # Check if we should advance based on the [ADVANCE] marker
            should_advance = "[ADVANCE]" in assistant_response
            
            # Remove the marker from the response before showing to user
            assistant_response_clean = assistant_response.replace("[ADVANCE]", "").strip()
            
            messages.append({"role": "assistant", "content": assistant_response_clean})
            
            # Save to history
            history.append({
                "step_id": current_step['id'],
                "title": current_step['title'],
                "question": current_step['question'],
                "answer": user_input,
                "assistant": assistant_response_clean
            })
            
            if should_advance and not is_last_step:
                current_step_index += 1
                print(f"\n[Step {current_step_index + 1}/{len(STEPS)}: {STEPS[current_step_index]['title']}]")
            
            print(f"\nAssistant: {assistant_response_clean}\n")
            
            if is_last_step and should_advance:
                # Exercise complete
                break
                
        except Exception as e:
            assistant_response = f"I apologize, but I encountered an error: {e}"
            print(f"\nAssistant: {assistant_response}\n")
            break

    # Save option
    if history:
        print("\n--- Exercise complete ---")
        if auto_save or (save_path is not None):
            if save_path is None:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = f"reflection_session_{timestamp}.json"
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            print(f"Your responses were saved: {save_path}")

    return history


if __name__ == '__main__':
    print("Reflektor — structured self-reflection exercise")
    print("Make sure you have set the OPENAI_API_KEY environment variable.")
    try:
        run_reflection_session()
    except Exception as e:
        print(f"An error occurred: {e}")
