"""Main entry point for todo-hackathon."""

from todo_hackathon.storage import TodoStorage
from todo_hackathon.commands import TodoCommands
from todo_hackathon.cli import CLIParser


def main():
    """Run the interactive todo application."""
    # Initialize components
    storage = TodoStorage()
    commands = TodoCommands(storage)
    parser = CLIParser(commands)
    
    print("Welcome to Todo Hackathon - Phase 1")
    print("Type 'help' for available commands or 'exit' to quit.\n")
    
    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = input("> ").strip()
            
            # Parse and execute
            command, args = parser.parse(user_input)
            result = parser.execute(command, args)
            
            # Handle exit
            if result == "EXIT":
                print("Goodbye!")
                break
            
            # Print result (if any)
            if result:
                print(result)
                print()  # Empty line for readability
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            print()


if __name__ == "__main__":
    main()

