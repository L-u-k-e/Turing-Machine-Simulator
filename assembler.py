'''
Author:   Lucas Parzych
Class:    CS 441, William Confer
Date Due: 10/2/15
Desc:
  This is part one of programming assignment 2. It is an assembler for the 
  turing machine architecture we made up in class. Part two is the actual 
  simulator.

  Valid assembly instructions are as follows:
    
    Label       !labell_string        Equivalent to the address of the next line of 
                                      expected code. The identifiers can be any 
                                      non­whitespace characters led with an exclamation 
                                      point.

    Alphabet    alpha 'a'
                alpha "abABxy"        Adds an ASCII character to the internal alphabet 
                                      file. The second form is translated into multiple
                                      consecutive alpha instructions in the binary.

    Halt        halt                  Terminate successfully.

    Fail        fail                  Terminate with failure notice.

    Compare     cmp ‘X’               Compare the value on the tape (at the head 
                                      position) and set/clear an internal “equal” 
                                      register.

    Branch 
    if equal    brae !label_string    Branch to the address associated
                                      with the given label if the “equal”
                                      register was set (1)

    Branch 
    if not 
    equal       brane !label_string   Branch to the address associated
                                      with the given label if the “equal”
                                      register was clear (0)

    branch      bra                   Brach to the address associated 
                                      with the given label regardless of what
                                      is in the register. Expands to:
                                        brae !label_string
                                        brane !label_string                                    

    Left        left 4                Move the head to the left the given
                                      number of positions [0...15]

    Right       right 4               Move the head to the right the given
                                      number of posiitions [0...15]

    Draw        draw ‘X’              Draws the given character at the head.

    Erase       erase                 “Blanks” the tape at the head.


  Labels are case sensitive. Other instructions are not.

  Byte ordering is Big Endian 

  The assembler should output a binary file with the same name as the asm file but 
  with a ".bin" extension added to the end. For example, "input.asm" is converted 
  to "input.asm.bin".


'''

import sys
import re
import copy
import struct












############################### GLOBALS #####################################
assembly_instructions = []
label_table = {}

syntax_forms = {
  'alpha': ['ascii_single', 'ascii_multiple'],
  'halt':  ['noargs'],
  'fail':  ['noargs'],
  'cmp':   ['ascii_single'],
  'brae':  ['label'],
  'brane': ['label'],
  'bra':   ['label'],
  'left':  ['number'],
  'right': ['number'],
  'draw':  ['ascii_single'],
  'erase': ['noargs']
}


op_codes = {
  'alpha': ['000', 'A'],
  'cmp':   ['001', 'C'],
  'brane': ['010', 'B'],
  'brae':  ['011', 'B'],
  'draw':  ['100', 'C'],
  'move':  ['101', 'C'],
  'stop':  ['110', 'C'],
  'erase': ['111', 'C']
}


ISA_map = {
  'alpha': ['alpha'],
  'halt':  ['stop', 1],
  'fail':  ['stop', 0],
  'cmp':   ['cmp', 0, 0],
  'brae':  ['brae'],
  'brane': ['brane'],
  'bra':   [('brae',),('brane',)],
  'left':  ['move', 1],
  'right': ['move', 0],
  'draw':  ['draw', 0, 0],
  'erase': ['erase', 0]
}




















###############################  MAIN  #####################################
def main():
  global assembly_instructions
  global label_table  

  if len(sys.argv) != 2:
    sys.exit("This assembler expects 1 and only 1 input file.")

  #Read the instructions into a 2d array of tokens. Ignore empty lines.
  assembly_instructions = [ line.split() for line in readlines(sys.argv[1]) 
                                          if not re.match(r'^\s*$', line)  ]
  
  #create label table, verify syntax, convert the instruction names 
  #to lower case and strip the comments from the token lists. Also, remove the 
  #label declarations. (Pass 1)
  assembly_instructions, label_table = createLabelTable(assembly_instructions) 
  
  #generate the actual machine instructions (Pass 2)
  machine_instructions = generateMachineInstructions()

  #write bytes to file.  
  pukeBytes(machine_instructions, sys.argv[1]+'.bin')






























