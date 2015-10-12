'''
  Author:  Lucas Parzych
  LICENSE: MIT
  SOURCE:  https://github.com/L-u-k-e/Turing-Machine-Simulator
'''
import sys
import copy
import struct










################################## GLOBALS #####################################
RAM = []
STACK = []
TAPES = []
ALPHA = []
HEAD = 0
PC = 0
REG = 0
BOOK = {}

OP_INFO = {
  '000':  ['alpha',         'A'],
  '001':  ['cmp',           'C'],
  '010':  ['brane',         'B'],
  '011':  ['brae',          'B'],
  '100':  ['drawAndMove',   'C'],
  '101':  ['move',          'C'],
  '110':  ['stop',          'C'],
  '111':  ['eraseAndMove',  'C'],
}



















################################### MAIN #######################################
def main():
  global RAM, TAPES
  RAM = ['1100000000000000'] * (2**13)
  RAM = merge(slurpInstructions(sys.argv[1]), RAM)
  TAPES = readlines(sys.argv[2])
   
  for tape in TAPES: 
    simulate(tape)




def simulate(input_tape):
  global TAPE, HEAD, ALPHA, PC, REG, IR, BOOK
  TAPE = initTape(input_tape) 
  HEAD = 0
  ALPHA = [False] * 256
  PC = 0
  REG = {'empty': True}

  BOOK['cycles'] = 0
  BOOK['moves'] = 0
  BOOK['writes'] = 0
  BOOK['exit status'] = ''
  while True:
    IR, PC = fetch(PC)
    control_signals = decode(IR)
    done = execute(**control_signals)
    BOOK['cycles'] += 1
    if done: break
  
  renderTape(TAPE, HEAD, BOOK)



















################################### FETCH ######################################
def fetch(pc):
  ir = RAM[pc]
  pc += 1
  return ir, pc



















################################## DECODE ######################################
def decode(bitstring):
  instruction = {}
  opcode = bitstring[:3]
  op_info = OP_INFO[opcode]
  instruction['instruction'] = op_info[0]
  instruction['arguments'] = getArguments(bitstring, op_info[1])
  return instruction





def getArguments(bitstring, instruction_type):
  return eval('{0} ( "{1}" )'.format(instruction_type, bitstring))

def A(bitstring):
  ordinal = int(bitstring[8:], 2)
  return { 'C': ordinal }


def B(bitstring):
  address = int(bitstring[3:], 2)
  return { 'A': address } 


def C(bitstring):
  n   = int(bitstring[3:7], 2)
  lhe = int(bitstring[7], 2)
  c   = int(bitstring[8:], 2)
  return { 'N': n, 'LHE': lhe, 'C': c }



















################################# EXECUTE ######################################
def execute(instruction, arguments):
  eval('{0} ( **{1} )'.format(instruction, arguments))
  done = True if instruction == 'stop' else False
  return done


def alpha(C=0):
  global ALPHA
  ALPHA[C] = True
  


def cmp(N=0, LHE=0, C=0):
  global REG
  if not LHE and not ALPHA[C]:
    stop()
  else:
    reg_item = {'ord': C}
    reg_item['empty'] = True if LHE else False
    REG = reg_item


def brane(A=0):
  global PC
  if not compareTapeItems(REG, TAPE[HEAD]):
    PC = A


def brae(A=0):
  global PC
  if compareTapeItems(REG, TAPE[HEAD]):
    PC = A


def drawAndMove(N=0, LHE=0, C=0):
  global TAPE, BOOK 
  TAPE[HEAD] = {'empty': False, 'ord': C}
  BOOK['writes'] += 1
  move(N, LHE) 


def move(N=0, LHE=0, C=0):
  global HEAD, TAPE, BOOK
  direction = -1 if LHE else 1
  HEAD += N * direction
  BOOK['moves'] += N

  #If we went off the end of the tape, extend the tape with blanks. 
  if not HEAD in range(0, len(TAPE)):
    start, end, reset = HEAD, 0, 0
    if HEAD > 0:
      end = len(TAPE)
      start = HEAD + 1
      reset = HEAD
    for _ in range(start, end, -direction):
      TAPE.insert(end, {'empty': True})
    HEAD = reset


def stop(N=0, LHE=0, C=0):
  global BOOK
  BOOK['exit status'] = "success" if LHE else "failure"



def eraseAndMove(N=0, LHE=0, C=0):
  global TAPE, BOOK
  TAPE[HEAD] = {'empty': True}
  BOOK['writes'] += 1
  move(N, LHE)



















############################# TAPE OPERATIONS ##################################
def initTape(input_string):
  tape = []
  for char in input_string:
    tape.append({ 'empty': False, 'ord': ord(char) })
  if not tape:
    tape.append({'empty': True})
  return tape


def compareTapeItems(item1, item2):
  eq = False
  try:
    if item1['empty'] and item2['empty']:
      eq = True
    elif item1['ord'] == item2['ord']:
      eq = True
  except KeyError:
    pass
  return eq


def renderTape(tape, head, book):
  out = sys.stdout.write
  for item in tape:
    char = ' ' if item['empty'] else chr(item['ord'])
    out(char)
  out('\n')
  for _ in range(0, head):
    out(' ')
  out('^\n')
  for key, value in book.items():
    out((key+':').ljust(15))
    out(str(value).rjust(10))
    out('\n')
  out('\n\n\n\n')



















######################## INITIALIZATION PROCEDURES #############################
def slurpInstructions(filename):
  instructions = []
  with open(filename, 'rb') as f:
    for chunk in iter(lambda: f.read(2), b''):
      instruction = ''.join(['{:08b}'.format(byte) for byte in chunk])
      instructions.append(instruction)
  return instructions


def merge(list1, list2):
  return list1 + list2[len(list1):]
  


#readlines of a file into a list
def readlines(filename):
  try:
    return [ line.strip() for line in open(filename) ]
  except:
    sys.exit('Error: The provided filename "{0}" does not exist in this directory.'.format(filename))
 

















  
main()