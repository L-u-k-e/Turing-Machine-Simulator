```
    Label       !label_string        Equivalent to the address of the next line of 
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
```