import json
import os
import sys

# Ensure backend package can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.agent.executor import AgentExecutor

def run_evaluations():
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not set. Cannot run evaluations.")
        sys.exit(1)

    with open(os.path.join(os.path.dirname(__file__), 'test_cases.json'), 'r') as f:
        cases = json.load(f)

    success_count = 0

    print("=================================")
    print("Agent Evaluation Runner")
    print("=================================")

    for case in cases:
        print(f"\nRunning Case {case['id']}: {case['description']}")
        
        executor = AgentExecutor()
        responses = []
        
        for user_input in case['inputs']:
            print(f"User: {user_input}")
            response = executor.process_message(user_input)
            responses.append(response)
            print(f"Agent: {response}")
            
        tool_used = any(msg.role == "tool" for msg in executor.state.messages)
        tool_used_name = next((msg.name for msg in executor.state.messages if msg.role == "tool"), None)

        passed = True
        
        if case['expected_tool']:
            if not tool_used or tool_used_name != case['expected_tool']:
                passed = False
                print(f"FAILED: Expected tool {case['expected_tool']}, but got {tool_used_name}")
            else:
                print(f"SUCCESS: Used tool {tool_used_name} as expected.")
        else:
            if tool_used:
                passed = False
                print(f"FAILED: Expected no tool, but used {tool_used_name}")
            else:
                print(f"SUCCESS: Answered directly without tools.")

        if passed:
            success_count += 1
            print("Status: PASSED")
        else:
            print("Status: FAILED")
            
    print("\n=================================")
    print(f"Evaluation Complete: {success_count}/{len(cases)} Passed")
    print("=================================")

if __name__ == "__main__":
    run_evaluations()
