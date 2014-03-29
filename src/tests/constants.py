'''
Created on Jan 20, 2014

@author: Vincent Ketelaars
'''
import os

TEST_DIRECTORY = "/tmp"
if os.name == "nt":
    TEST_DIRECTORY = "C:\Temp"

TEST_MAX_WAIT = 10.0 # Seconds