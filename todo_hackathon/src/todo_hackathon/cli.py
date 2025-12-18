"""CLI parser for todo commands."""

import shlex
from typing import List, Tuple, Optional
from todo_hackathon.commands import TodoCommands


class CLIParser:
    """Parse and validate CLI commands."""
    
    def __init__(self, commands: TodoCommands):
        """Initialize with commands instance."""
        self.commands = commands
    
    def parse(self, input_line: str) -> Tuple[str, List[str]]:
        """
        Parse a command line.
        
        Args:
            input_line: Raw input from user
            
        Returns:
            Tuple of (command, args)
        """
        if not input_line or not input_line.strip():
            return ("", [])
        
        # Use shlex to handle quoted strings properly
        parts = shlex.split(input_line.strip())
        command = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        return (command, args)
    
    def execute(self, command: str, args: List[str]) -> str:
        """
        Execute a parsed command.
        
        Args:
            command: Command name
            args: Command arguments
            
        Returns:
            Command output
        """
        if not command:
            return ""
        
        if command == "add":
            if not args:
                return "Error: 'add' requires a title. Usage: add <title> [description]"
            title = args[0]
            description = " ".join(args[1:]) if len(args) > 1 else None
            return self.commands.add(title, description)
        
        elif command == "list":
            return self.commands.list_todos()
        
        elif command == "view":
            if not args:
                return "Error: 'view' requires an ID. Usage: view <id>"
            try:
                todo_id = int(args[0])
                return self.commands.view(todo_id)
            except ValueError:
                return "Error: ID must be a number"
        
        elif command == "complete":
            if not args:
                return "Error: 'complete' requires an ID. Usage: complete <id>"
            try:
                todo_id = int(args[0])
                return self.commands.complete(todo_id)
            except ValueError:
                return "Error: ID must be a number"
        
        elif command == "incomplete":
            if not args:
                return "Error: 'incomplete' requires an ID. Usage: incomplete <id>"
            try:
                todo_id = int(args[0])
                return self.commands.incomplete(todo_id)
            except ValueError:
                return "Error: ID must be a number"
        
        elif command == "update":
            if len(args) < 3:
                return "Error: 'update' requires ID, field, and value. Usage: update <id> <field> <value>"
            try:
                todo_id = int(args[0])
                field = args[1]
                value = " ".join(args[2:])  # Allow multi-word values
                return self.commands.update(todo_id, field, value)
            except ValueError:
                return "Error: ID must be a number"
        
        elif command == "delete":
            if not args:
                return "Error: 'delete' requires an ID. Usage: delete <id>"
            try:
                todo_id = int(args[0])
                return self.commands.delete(todo_id)
            except ValueError:
                return "Error: ID must be a number"
        
        elif command == "help":
            return self.commands.help()
        
        elif command == "exit":
            return "EXIT"
        
        else:
            return f"Error: Unknown command '{command}'. Type 'help' for available commands."

