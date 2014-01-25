'''
Created on Jan 25, 2014

@author: Vincent Ketelaars
'''

import sys
import os
import re

def main(args):
    if len(args) > 2:
        return
    file_ = args[0]
    hours = 1
    try:
        hours = int(args[1])
    except IndexError:
        print "No number supplied for hours, defaulting to %d" % (hours,)
    except ValueError:
        print "The supplied value %s is not a number" % (args[1],)  
    
    if hours < 1 or hours > 23:
        print "The supplied value %d cannot be used, it must be between 1 and 23" % (hours,)
        return
    
    print "Writing cron job for every %d hours to file %s" % (hours, file_)
    
    PWD = os.getenv("PWD")
    script = os.path.join(PWD, "run_once.sh")
    p = re.compile("0 \*/\d{1,2} \* \* \* " + script)
    command = "0 */" + str(hours) + " * * * " + script
    
    try:
        with open(file_, "w+b") as f:
            content = f.read()
            (content, num) = p.subn(command, content)
            if num == 0:
                content += command + "\r\n"
            f.write(content)
    except IOError:
        print "Could not open file", file_, sys.exc_info()

if __name__ == '__main__':
    main(sys.argv[1:])
    