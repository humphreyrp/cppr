#!/usr/bin/env python

import sys
import subprocess

class WorkFile:
    filepath = '/tmp/repl.cpp'
    outfilepath = '/tmp/a.out'
    # Include a few common headers
    headers = [ '#include <iostream>' ]
    body = [] 
    line_count = 0
    line_history = []

    def __init__(self):
        pass

    def addLine(self, line):

        # Always add to our history
        self.line_history.append(line)

        # We won't add this to our list of code unless it's successfully compiled, so keep a local
        # copy of our headers and body
        headers = self.headers.copy()
        body = self.body.copy()

        if len(line) >= 1:
            if line[0] == '#':
                headers.append(line)
            else:
                body.append(line)
        else:
            # Empty string, just return a blank line
            return ''

        # Generate the string to write to the file including any necessary boilerplate
        body_str = ''
        header_str = ''
        for line in headers:
            header_str += (line + '\n')
        for line in body:
            body_str += (line + '\n')
        file_str = f"{header_str}\n int main()\n{{\n    {body_str}\n}}"

        # Open the file and generate
        try:
            with open(self.filepath, 'w') as f:
                f.write(file_str)
        except Exception as e:
            return e.what()

        # Compile
        out = subprocess.run(['g++', self.filepath, '-o', self.outfilepath], capture_output=True)
        if out.returncode != 0:
            return f"Compile Failed: {out.stderr.decode('utf-8')}"

        # Execute
        out = subprocess.run([self.outfilepath], capture_output=True)
        if out.returncode != 0:
            return f"Execution failed: {out.stderr.decode('utf-8')}"
        out_str = out.stdout.decode('utf-8')


        # Iterate over the new list and note all new items
        out_list_full = out_str.split('\n')
        out_list_trimmed = []
        for i in range(self.line_count, len(out_list_full)):
            line = out_list_full[i]
            stripped_line = line.strip()
            if len(line) > 0:
                out_list_trimmed.append(stripped_line)
                self.line_count += 1

        # Reconstruct
        out_str = ''
        for line in out_list_trimmed:
            out_str += (line)

        # Update our member variables
        self.headers = headers.copy()
        self.body = body.copy()

        return out_str

    def getLine(self, i):
        if i < len(self.line_history):
            return self.line_history[i]
        return ''


if __name__ == '__main__':

    try:
        wf = WorkFile()

        while True:
            line = input("> ")
            output = wf.addLine(line)
            if len(output) > 0:
                print(output)

    except KeyboardInterrupt:
        print("")

