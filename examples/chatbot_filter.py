# chatbot_filter.py: scrub PII from user input before sending to an LLM.
#
# Usage:
#   echo "My IBAN is GB29NWBK60161331926819" | python examples/chatbot_filter.py
#
# Integration point:
#   scrubbed = piigex.clean(user_message)
#   # -> send to LLM here:
#   # response = anthropic.Anthropic().messages.create(
#   #     model="claude-opus-4-5",
#   #     max_tokens=1024,
#   #     messages=[{"role": "user", "content": scrubbed}],
#   # )

import sys

import piigex

if __name__ == "__main__":
    user_message = sys.stdin.read()
    scrubbed = piigex.clean(user_message)
    print(scrubbed, end="")
