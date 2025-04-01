" " " 
 T e s t s   f o r   t e l e p h o n y   f u n c t i o n a l i t y . 
 " " " 
 i m p o r t   o s 
 i m p o r t   u n i t t e s t 
 i m p o r t   t i m e 
 f r o m   u n i t t e s t . m o c k   i m p o r t   M a g i c M o c k ,   p a t c h 
 i m p o r t   y a m l 
 
 i m p o r t   s y s 
 s y s . p a t h . a p p e n d ( o s . p a t h . d i r n a m e ( o s . p a t h . d i r n a m e ( o s . p a t h . a b s p a t h ( _ _ f i l e _ _ ) ) ) ) 
 
 f r o m   s r c . t e l e p h o n y . c a l l _ r o u t e r   i m p o r t   C a l l R o u t e r 
 f r o m   s r c . t e l e p h o n y . c a l l _ h a n d l e r   i m p o r t   C a l l H a n d l e r 
 
 c l a s s   T e s t C a l l R o u t e r ( u n i t t e s t . T e s t C a s e ) : 
         " " " T e s t   c a s e s   f o r   t h e   C a l l R o u t e r   c l a s s . " " " 
         
         d e f   s e t U p ( s e l f ) : 
                 " " " S e t   u p   t e s t   f i x t u r e s . " " " 
                 #   C r e a t e   a   t e m p o r a r y   c o n f i g   f i l e   f o r   t e s t i n g 
                 s e l f . t e s t _ c o n f i g   =   { 
                         ' t e l e p h o n y ' :   { 
                                 ' r o u t i n g _ r u l e s ' :   [ 
                                         { 
                                                 ' n a m e ' :   ' T e s t   R u l e ' , 
                                                 ' n u m b e r _ p a t t e r n ' :   ' ^ 1 5 5 5 1 2 3 . * $ ' , 
                                                 ' a c t i o n ' :   ' t e s t _ a c t i o n ' , 
                                                 ' p a r a m s ' :   { ' t e s t ' :   ' v a l u e ' } 
                                         } 
                                 ] , 
                                 ' b l a c k l i s t ' :   [ ' ^ 1 5 5 5 9 9 9 . * $ ' ] , 
                                 ' w h i t e l i s t ' :   [ ' ^ 1 5 5 5 1 1 1 . * $ ' ] , 
                                 ' b u s i n e s s _ h o u r s ' :   { 
                                         ' s t a r t ' :   ' 0 9 : 0 0 ' , 
                                         ' e n d ' :   ' 1 7 : 0 0 ' 
                                 } 
                         } 
                 } 
                 
                 #   M o c k   t h e   c o n f i g   l o a d i n g 
                 s e l f . c o n f i g _ p a t c h e r   =   p a t c h ( ' y a m l . s a f e _ l o a d ' ) 
                 s e l f . m o c k _ y a m l _ l o a d   =   s e l f . c o n f i g _ p a t c h e r . s t a r t ( ) 
                 s e l f . m o c k _ y a m l _ l o a d . r e t u r n _ v a l u e   =   s e l f . t e s t _ c o n f i g 
                 
                 #   C r e a t e   a   r o u t e r   i n s t a n c e   w i t h   m o c k e d   c o n f i g 
                 s e l f . r o u t e r   =   C a l l R o u t e r ( ) 
         
         d e f   t e a r D o w n ( s e l f ) : 
                 " " " T e a r   d o w n   t e s t   f i x t u r e s . " " " 
                 s e l f . c o n f i g _ p a t c h e r . s t o p ( ) 
         
         d e f   t e s t _ b l a c k l i s t e d _ n u m b e r ( s e l f ) : 
                 " " " T e s t   r o u t i n g   f o r   b l a c k l i s t e d   n u m b e r s . " " " 
                 c a l l _ m e t a d a t a   =   { 
                         ' c a l l e r _ n u m b e r ' :   ' 1 5 5 5 9 9 9 1 2 3 4 ' , 
                         ' c a l l e r _ n a m e ' :   ' T e s t   C a l l e r ' , 
                         ' t i m e s t a m p ' :   t i m e . t i m e ( ) 
                 } 
                 a c t i o n ,   p a r a m s   =   s e l f . r o u t e r . r o u t e _ c a l l ( c a l l _ m e t a d a t a ) 
                 s e l f . a s s e r t E q u a l ( a c t i o n ,   ' r e j e c t ' ) 
                 s e l f . a s s e r t E q u a l ( p a r a m s [ ' r e a s o n ' ] ,   ' b l a c k l i s t e d ' ) 
         
         d e f   t e s t _ w h i t e l i s t e d _ n u m b e r ( s e l f ) : 
                 " " " T e s t   r o u t i n g   f o r   w h i t e l i s t e d   n u m b e r s . " " " 
                 c a l l _ m e t a d a t a   =   { 
                         ' c a l l e r _ n u m b e r ' :   ' 1 5 5 5 1 1 1 9 8 7 6 ' , 
                         ' c a l l e r _ n a m e ' :   ' V I P   C a l l e r ' , 
                         ' t i m e s t a m p ' :   t i m e . t i m e ( ) 
                 } 
                 a c t i o n ,   p a r a m s   =   s e l f . r o u t e r . r o u t e _ c a l l ( c a l l _ m e t a d a t a ) 
                 s e l f . a s s e r t E q u a l ( a c t i o n ,   ' p r i o r i t y ' ) 
                 s e l f . a s s e r t E q u a l ( p a r a m s [ ' l e v e l ' ] ,   ' h i g h ' ) 
         
         d e f   t e s t _ r u l e _ m a t c h i n g ( s e l f ) : 
                 " " " T e s t   r u l e   m a t c h i n g   f u n c t i o n a l i t y . " " " 
                 c a l l _ m e t a d a t a   =   { 
                         ' c a l l e r _ n u m b e r ' :   ' 1 5 5 5 1 2 3 4 5 6 7 ' , 
                         ' c a l l e r _ n a m e ' :   ' R e g u l a r   C a l l e r ' , 
                         ' t i m e s t a m p ' :   t i m e . t i m e ( ) 
                 } 
                 a c t i o n ,   p a r a m s   =   s e l f . r o u t e r . r o u t e _ c a l l ( c a l l _ m e t a d a t a ) 
                 s e l f . a s s e r t E q u a l ( a c t i o n ,   ' t e s t _ a c t i o n ' ) 
                 s e l f . a s s e r t E q u a l ( p a r a m s [ ' t e s t ' ] ,   ' v a l u e ' ) 
         
         d e f   t e s t _ b u s i n e s s _ h o u r s ( s e l f ) : 
                 " " " T e s t   b u s i n e s s   h o u r s   f u n c t i o n a l i t y . " " " 
                 #   S e t   u p   a   m o c k   t i m e   t h a t ' s   w i t h i n   b u s i n e s s   h o u r s   ( 1 1   A M ) 
                 m o c k _ t i m e   =   t i m e . m k t i m e ( t i m e . s t r p t i m e ( " 2 0 2 3 - 0 1 - 0 1   1 1 : 0 0 : 0 0 " ,   " % Y - % m - % d   % H : % M : % S " ) ) 
                 
                 c a l l _ m e t a d a t a   =   { 
                         ' c a l l e r _ n u m b e r ' :   ' 1 2 2 2 3 3 3 4 4 4 4 ' ,     #   N u m b e r   t h a t   d o e s n ' t   m a t c h   a n y   s p e c i f i c   r u l e s 
                         ' c a l l e r _ n a m e ' :   ' T e s t   C a l l e r ' , 
                         ' t i m e s t a m p ' :   m o c k _ t i m e 
                 } 
                 
                 #   F i r s t ,   t e s t   w i t h i n   b u s i n e s s   h o u r s 
                 i s _ b u s i n e s s _ h o u r s   =   s e l f . r o u t e r . _ i s _ b u s i n e s s _ h o u r s ( m o c k _ t i m e ) 
                 s e l f . a s s e r t T r u e ( i s _ b u s i n e s s _ h o u r s ) 
                 
                 #   N o w   t e s t   o u t s i d e   b u s i n e s s   h o u r s   ( 3   A M ) 
                 m o c k _ t i m e _ o u t s i d e   =   t i m e . m k t i m e ( t i m e . s t r p t i m e ( " 2 0 2 3 - 0 1 - 0 1   0 3 : 0 0 : 0 0 " ,   " % Y - % m - % d   % H : % M : % S " ) ) 
                 i s _ o u t s i d e _ h o u r s   =   n o t   s e l f . r o u t e r . _ i s _ b u s i n e s s _ h o u r s ( m o c k _ t i m e _ o u t s i d e ) 
                 s e l f . a s s e r t T r u e ( i s _ o u t s i d e _ h o u r s ) 
 
 
 c l a s s   T e s t C a l l H a n d l e r ( u n i t t e s t . T e s t C a s e ) : 
         " " " T e s t   c a s e s   f o r   t h e   C a l l H a n d l e r   c l a s s . " " " 
         
         d e f   s e t U p ( s e l f ) : 
                 " " " S e t   u p   t e s t   f i x t u r e s . " " " 
                 #   C r e a t e   m o c k   c o m p o n e n t s 
                 s e l f . m o c k _ s t t   =   M a g i c M o c k ( ) 
                 s e l f . m o c k _ t t s   =   M a g i c M o c k ( ) 
                 s e l f . m o c k _ l l m   =   M a g i c M o c k ( ) 
                 s e l f . m o c k _ c o n t e x t   =   M a g i c M o c k ( ) 
                 s e l f . m o c k _ a c t i o n _ h a n d l e r   =   M a g i c M o c k ( ) 
                 
                 #   C r e a t e   a   t e s t   c a l l   m e t a d a t a 
                 s e l f . t e s t _ c a l l _ m e t a d a t a   =   { 
                         ' c a l l _ i d ' :   ' t e s t - c a l l - 1 2 3 ' , 
                         ' c a l l e r _ n u m b e r ' :   ' 1 5 5 5 1 2 3 4 5 6 7 ' , 
                         ' c a l l e r _ n a m e ' :   ' T e s t   C a l l e r ' , 
                         ' t i m e s t a m p ' :   t i m e . t i m e ( ) 
                 } 
                 
                 #   P a t c h   t h e   i m p o r t s 
                 s e l f . p a t c h e s   =   [ 
                         p a t c h ( ' s r c . t e l e p h o n y . c a l l _ h a n d l e r . S p e e c h T o T e x t ' ,   r e t u r n _ v a l u e = s e l f . m o c k _ s t t ) , 
                         p a t c h ( ' s r c . t e l e p h o n y . c a l l _ h a n d l e r . T e x t T o S p e e c h ' ,   r e t u r n _ v a l u e = s e l f . m o c k _ t t s ) , 
                         p a t c h ( ' s r c . t e l e p h o n y . c a l l _ h a n d l e r . O l l a m a C l i e n t ' ,   r e t u r n _ v a l u e = s e l f . m o c k _ l l m ) , 
                         p a t c h ( ' s r c . t e l e p h o n y . c a l l _ h a n d l e r . C o n v e r s a t i o n C o n t e x t ' ,   r e t u r n _ v a l u e = s e l f . m o c k _ c o n t e x t ) , 
                         p a t c h ( ' s r c . t e l e p h o n y . c a l l _ h a n d l e r . A c t i o n H a n d l e r ' ,   r e t u r n _ v a l u e = s e l f . m o c k _ a c t i o n _ h a n d l e r ) , 
                 ] 
                 
                 f o r   p   i n   s e l f . p a t c h e s : 
                         p . s t a r t ( ) 
                 
                 #   C r e a t e   h a n d l e r   i n s t a n c e 
                 s e l f . h a n d l e r   =   C a l l H a n d l e r ( s e l f . t e s t _ c a l l _ m e t a d a t a ) 
                 
                 #   M o c k   s e s s i o n 
                 s e l f . m o c k _ s e s s i o n   =   M a g i c M o c k ( ) 
         
         d e f   t e a r D o w n ( s e l f ) : 
                 " " " T e a r   d o w n   t e s t   f i x t u r e s . " " " 
                 f o r   p   i n   s e l f . p a t c h e s : 
                         p . s t o p ( ) 
         
         d e f   t e s t _ i n i t i a l i z a t i o n ( s e l f ) : 
                 " " " T e s t   h a n d l e r   i n i t i a l i z a t i o n . " " " 
                 s e l f . a s s e r t E q u a l ( s e l f . h a n d l e r . c a l l _ i d ,   s e l f . t e s t _ c a l l _ m e t a d a t a [ ' c a l l _ i d ' ] ) 
                 s e l f . a s s e r t E q u a l ( s e l f . h a n d l e r . c a l l e r _ n u m b e r ,   s e l f . t e s t _ c a l l _ m e t a d a t a [ ' c a l l e r _ n u m b e r ' ] ) 
                 s e l f . a s s e r t E q u a l ( s e l f . h a n d l e r . c a l l e r _ n a m e ,   s e l f . t e s t _ c a l l _ m e t a d a t a [ ' c a l l e r _ n a m e ' ] ) 
         
         d e f   t e s t _ s h o u l d _ e n d _ c a l l ( s e l f ) : 
                 " " " T e s t   d e t e c t i o n   o f   c a l l - e n d i n g   p h r a s e s . " " " 
                 e n d _ p h r a s e s   =   [ 
                         " g o o d b y e " ,   " b y e " ,   " h a n g   u p " ,   " e n d   c a l l " , 
                         " t h a n k   y o u   g o o d b y e " ,   " t h a t ' s   a l l " ,   " d i s c o n n e c t " 
                 ] 
                 
                 f o r   p h r a s e   i n   e n d _ p h r a s e s : 
                         s e l f . a s s e r t T r u e ( s e l f . h a n d l e r . _ s h o u l d _ e n d _ c a l l ( p h r a s e ) ,   f " F a i l e d   f o r   ' { p h r a s e } ' " ) 
                 
                 n o n _ e n d _ p h r a s e s   =   [ 
                         " h e l l o " ,   " y e s " ,   " n o " ,   " m a y b e " ,   " t e l l   m e   m o r e " , 
                         " w h a t   t i m e   i s   i t " ,   " c a n   y o u   h e l p   m e " 
                 ] 
                 
                 f o r   p h r a s e   i n   n o n _ e n d _ p h r a s e s : 
                         s e l f . a s s e r t F a l s e ( s e l f . h a n d l e r . _ s h o u l d _ e n d _ c a l l ( p h r a s e ) ,   f " F a i l e d   f o r   ' { p h r a s e } ' " ) 
         
         d e f   t e s t _ c o n v e r s a t i o n _ f l o w ( s e l f ) : 
                 " " " T e s t   t h e   b a s i c   c o n v e r s a t i o n   f l o w . " " " 
                 #   S e t u p   m o c k s 
                 s e l f . m o c k _ s t t . t r a n s c r i b e . r e t u r n _ v a l u e   =   " T h i s   i s   a   t e s t   m e s s a g e " 
                 s e l f . m o c k _ l l m . g e n e r a t e _ r e s p o n s e . r e t u r n _ v a l u e   =   " T h i s   i s   t h e   A I   r e s p o n s e " 
                 s e l f . m o c k _ a c t i o n _ h a n d l e r . e x t r a c t _ a c t i o n s . r e t u r n _ v a l u e   =   [ ] 
                 
                 #   C a l l   p r o c e s s _ c a l l   w i t h   p a t c h e d   _ c a p t u r e _ a u d i o   a n d   _ s h o u l d _ e n d _ c a l l 
                 w i t h   p a t c h . o b j e c t ( s e l f . h a n d l e r ,   ' _ c a p t u r e _ a u d i o ' )   a s   m o c k _ c a p t u r e : 
                         w i t h   p a t c h . o b j e c t ( s e l f . h a n d l e r ,   ' _ s h o u l d _ e n d _ c a l l ' )   a s   m o c k _ e n d : 
                                 #   F i r s t   a u d i o   c a p t u r e   r e t u r n s   m e s s a g e ,   s e c o n d   s i m u l a t e s   e n d   o f   c a l l 
                                 m o c k _ c a p t u r e . s i d e _ e f f e c t   =   [ b " A U D I O _ D A T A " ,   N o n e ] 
                                 m o c k _ e n d . r e t u r n _ v a l u e   =   F a l s e 
                                 
                                 s e l f . h a n d l e r . p r o c e s s _ c a l l ( s e l f . m o c k _ s e s s i o n ) 
                 
                 #   V e r i f y   t h e   c o n v e r s a t i o n   f l o w 
                 s e l f . m o c k _ c o n t e x t . i n i t _ c o n v e r s a t i o n . a s s e r t _ c a l l e d _ o n c e ( ) 
                 s e l f . m o c k _ s t t . t r a n s c r i b e . a s s e r t _ c a l l e d _ o n c e ( ) 
                 s e l f . m o c k _ c o n t e x t . a d d _ u s e r _ m e s s a g e . a s s e r t _ c a l l e d _ o n c e _ w i t h ( " T h i s   i s   a   t e s t   m e s s a g e " ) 
                 s e l f . m o c k _ l l m . g e n e r a t e _ r e s p o n s e . a s s e r t _ c a l l e d _ o n c e ( ) 
                 s e l f . m o c k _ c o n t e x t . a d d _ a s s i s t a n t _ m e s s a g e . a s s e r t _ c a l l e d _ o n c e _ w i t h ( " T h i s   i s   t h e   A I   r e s p o n s e " ) 
                 s e l f . m o c k _ a c t i o n _ h a n d l e r . e x t r a c t _ a c t i o n s . a s s e r t _ c a l l e d _ o n c e _ w i t h ( " T h i s   i s   t h e   A I   r e s p o n s e " ) 
                 
 
 i f   _ _ n a m e _ _   = =   ' _ _ m a i n _ _ ' : 
         u n i t t e s t . m a i n ( ) 