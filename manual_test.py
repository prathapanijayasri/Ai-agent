import os
import sys
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from app.agent.executor import AgentExecutor

tests = [
    ["What is 25 * 4?"],
    ["Calculate (100 + 50) / 5."],
    ["What is artificial intelligence?"],
    ["Calculate 10 / 0."],
    ["My name is Mahesh.", "What is my name?"]
]

print("Starting Manual Tests\n" + "="*30)

executor = AgentExecutor()

for i, test in enumerate(tests):
    print(f"\n--- Test {i+1} ---")
    for msg in test:
        print(f"User: {msg}")
        retries = 3
        while retries > 0:
            try:
                response = executor.process_message(msg)
                print(f"Agent: {response}")
                break
            except Exception as e:
                if "503" in str(e) or "429" in str(e):
                    print(f"API busy, retrying... ({str(e)})")
                    time.sleep(2)
                    retries -= 1
                else:
                    print(f"Error: {e}")
                    break