###############################  PASS 1  #####################################
#Report syntax errors and create the label table.
def createLabelTable(token_lists):
  global label_table

  #token_lists with comments and label declarations removed. 
  trimmed_instructions = []

  is_label = False
  for i, _list in enumerate(assembly_instructions):
    token = _list[0]
    if (re.match(r'^!.*', token)):
      #Found a label declaration. Check some edge cases, then create the label.
      if token in label_table: 
        abort(
          error_message = "Can't declare a label twice", 
          token = token,  
          label_flag = True
        )
      elif(len(_list) > 1) and (_list[1][0] != '#'):
        abort(
          error_message = "A label declaration can't share a line with any other tokens:", 
          token = "\t".join((token, _list[1])),
          label_flag = True
        )
      else:
        is_label = True
        label_table[token] = len(trimmed_instructions) 
    else:
      #Not a label declaration, check for syntax errors. 
      is_label = False
      instruction, comment_flag = extractValueFromToken(token)
      if not instruction: 
        continue
      elif instruction not in syntax_forms:
        abort(
          error_message = "Not a valid instruction",
          line_number = i
        )
      else:
        verifyArguments(
          instruction = instruction,
          comment_flag = comment_flag,
          arguments = _list[1:],
          line_number = i
        )

      #modify the original list to include the lowercase instruction name
      _list[0] = instruction

    if not is_label:
      trimmed_instructions.append(stripCommentsAndQuotes(_list))

  return trimmed_instructions, label_table










#Verify syntax of the arguments provided to the function.
#This is kind of a weird way to do it, because only one instruction has multiple
#forms, so I could have just detected 'alpha' as a special case, but I like the
#fact that this method is more extensible. (Any instruction can have multiple forms this way)
def verifyArguments(instruction, arguments, line_number, comment_flag=False):
  argforms = syntax_forms[instruction]
  valid = False
  official_error_message = "" 
  for form in argforms:
    error_message = "" 
    if form == 'noargs' and arguments and arguments[0][0] != '#' and not comment_flag:
      error_message = 'This instruction expects no arguments.'
    elif form != 'noargs' and (comment_flag or (not arguments) or arguments[0][0] == '#'):
      error_message = "This instruction requires an argument, but none were found."
    elif form == 'label' and arguments and arguments[0][0] != '!':
      error_message = 'This instruction expects a label as its argument.'
    elif form != 'noargs':
      argument = arguments[0]
      if form == 'ascii_single' and not ( re.match(r'^(("")|(\'\'))(#.*)?$', argument) or
                                          re.match(r"^'[^']'(#.*)?$", argument)       or
                                          re.match(r'^"[^"]"(#.*)?$', argument)         ):
        error_message = "The agument provided to this instruction must be a single valid ascii char"
        if 'ascii_multiple' in argforms:
          error_message += ' or a sequence of valid ascii chars.'
      elif form == 'ascii_multiple' and not ( re.match(r"^'[^'][^']+'(#.*)?$", argument) or
                                              re.match(r'^"[^"][^"]+"(#.*)?$', argument)   ):
        error_message = 'The argument provided to this instruction must be a valid ascii sequence.'

      argument, comment_flag2 = extractValueFromToken(arguments[0])
      if form == 'number':
        try: 
          if int(argument) > 15 or int(argument) < 0:
            error_message = "This instruction only accepts integers between 0 and 15."
        except ValueError:
          error_message = "This instruction expects an integer argument."
      elif len(arguments) > 1 and arguments[1][0] != '#' and not comment_flag2:
        error_message = 'You may not provide more than 1 argument to this instruction.'

    if error_message:
      official_error_message = error_message
    else:
      #If we get here, then the line matches one of the expected forms for this argument
      valid = True
      break
  
  if not valid:
    abort(
      line_number = line_number,
      error_message = official_error_message
    )
    









#Extracts everything before the first '#' and converts it to lowercase.
#Sets comment flag to True if a '#' was found.
def extractValueFromToken(token):
  parts = token.split('#')
  result = parts[0].lower()
  comment_flag = True if len(parts) > 1 else False
  return result, comment_flag










#print specified error message and then exit.
def abort(error_message, line_number=0, label_flag=0, token=""):  
  start = "Error processing instruction {0}:    {1}".format(line_number, assembly_instructions[line_number])
  if label_flag:
    start = "Error processing label declaration:  {0}".format(token)

  exit_message = "{0}\n\t{1}".format(start, error_message)
  sys.exit(exit_message)










#Take a list of tokens and strip comments and quote chars.
#label declarations shouldn't be passed to this function. 
def stripCommentsAndQuotes(tokens):
  new_token_list = []
  tokens = tokens[:2]

  token1_parts = tokens[0].split('#')
  new_token_list.append(token1_parts[0])

  if len(tokens) > 1 and len(token1_parts) == 1:
    arg = tokens[1]
    if arg[0] == '"':
      arg = re.sub(r'"([^"]*).*', r'\1', arg)
    elif arg[0] == "'":
      arg = re.sub(r"'([^']*)'.*", r'\1', arg)
    elif arg[0] != '!':
      arg = arg.split('#')[0]
    new_token_list.append(arg)

  return new_token_list





























