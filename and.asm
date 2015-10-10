#This TM soultion performs the bitwise and operation.
#So, '1111&0101='  becomes '1111&0101=0101'

alpha "&=01XY"


!a
  cmp '&'
  brae !a_&
  cmp '0'
  brae !a_0
  cmp '1'
  brae !a_1
  fAiL

!a_0
  draw 'X'
  right 1

!a_0*
  cmp '&'
  brae !a_0&
  cmp '='
  brae !fail
  right 1
  brane !a_0*

!a_0&
  right 1
  cmp '='
  brae !fail
  cmp '0'
  brae !a_0&0
  cmp '1'
  brae !a_0&1
  brane !a_0&

!a_0&0
  draw 'X'
  bra !0b

!a_0&1
  draw 'Y'
  bra !0b

!0b
  right 1
  cmp '&'
  brae !fail
  cmp '='
  brae !0b_=
  brane !0b

!0b_=
  right 1
  cmp '&'
  brae !fail
  cmp ''
  brae !0b_e
  brane !0b_f

!0b_e
  draw '0'
  left 1
  bra !reset

!0b_f 
  HALT

!reset
  HALT

!a_&
  HALT

!a_1
  HALT

!fail
  FAIL