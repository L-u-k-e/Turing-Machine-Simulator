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
  cmp ''
  brae !0b_e
  cmp '&'
  brae !fail
  brane !0b_=

!0b_e
  draw '0'
  left 1
  bra !reset



!a_1
  draw 'Y'
  right 1

!a_1*
  cmp '&'
  brae !a_1&
  cmp '='
  brae !fail
  right 1
  brane !a_1*

!a_1&
  right 1
  cmp '='
  brae !fail
  cmp '0'
  brae !a_0&0
  cmp '1'
  brae !a_1&1
  brane !a_1&

!a_1&1
  draw 'Y'
  bra !1b

!1b
  right 1
  cmp '&'
  brae !fail
  cmp '='
  brae !1b_=
  brane !1b

!1b_=
  right 1
  cmp ''
  brae !1b_e
  cmp '&'
  brae !fail
  brane !1b_=

!1b_e
  draw '1'
  left 1
  bra !reset




!reset
  left 1
  cmp '&'
  brae !reset_&
  brane !reset

!reset_&
  left 1
  cmp '0'
  brae !reset_&
  cmp '1'
  brae !reset_&
  right 1
  bra !a



!a_&
  right 1
  cmp 'X'
  brae !a_&
  cmp 'Y'
  brae !a_&
  cmp '='
  brae !clean
  brane !fail

!clean
  left 1
  cmp 'X'
  brae !clean_x
  cmp 'Y'
  brae !clean_y
  cmp '&'
  brae !clean
  right 1
  HALT

!clean_x
  draw '0'
  bra !clean

!clean_y
  draw '1'
  bra !clean

!fail
  FAIL