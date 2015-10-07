import sys
import copy
import struct



################################## GLOBALS #####################################
RAM = []
STACK = []
TAPES = []
OUTPUT = open(sys.argv[2]+'.out', 'w')

OP_INFO = {
  '000':  ['alpha',         'A'],
  '001':  ['cmp',           'A'],
  '010':  ['brane',         'B'],
  '011':  ['brae',          'B'],
  '100':  ['drawAndMove',   'C'],
  '101':  ['move',          'C'],
  '110':  ['stop',          'C'],
  '111':  ['eraseAndMove',  'C'],
}



















def main():
  global RAM, TAPES

  RAM = slurpInstructions(sys.argv[1])
  TAPES = readlines(sys.argv[2])
   
  for tape in tapes:
    simulate(tape)
    




def simulate(input_tape):
  global OUTPUT, IR
  TAPE = initTape(input_tape) 
  HEAD = 0
  ALPHA = [False] * 256
  PC = 0
  REG = 0
  
  IR, PC = fetch(PC)
  control_signals = decode(IR)
  execute(**control_signals)



















def fetch(pc):
  ir = RAM[pc]
  pc += 1
  return ir, pc



















def decode(bitstring):
  instruction = {}
  opcode = bitstring[:3]
  op_info = OP_INFO[opcode]
  instruction['name'] = op_info[0]
  instruction['arguments'] = getArguments(bitstring, op_info[1])
  return instruction





def getArguments(bitstring, instruction_type):
  eval('{0} ( {1} )'.format(instruction_type, bitstring))

def A(bitstring):
  ordinal = int(bitstring[8:], 2)
  return { 'C': ordinal }


def B(bitstring):
  address = int(bitstring[3:], 2)
  return { 'A': address } 


def C(bitstring):
  n  = int(bitstring[3:7], 2)
  lh = int(bitstring[7], 2)
  c  = int(bitstring[8:], 2)
  return { 'N': n, 'LH': lh, 'C': c }



















def execute(instruction, arguments):
  nonlocal TAPE, HEAD, ALPHA, REG
  eval('{0} ( **{1} )'.format(instruction, arguments))


def alpha(C=0):
  nonlocal ALPHA
  ALPHA[C] = True
  


def cmp(C=0):
  if not ALPHA[C]:
    execute('stop')
  else:


def brane(A=0):
  pass


def brae(A=0):
  pass


def drawAndMove(N=0, LH=0, C=0):
  pass

def move(N=0, LH=0, C=0):
  pass


def stop(N=0, LH=0, C=0):
  pass

def eraseAndMove(N=0, LH=0, C=0):
  pass



















def initTape(input_string):
  tape = []
  for char in input_string:
    tape.append({ 'empty': False, 'char': char })
  return tape


def compareTapeItems(item1, item2):
  eq = False
  if item1['char'] == item2['char']:
    eq = True
  elif item1['empty'] and item2['empty']:
    eq = True
  return eq



















def slurpInstructions(filename):
  instructions = []
  with open(filename, 'rb') as f:
    for chunk in iter(lambda: f.read(2), b''):
      instruction = ''.join(['{:08b}'.format(byte) for byte in chunk])
      instructions.append(instruction)
  return instructions
 

















  
main()