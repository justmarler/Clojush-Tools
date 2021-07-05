#!/usr/bin/python

# Command-line arguments:
# - Directory of log files
# - (Optional) list of run numbers to use

import os, sys, re

# Some functions
def median(lst):
    if len(lst) <= 0:
        return False
    sorts = sorted(lst)
    length = len(lst)
    if not length % 2:
        return (sorts[length / 2] + sorts[length / 2 - 1]) / 2.0
    return sorts[length / 2]

def mean(nums):
    if len(nums) <= 0:
        return False
    return sum(nums) / float(len(nums))

def reverse_readline(filename, buf_size=8192):
    """a generator that returns the lines of a file in reverse order
       From: https://stackoverflow.com/questions/2301789/read-a-file-in-reverse-order-using-python"""
    with open(filename) as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        total_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(total_size, offset + buf_size)
            fh.seek(-offset, os.SEEK_END)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split('\n')
            # the first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # if the previous chunk starts right from the beginning of line
                # do not concact the segment to the last line of new chunk
                # instead, yield the segment first 
                if buffer[-1] != '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if len(lines[index]):
                    yield lines[index]
        yield segment


outputDirectory = sys.argv[1]

if outputDirectory[-1] != '/':
    outputDirectory += '/'

dirList = os.listdir(outputDirectory)

if not os.path.exists(outputDirectory + 'distributions/'):
    os.makedirs(outputDirectory + 'distributions/')

outputFilePrefix = "log"
outputFileSuffix = ".txt"

i = 0

expression = r'^{:instruction (.*), :count ([0-9]*), :dcdf ([0-9]*)}'
matcher = re.compile(expression)

while (outputFilePrefix + str(i) + outputFileSuffix) in dirList:

    fileName = (outputFilePrefix + str(i) + outputFileSuffix)

    if os.path.getsize(outputDirectory + fileName) == 0:
        i += 1
        continue
    
    distributions = []

    prev_line = ""
    for line in reverse_readline(outputDirectory + fileName):
        if (line.startswith('Adaptive Source')):
            break

        # Handle newlines that separated outputs.
        match = matcher.match(line)
        if match is None:
            if prev_line == "":
                prev_line = line
                continue
            else:
                line += r'\n' + prev_line
                match = matcher.match(line)
                prev_line = ""
        
        instruction, count, dcdf = match.groups()
        instruction = instruction.replace('\t', r'\t')
        instruction = instruction.replace('"', "")
        distributions.append([instruction, count, dcdf])

    with open(outputDirectory + 'distributions/' +\
        outputFilePrefix + str(i) + 'adaptive.tsv', 'w+') as res:

        res.write('instruction\tcount\tdcdf\n')
        for distr in distributions:
            res.write('\t'.join(distr) + '\n')

    i += 1