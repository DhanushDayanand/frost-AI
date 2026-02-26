import json
from datetime import datetime
from openai import OpenAI


client = OpenAI(
    api_key="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"
)

SYSTEM_PROMPT = """
You are a scheduling assistant.

Extract hydration scheduling AND reminder timer information from user input.

Rules:
- Always return VALID JSON
- Use 24-hour time format (HH:MM)
- If a field is missing, use null
- If the user implies reminders (e.g., "remind me", "every 30 minutes"), enable hydration_timer
- If no interval is mentioned but reminders are implied, default interval_minutes to 30
- hydration_timer.start_time and end_time should usually match active_window
- Follow this schema exactly

Schema:
{
  "task": "hydration",

  "active_window": {
    "start": "HH:MM",
    "end": "HH:MM"
  },

  "hydration_timer": {
    "enabled": true,
    "interval_minutes": 30,
    "start_time": "HH:MM",
    "end_time": "HH:MM",
    "alert_message": "Time to drink water 💧"
  },

  "exclusions": [
    {
      "label": "string",
      "start": "HH:MM",
      "end": "HH:MM"
    },
    {
      "label": "string",
      "time": "HH:MM"
    }
  ]
}
"""


def parse_with_chatgpt(user_text: str) -> dict:
    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    )

    # Extract raw text output
    raw_output = response.output_text.strip()

    # Defensive JSON parsing
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON:\n{raw_output}") from e


def save_to_json(data: dict) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hydration_schedule_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"\n[SUCCESS] Schedule saved to {filename}")


if __name__ == "__main__":
    print("\n--- Hydration Scheduler with Timers (ChatGPT Powered) ---")
    print("Example input:")
    print("I work from 9am to 5pm, lunch 12:30 to 1:30,")
    print("remind me to drink water every 40 minutes, coffee at 4pm")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("User Schedule: ").strip()

        if user_input.lower() in {"exit", "quit", "q"}:
            print("Exiting. Stay hydrated 💧")
            break

        if not user_input:
            continue

        try:
            parsed_data = parse_with_chatgpt(user_input)

            print("\nParsed JSON Output:")
            print(json.dumps(parsed_data, indent=4))

            save_to_json(parsed_data)

        except Exception as e:
            print("❌ Error parsing input:", e)

        print("-" * 50)