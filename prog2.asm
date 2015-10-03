alpha "abAB"
bra !Q 
  	 	
	   
		

!1 
	cmp 'a' 
	brae !1_a
	cmp 'b'
	brae !1_b
	fail 
!1_a 
	draw 'A'
	right 1
	brae !2 
	brane !2
!1_b
	DRAW 'B'  
	right 1
	bra !3
	brane !3
!2
	cmp 'a'
	brae !2_a
	cmp 'B'
	brae !2_b
	brane !2_[^aB]
!2_a
	draw 'B'
	left 1
	halt
!2_b
	draw 'a'
	right 1
	brae !1
	brane !1
!2_[^aB]
	draw 'a'
	left 1
	brae !3
	brane !3
!3  
	cmp 'a'
