Turing Machine Simulator
===
Both an assembler and a simulator for a fictitous architecture whose sole purpose is to simulate a classical Turing Machine.

Dependencies:
---
Python 3+: https://www.python.org/downloads/

Usage
---
 - When you're writing the assembly, keep in mind that labels are case sensitive, but other instructions are not.
 - Compile the assembly code with assembler.py like: `python assembler.py assembly_file.asm`.
 - This will create a binary (big endian ordering) named `(sys.argv[2]).bin` e.g. `assembly_file.asm.bin`.
 - Pass the binary as the first argument to `simulator.py`. The second argument should be the tape file. The tape file should be a set of newline delimited character strings that you would like the run the TM solution on.
 - Running the simulator might look like: `python simulator.py assembly_file.asm.bin input.tape`
 - Results will be logged to console.



##Supported Assembly Instructions

 - **Label Declaration**       
  - `!label_string`        
  -  Equivalent to the address of the next line of expected code. The identifiers can be any non­whitespace characters led with an exclamation point.


 - **Alphabet Addition**   
  - `alpha 'a'`
  - `alpha "a"` 
  - `alpha "abABxy"`
  - `alpha 'abABxy'`
  - Adds an ASCII character to the internal alphabet file. The second form is translated into multiple consecutive alpha instructions in the binary.


 - **Halt**        
  - `halt`                  
  - Terminate successfully.


 - **Fail**
  - `fail`
  - Terminate with failure notice.


 - **Compare**     
  - `cmp ‘X’`
  - `cmp "X"`               
  - Compare the value on the tape (at the head position) and set/clear an internal “equal” register.


 - **Branch if equal**
  - `brae !label_string`    
  - Branch to the address associated with the given label if the “equal” register was set (1)


 - **Branch if not equal**
  - `brane !label_string`   
  - Branch to the address associated with the given label if the “equal” register was clear (0)


 - **branch**      
  - `bra !label_string`                   
  - Brach to the address associated with the given label regardless of what is in the register. Expands to: `brae !label_string` `brane !label_string`                                    


 - **Left**        
  - `left N`                
  - Move the head to the left N positions  ( 0 <= N <= 15 )


 - **Right**       
  - `right N`        
  - Move the head to the right N positions  ( 0 <= N <= 15 )


 - **Draw**        
  - `draw ‘X’`
  - `draw "X"`
  - Draws the given character at the head.


 - **Erase**       
  - `erase`                 
  - “Blanks” the tape at the head.






Machine Level ISA 
---
 - **key**
  - O = opcode bit
  - N = unsigned integer bit
  - F = flag
  - C = character
  - R = reserved
 
- **Operation Classes:**
 - A: `OOORRRRRCCCCCCCC`
 - B: `OOONNNNNNNNNNNNN`
 - C: `OOONNNNFNNNNNNNN` OR `OOORRRRFCCCCCCCC` OR `OOORRRRFRRRRRRRR`

- **Alpha: `000`**
 - Class: A
 - add the specified char to the internal alphabet file.

- **cmp: `001`**
 - Class: C
 - compare contents of tape at head with the specified char, set the register accordingly. use F as a boolean to indicate that the comparison should be done against a "blank"

- **brane: `010`**
 - Class: B
 - branch to the address specified by the provided 13 bit int if the eq register is set to False
 
- **brane: `011`**
 - Class: B
 - branch to the address specified by the provided 13 bit int if the eq register is set to True

- **draw/move: `100`**
 - Class: C
 - draw the char specified by the final 8 bits. Then, move following the same rules as the move instruction.

- **move: `101`**
 - Class: C
 - Move the number of positions specified by the first 4 `NNNN` move left if F is 1, otherwise move right. 

- **stop: `110`**
 - Class: C
 - stop processing instructions. If F is 1 exit with sucess, otherwise exit with failure. 

- **erase/move: `111`**
 - Class: C
 - "blank" the tape at the head. The move following the same rules as the move instruction. 
 
