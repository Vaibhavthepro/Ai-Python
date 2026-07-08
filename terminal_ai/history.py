class HistoryManager:
    def __init__(self):
        self.history = []
        self.index = -1

    def add_command(self, command: str):
        if not command.strip():
            return
        # If it's the same as the last command, don't duplicate
        if self.history and self.history[-1] == command:
            self.index = len(self.history)
            return
            
        self.history.append(command)
        self.index = len(self.history)

    def get_previous(self) -> str:
        if self.index > 0:
            self.index -= 1
            return self.history[self.index]
        elif self.index == 0 and self.history:
            return self.history[0]
        return ""

    def get_next(self) -> str:
        if self.index < len(self.history) - 1:
            self.index += 1
            return self.history[self.index]
        else:
            self.index = len(self.history)
            return ""
