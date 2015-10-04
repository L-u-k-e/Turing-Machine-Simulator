import sys
import copy

RAM = []
PC = 0
STACK = []

TAPES = []

OUTPUT = file.open(sys.argv[2]+'.out', 'w')

def main():
  global RAM, TAPES

  RAM = slurpBits(sys.argv[1])
  TAPES = readlines(sys.argv[2])
  
  for tape in tapes:
    simulate(tape)
    
#  fetch(PC)
#  decode()
#  execute()


def simulate(input_tape):
  global OUTPUT
  tape = copy.copy(input_tape)






def fetch(PC):
  pass

def decode():
  pass

def execute():
  pass
  


def move(left, )


def slurpBits(filename):
  open(filename)
