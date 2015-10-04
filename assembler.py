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
  'cmp':   ['001', 'A'],
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
  'cmp':   ['cmp'],
  'brae':  ['brae'],
  'brane': ['brane'],
  'bra':   [('brae',),('brane',)],
  'left':  ['move', 1],
  'right': ['move', 0],
  'draw':  ['draw', 0, 0],
  'erase': ['erase']
}













###############################  MAIN  #####################################
def main():
  global assembly_instructions
  global label_table  
  #Read the instructions into a 2d array of tokens. Ignore empty lines.
  assembly_instructions = [ line.split() for line in readlines(sys.argv[1]) 
                                          if not re.match(r'^\s*$', line)  ]
  
  #create label table, verify syntax, convert the instruction names 
  #to lower case and strip the comments from the token lists. Also, remove the 
  #label declarations. 
  assembly_instructions, label_table = createLabelTable(assembly_instructions) 
  
  #generate strings of '0's and '1's corresponding to the actual 
  #bitstrings that make up the machine level instructions. 
  machine_instructions = generateStrings()

  '''
  #convert strings to bytes
  machine_instructions = makeBytes(machine_instructions)

  #write bytes to file in big endian ordering.  
  pukeBytes(machine_instructions)
  '''











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
        label_table[token] = i - len(label_table)
    else:
      #Not a label declaration, check for syntax errors. 
      is_label = False
      instruction, comment_flag = extractValueFromToken(token)
      if instruction not in syntax_forms:
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
      trimmed_instructions.append(stripComments(_list))

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
      error_message = 'This instruction expects no arguments'
    elif form != 'noargs' and (comment_flag or (not arguments) or arguments[0][0] == '#'):
      error_message = "This instruction requires an argument, but none were found."
    elif form == 'label' and arguments and arguments[0][0] != '!':
      error_message = 'This instruction expects a label as its argument'
    elif form != 'noargs':
      argument, comment_flag2 = extractValueFromToken(arguments[0])
      if form == 'ascii_single' and not re.match(r"^'.?'#?.*$", argument):
        error_message = "The argument provided to this instruction must match: '.?'"
      elif form == 'ascii_multiple' and not re.match(r'^"[^"][^"]+"#?.*$', argument):
        error_message = 'The argument provided to this instruction must match ^"[^"][^"]+"$'
      elif form == 'number':
        try: 
          if int(argument) > 15 or int(argument) < 0:
            error_message = "This instruction only accepts integers between 0 and 15"
        except ValueError:
          error_message = "This instruction expects an integer argument."
      elif len(arguments) > 1 and arguments[1][0] != '#' and not comment_flag2:
        error_message = 'You may not provide more than 1 argument to this function'

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




#Take a list of tokens and strip anything after/including the first instance of 
#a '#', which is not: (inside '' or "" and is also in the second token) OR ( is  
#a part of a label)
def stripComments(tokens):
  new_token_list = []
  tokens = tokens[:2]
  if tokens[0][0] != '!': 
    token1_parts = tokens[0].split('#')
    new_token_list.append(token1_parts[0])
    if len(token1_parts) > 1:
      return new_token_list
  else:
    new_token_list.append(tokens[0])

  if(len(tokens) > 1):
    token2 = tokens[1]
    if token2[0]  in ("'", '"'):
      token2_parts = []
      if token2[0] == "'":
        token2_parts = re.split(r"('.?')", token2) 
      else:
        token2_parts = re.split(r'("[^"]*")', token2)

      new_token_list.append(token2_parts[1])
      if len(token2_parts) > 1:
        return new_token_list
    elif token2[0] == "!":
      new_token_list.append(token2)
    else:
      token2_parts = token2.split('#')
      new_token_list.append(token2_parts[0])
      if len(token2_parts) > 1:
        return new_token_list

  return new_token_list















###############################  PASS 2  #####################################

def generateStrings():
  #translate assembly instructions to their lower level equivs using the ISA_map
  decomposed_instructions = decomposeInstructions(); #things are still in english here
  #decomposed_instructions = optimizeInstructions(decomposed_instructions)

  #substitute the label strings with the line addresses, now that it's safe to do so.
  decomposed_instructions = replaceLabels(decomposed_instructions)
  '''
  bit_strings = generateBitStrings(decomposed_instructions)

  return bit_strings
  '''
  strings = []
  bits = ''
  function_map = {
    'A': A,
    'B': B,
    'C': C
  }
  for i, tokens in enumerate(decomposed_instructions):
    bits = ''
    instruction = tokens[0]
    args = tokens[1:] if len(tokens) else None
    op_info = op_codes[instruction]
    bits = op_info[0]
    bits += function_map[op_info[1]](*args)
    strings.append(bits)

  for i, bits in enumerate(strings):
    print("{0}{1}".format(str(decomposed_instructions[i]).ljust(25),  bits) )
    
    

#o=op code
#v=variable
#r=reserved
#i=integer
#c=char

#A:ooorrrrrcccccccc
#B:oooiiiiiiiiiiiii
#C:oooiiiivcccccccc
def A(char):
  return '{:013b}'.format(ord(char))

def B(address):
  return '{:013b}'.format(address)

def C(flag, arg2=False, arg3=False):
  flag = str(flag)
  number = '{:04b}'.format(arg2) if arg2 else '0000'
  char = '{:08b}'.format(ord(arg3)) if arg3 else '00000000'
  return number + flag + char



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
    elif [True for form in syntax_forms[instruction] if re.match(r'ascii_.*', form)]:
      #ascii_multiple's need to expand into multiple ascii_single's
      chars = arg[1:-1]
      for char in chars:
        result.append(machine_instruction_info + [char])
    else:
      arg = int(arg) if 'number' in syntax_forms[instruction] else arg
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
  global label_table
  for label in label_table.keys():
    if label_table[label] >= current_line:
      label_table[label] += incr 




def replaceLabels(token_lists):
  
  def substitue_labels(tokens):
    new_list = []
    for i, token in enumerate(tokens):
      push_me = label_table[token] if token in label_table else token
      new_list.append(push_me)
    return new_list

  result = list(map(substitue_labels, token_lists))
  return result











##########################  HELPER FUNCTIONS  ################################
#readlines of a file into a list
def readlines(filename):
  return [ line.strip() for line in open(filename) ]
















main()