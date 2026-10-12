import sys
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

# Ensure tools are loaded
import app.agent.tools

from .executor import AgentExecutor

def main():
    print("=================================")
    print("AI Agent CLI")
    print("Type 'exit' to quit")
    print("=================================")
    
    try:
        executor = AgentExecutor()
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        sys.exit(1)

    while True:
        try:
            user_input = input("\nUser: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']:
                break
            
            response = executor.process_message(user_input)
            print(f"\nAgent: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