###############################  PASS 2  #####################################

def generateMachineInstructions():
  #translate assembly instructions to their lower level equivs using the ISA_map
  decomposed_instructions = decomposeInstructions(); #things are still in english here
  
  #optimize instrution set for fewest cycles
  decomposed_instructions = optimizeInstructionSet(decomposed_instructions)

  #substitute the label strings with the line addresses, now that it's safe to do so.
  decomposed_instructions = replaceLabels(decomposed_instructions)
  
  #actually generate the machine code
  machine_instructions = makeBytes(decomposed_instructions)

  return machine_instructions










def decomposeInstructions():
  #Returns a list of token lists representing the decomposed instruction.
  def decompose(instruction_tokens):
    result = []
    instruction = instruction_tokens[0]
    arg = instruction_tokens[1] if len(instruction_tokens) > 1 else None
    machine_instruction_info = copy.deepcopy(ISA_map[instruction])
    operation = machine_instruction_info[0]
    if isinstance(operation, tuple): 
      #The instruction needs to expand into multiple *different* operations (i.e bra).
      for instr in machine_instruction_info:
        result.append(decompose([instr[0], arg])[0])
    elif 'ascii_multiple' in syntax_forms[instruction]:
      #ascii_multiple's need to expand into multiple ascii_single's
      for char in arg:
        result.append(machine_instruction_info + [char])
    else:
      if 'number' in syntax_forms[instruction]:
        arg = int(arg)
      elif instruction == 'cmp' and arg == '':
        machine_instruction_info[1] = 1

      if arg: 
        machine_instruction_info.append(arg)
      result.append(machine_instruction_info)

    return result

  decomposed_instructions = []
  cur = 0  
  for i, tokens in enumerate(assembly_instructions):
    equivalent_instruction_set = decompose(tokens)
    incr = len(equivalent_instruction_set) - 1
    adjustLabelTable( current_line=cur, incr=incr)
    cur += incr
    decomposed_instructions += equivalent_instruction_set
    cur += 1

  return decomposed_instructions










#As we are de-composing instructions and optimizing we will need to adjust the 
#lines that the respective labels point to.
def adjustLabelTable(current_line=0, incr=0):
  if incr != 0: 
    print(incr) 
  global label_table
  for label in label_table.keys():
    if label_table[label] >= current_line:
      label_table[label] += incr










def optimizeInstructionSet(instructions):
  return instructions










def replaceLabels(token_lists):
  
  def substitute_labels(tokens):
    new_list = []
    for i, token in enumerate(tokens):
      push_me = label_table[token] if token in label_table else token
      new_list.append(push_me)
    return new_list

  result = list(map(substitute_labels, token_lists))
  return result










def makeBytes(instructions):
  
  def A(char='\0'):
    return '{:013b}'.format(ord(char))

  def B(address):
    try:
      return '{:013b}'.format(address)
    except ValueError:
      abort(
        error_message = "This label was referenced but never declared:", 
        token = address,
        label_flag = True
      )
  def C(flag, arg2=False, arg3=False):
    flag = str(flag)
    number = '{:04b}'.format(arg2) if arg2 else '0000'
    char = '{:08b}'.format(ord(arg3)) if arg3 else '00000000'
    return number + flag + char  

  function_map = {
    'A': A,
    'B': B,
    'C': C
  }

  char_strings = [] #used for debugging
  bit_strings = []
  bits = ''
  for i, tokens in enumerate(instructions):
    bits = ''
    instruction = tokens[0]
    args = tokens[1:] if len(tokens) else None
    op_info = op_codes[instruction]
    bits = op_info[0]
    bits += function_map[op_info[1]](*args)
    int_value = int(bits, 2)
    big_endian_u_short = struct.pack('>H', int_value)
    bit_strings.append(big_endian_u_short)


  #uncomment for debugging (leave the indentation as is)
  #'''
    char_strings.append(bits)
  for i, bits in enumerate(char_strings):
    print("{0}{1}".format(str(instructions[i]).ljust(25),  bits) )
  #'''
  return bit_strings    










 





























##########################  IO FUNCTIONS  ################################
#readlines of a file into a list
def readlines(filename):
  try:
    return [ line.strip() for line in open(filename) ]
  except:
    sys.exit('Error: The provided filename "{0}" does not exist in this directory.'.format(filename))








#write each bit structure in an array to the specified output file
def pukeBytes(instructions, filename):
  out = open(filename, 'wb')
  for instruction in instructions:
    out.write(instruction)
  out.close()

























main()
'''
try:
  main()
except:
  print('Well, this is embarassing :/\nThere was an internal error during the assembly.')
'''