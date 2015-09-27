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














############################### GLOBALS #####################################
assembly_instructions = []
instruction_set = {
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

op_codes = [
  'alpha', #000
  'cmp',   #001
  'brane', #010
  'brae',  #011
  'draw',  #100
  'move',  #101
  'stop',  #110
  'erase', #111
]














###############################  MAIN  #####################################
def main():
  global assembly_instructions
  
  #Read the instructions into a 2d array of tokens. Ignore empty lines.
  assembly_instructions = [ line.split() for line in readlines(sys.argv[1]) 
                                          if not re.match(r'^\s*$', line)  ]
  
  #First pass: create label table, verify syntax, lowercase the instruction names 
  #and strip comments
  label_table = createLabelTable() 

  print(assembly_instructions)
'''
  #Second pass: optimize and generate machine code
  comment_flag = False
  for i, list in enumerate(assembly_instructions):
    instruction, comment_flag = extractValueFromToken(list[0]):
    if instruction in label_table:
      continue
    elif instruction not in instruction_set:
      abort(
        error_message = "Not a valid instruction",
        line_number = i
      )
    else:
      generateMachineInstruction(instruction, comment_flag, list[1:])
'''















###############################  PASS 1  #####################################
#Report syntax errors and create the label table.
def createLabelTable():
  global assembly_instructions
  label_table = {}
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
        label_table[token] = i
    else:
      #Not a label declaration, check for syntax errors. 
      instruction, comment_flag = extractValueFromToken(token)
      if instruction not in instruction_set:
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

      #modify the original list to include the lowercased instruction name
      assembly_instructions[i] = _list[1:]
      assembly_instructions[i].insert(0, instruction)

    #strip comments
    assembly_instructions[i] = stripComments(assembly_instructions[i])





#Verify syntax of the arguments provided to the function.
#This is kind of a weird way to do it, because only one instruction has multiple
#forms, so I could have just detected 'alpha' as a special case, but I like the
#fact that this method is more extensible. (Any instruction can have multiple forms this way)
def verifyArguments(instruction, arguments, line_number, comment_flag=False):
  argforms = instruction_set[instruction]
  valid = False
  official_error_message = "" 
  for form in argforms:
    error_message = "" 
    if form == 'noargs' and arguments and arguments[0][0] != '#' and not comment_flag:
      error_message = 'This instruction expects no arguments'
    elif form == 'label' and arguments[0][0] != '!':
      error_message = 'This instruction expects a label as its argument'
    elif form != 'noargs':
      argument, comment_flag2 = extractValueFromToken(arguments[0])
      if comment_flag or not arguments or arguments[0][0] == '#':
        error_message = "This instruction requires an argument, but none were found."
      elif form == 'ascii_single' and not re.match(r"^'.?'#?.*$", argument):
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

    if not error_message:
      #If we get here, then line matches one of the expected forms for this argument
      valid = True
      break
  
  if not valid:
    abort(
      line_number = line_number,
      error_message = error_message
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
#a '#', which is: (not inside '' or "" and is also in the second token) OR ( is a 
#part of a label)
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




















##########################  HELPER FUNCTIONS  ################################
#readlines of a file into a list
def readlines(filename):
  return [ line.strip() for line in open(filename) ]
















main()