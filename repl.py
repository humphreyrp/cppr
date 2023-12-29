#!/usr/bin/env python

import subprocess
import yaml


# Application class, handles
class Repl:
    header_lines = []
    body_lines = []
    line_count = 0

    def __init__(self):

        try:
            with open('./config.yaml') as f:
                self._cfg = yaml.safe_load(f.read())
        except Exception as e:
            print(f"Error reading configuration: {e}")
            raise

        self.compiler = self.get_cfg_or('compiler', 'g++')
        work_dir = self.get_cfg_or('work_dir', '/tmp')
        self.filepath = work_dir + '/repl.cpp'
        self.outfilepath = work_dir + '/a.out'

        default_headers = self.get_cfg_or('default_headers', [])
        for header in default_headers:
            self.header_lines.append(f"#include <{header}>")

    # Returns a configuration value if it exists in the config, otherwise the default value
    def get_cfg_or(self, key, default):
        if self._cfg.get(key) is not None:
            return self._cfg.get(key)
        else:
            return default

    # Generates a string of file content based on a list of body lines and header lines
    def build_file_content(self, body_lines, header_lines):

        # Generate the string to write to the file including any necessary boilerplate. Start with the includes.
        header_str = ''
        for i in range(0, len(header_lines)):
            header_str += (header_lines[i] + '\n')
            if i == len(header_lines) - 1: header_str += '\n'

        # Then add the body
        body_str = ''
        for i in range(0, len(body_lines)):

            # If the line doesn't end in a semicolon, we want to print the result to the display, so wrap it in
            # an iostream command
            line = body_lines[i]
            if line[len(line) - 1] != ';':
                line = f"std::cout << ({line}) << std::endl;"

            # Add to the body
            if i > 0: body_str += '\n'
            body_str += ('    ' + line)

        # Insert into our template
        return f'{header_str}int main()\n{{\n{body_str}\n}}'

    # Takes the execution output and returns a string of all new lines contained
    def handle_exec_output(self, out_str):

        # Create a list of all lines of output (not counting any empty lines)
        out_list_full = [ line for line in out_str.split('\n') if len(line.strip()) > 0 ]

        # The new lines are only the ones after our current line count
        out_list_new = out_list_full[self.line_count:]

        # Reconstruct the output using just the new lines
        out = ''
        for line in out_list_new:
            out += line.strip()

        # Update the line count so we know how many items to display next time
        self.line_count = len(out_list_full)

        return out

    def addLine(self, line):

        # We won't add this to our list of code unless it's successfully compiled, so keep a local
        # copy of our headers and body
        header_lines = self.header_lines.copy()
        body_lines = self.body_lines.copy()

        if len(line) >= 1:
            if line[0] == '#':
                header_lines.append(line)
            else:
                body_lines.append(line)
        else:
            # Empty string, just return a blank line
            return ''

        # Generate the file content
        file_content = self.build_file_content(body_lines, header_lines)

        # Open the file and generate
        try:
            with open(self.filepath, 'w') as f:
                f.write(file_content)
        except Exception as e:
            return e.what()

        # Compile
        out = subprocess.run([self.compiler, self.filepath, '-o', self.outfilepath], capture_output=True)
        if out.returncode != 0:
            return f"Compile Failed: {out.stderr.decode('utf-8')}"

        # Execute
        out = subprocess.run([self.outfilepath], capture_output=True)
        if out.returncode != 0:
            return f"Execution failed: {out.stderr.decode('utf-8')}"

        # Handle the execution output and get all the new lines
        new_lines_str = self.handle_exec_output(out.stdout.decode('utf-8'))

        # Update our member variables since this was successful
        self.header_lines = header_lines.copy()
        self.body_lines = body_lines.copy()

        return new_lines_str


if __name__ == '__main__':

    try:
        # Create the REPL object
        repl = Repl()

        while True:
            line = input("> ")
            output = repl.addLine(line)
            if len(output) > 0:
                print(output)

    except KeyboardInterrupt:
        print("")

