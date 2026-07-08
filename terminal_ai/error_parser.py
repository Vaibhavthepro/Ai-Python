import re

class ErrorAnalyzer:
    def __init__(self):
        # Matches standard Python exceptions
        self.error_pattern = re.compile(r"^(\w+Error|Exception):\s*(.*)")
        self.traceback_pattern = re.compile(r"Traceback \(most recent call last\):")
        
        self.in_traceback = False
        self.current_traceback = []

    def process_line(self, line: str):
        """
        Scans a line for python errors.
        Returns a dictionary with error info if a complete traceback is found, else None.
        """
        line_stripped = line.rstrip()
        
        if self.traceback_pattern.search(line_stripped):
            self.in_traceback = True
            self.current_traceback = [line_stripped]
            return None

        if self.in_traceback:
            self.current_traceback.append(line_stripped)
            match = self.error_pattern.search(line_stripped)
            
            # The actual error type is unindented at the end of the traceback
            if match and not line.startswith(" ") and not line.startswith("\t"): 
                self.in_traceback = False
                error_type = match.group(1)
                error_msg = match.group(2)
                full_tb = "\n".join(self.current_traceback)
                self.current_traceback = []
                
                return {
                    "type": error_type,
                    "msg": error_msg,
                    "traceback": full_tb
                }
        return None
