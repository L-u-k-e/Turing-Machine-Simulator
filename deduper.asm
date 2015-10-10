#This TM solution dedups consecutive strings of a's,b's and c's respectively. 
#So, 'aabcccbbba' becomes 'abcba' 

alpha "abc&-"

#Begin: If we read empty, halt. Otherwise, put an & just to the left of the 
#string. We'll need that later. 
!0
  cmp ''
  brae !0_e
  cmp 'a'
  brae !0_*
  cmp 'b'
  brae !0_*
  cmp 'c'
  brae !0_*
  fail

!0_e
  halt

!0_*
  left 1
  draw '&'
  right 1







#Part 1: Traverse left to right deleting strings of consecutive chars.
#Leave the final char in the sequence alone.

!1
  cmp ''
  brae !1_e
  cmp 'a'
  brae !1_a
  cmp 'b'
  brae !1_b
  cmp 'c'
  brae !1_c
  fail

!1_a 
  erase    
  right 1               
  cmp 'a'               
  brane !1_a_*                         
  brae !1_a

!1_a_*
  left 1
  draw 'a'
  right 1
  bra !1


!1_b  
  erase
  right 1                               
  cmp 'b'               
  brane !1_b_*          
  brae !1_b
!1_b_*
  left 1
  draw 'b'
  right 1
  bra !1


!1_c   
  erase  
  right 1                             
  cmp 'c'               
  brane !1_c_*          
  brae !1_c
!1_c_*
  left 1
  draw 'c'
  right 1
  bra !1


!1_e
  left 1
  

#Part 2: traverse the string right, to left. 
#Move each [abc] to the left of the '&'

!2
  cmp ''
  brae !2_e
  cmp 'a'
  brae !2_a
  cmp 'b'
  brae !2_b
  cmp 'c'
  brae !2_c
  cmp '&'
  brae !2_&
  fail


!2_e 
  left 1
  bra !2


!2_a
  draw '-'
  left 1
!2_a_1
  cmp '&'
  brae !2_a_1_&
  left 1
  brane !2_a_1
!2_a_1_&
  left 1
!2_a_2
  cmp ''
  brae !2_a_2_e
  left 1
  brane !2_a_2
!2_a_2_e
  draw 'a'
  right 1
!2_a_3 
  cmp '-'
  brae !2_a_3_-
  right 1 
  brane !2_a_3
!2_a_3_-
  erase
  left 1
  bra !2


!2_b
  draw '-'
  left 1
!2_b_1
  cmp '&'
  brae !2_b_1_&
  left 1
  brane !2_b_1
!2_b_1_&
  left 1
!2_b_2
  cmp ''
  brae !2_b_2_e
  left 1
  brane !2_b_2
!2_b_2_e
  draw 'b'
  right 1
!2_b_3 
  cmp '-'
  brae !2_b_3_-
  right 1 
  brane !2_b_3
!2_b_3_-
  erase
  left 1
  bra !2


!2_c
  draw '-'
  left 1
!2_c_1
  cmp '&'
  brae !2_c_1_&
  left 1
  brane !2_c_1
!2_c_1_&
  left 1
!2_c_2
  cmp ''
  brae !2_c_2_e
  left 1
  brane !2_c_2
!2_c_2_e
  draw 'c'
  right 1
!2_c_3 
  cmp '-'
  brae !2_c_3_-
  right 1 
  brane !2_c_3
!2_c_3_-
  erase
  left 1
  bra !2


!2_&
  erase
  left 1  




#Part 3: Reset the head
!3
  cmp ''
  brae !3_e
  left 1
  brane !3

!3_e
 right 1
 HALT
