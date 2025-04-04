# ! / b i n / b a s h 
 #   S c r i p t   f o r   t r a i n i n g   v o i c e   m o d e l s   f o r   t h e   A I   C a l l   S e c r e t a r y 
 
 #   D e f a u l t   v a l u e s 
 V O I C E _ N A M E = " " 
 S A M P L E S _ D I R = " " 
 C O N F I G _ F I L E = " . . / c o n f i g / d e f a u l t . y m l " 
 M E T A D A T A _ F I L E = " " 
 P Y T H O N _ S C R I P T = " . . / s r c / v o i c e / t r a i n _ v o i c e . p y " 
 F O R C E = f a l s e 
 
 #   H e l p   f u n c t i o n 
 s h o w _ h e l p ( )   { 
         e c h o   " U s a g e :   $ 0   [ o p t i o n s ] " 
         e c h o   " T r a i n   a   c u s t o m   v o i c e   m o d e l   f o r   t h e   A I   C a l l   S e c r e t a r y " 
         e c h o   " " 
         e c h o   " O p t i o n s : " 
         e c h o   "     - n ,   - - n a m e   N A M E                 N a m e   f o r   t h e   v o i c e   m o d e l   ( r e q u i r e d ) " 
         e c h o   "     - s ,   - - s a m p l e s   D I R             D i r e c t o r y   c o n t a i n i n g   a u d i o   s a m p l e s   ( r e q u i r e d ) " 
         e c h o   "     - c ,   - - c o n f i g   F I L E             P a t h   t o   c o n f i g   f i l e   ( d e f a u l t :   . . / c o n f i g / d e f a u l t . y m l ) " 
         e c h o   "     - m ,   - - m e t a d a t a   F I L E         P a t h   t o   J S O N   m e t a d a t a   f i l e " 
         e c h o   "     - f ,   - - f o r c e                         O v e r w r i t e   i f   v o i c e   a l r e a d y   e x i s t s " 
         e c h o   "     - h ,   - - h e l p                           S h o w   t h i s   h e l p   m e s s a g e " 
         e c h o   " " 
         e c h o   " E x a m p l e : " 
         e c h o   "     $ 0   - - n a m e   b u s i n e s s _ v o i c e   - - s a m p l e s   . / r e c o r d i n g s /   - - m e t a d a t a   . / m e t a d a t a . j s o n " 
 } 
 
 #   P a r s e   a r g u m e n t s 
 w h i l e   [ [   $ #   - g t   0   ] ] ;   d o 
         k e y = " $ 1 " 
         c a s e   $ k e y   i n 
                 - n | - - n a m e ) 
                         V O I C E _ N A M E = " $ 2 " 
                         s h i f t   2 
                         ; ; 
                 - s | - - s a m p l e s ) 
                         S A M P L E S _ D I R = " $ 2 " 
                         s h i f t   2 
                         ; ; 
                 - c | - - c o n f i g ) 
                         C O N F I G _ F I L E = " $ 2 " 
                         s h i f t   2 
                         ; ; 
                 - m | - - m e t a d a t a ) 
                         M E T A D A T A _ F I L E = " $ 2 " 
                         s h i f t   2 
                         ; ; 
                 - f | - - f o r c e ) 
                         F O R C E = t r u e 
                         s h i f t 
                         ; ; 
                 - h | - - h e l p ) 
                         s h o w _ h e l p 
                         e x i t   0 
                         ; ; 
                 * ) 
                         e c h o   " U n k n o w n   o p t i o n :   $ 1 " 
                         s h o w _ h e l p 
                         e x i t   1 
                         ; ; 
         e s a c 
 d o n e 
 
 #   C h e c k   r e q u i r e d   a r g u m e n t s 
 i f   [   - z   " $ V O I C E _ N A M E "   ] ;   t h e n 
         e c h o   " E r r o r :   V o i c e   n a m e   i s   r e q u i r e d " 
         s h o w _ h e l p 
         e x i t   1 
 f i 
 
 i f   [   - z   " $ S A M P L E S _ D I R "   ] ;   t h e n 
         e c h o   " E r r o r :   S a m p l e s   d i r e c t o r y   i s   r e q u i r e d " 
         s h o w _ h e l p 
         e x i t   1 
 f i 
 
 #   V a l i d a t e   s a m p l e s   d i r e c t o r y 
 i f   [   !   - d   " $ S A M P L E S _ D I R "   ] ;   t h e n 
         e c h o   " E r r o r :   S a m p l e s   d i r e c t o r y   d o e s   n o t   e x i s t :   $ S A M P L E S _ D I R " 
         e x i t   1 
 f i 
 
 #   C o u n t   a u d i o   s a m p l e s   ( W A V   a n d   M P 3   f i l e s ) 
 S A M P L E _ C O U N T = $ ( f i n d   " $ S A M P L E S _ D I R "   - t y p e   f   \ (   - n a m e   " * . w a v "   - o   - n a m e   " * . m p 3 "   \ )   |   w c   - l ) 
 e c h o   " F o u n d   $ S A M P L E _ C O U N T   a u d i o   s a m p l e s   i n   $ S A M P L E S _ D I R " 
 
 #   C h e c k   i f   w e   h a v e   e n o u g h   s a m p l e s   ( m i n i m u m   5 ) 
 i f   [   " $ S A M P L E _ C O U N T "   - l t   5   ] ;   t h e n 
         e c h o   " E r r o r :   N o t   e n o u g h   a u d i o   s a m p l e s .   N e e d   a t   l e a s t   5 ,   f o u n d   $ S A M P L E _ C O U N T " 
         e x i t   1 
 f i 
 
 #   C r e a t e   P y t h o n   s c r i p t   t o   t r a i n   t h e   v o i c e 
 c a t   >   " $ P Y T H O N _ S C R I P T "   < < E O F 
 " " " 
 V o i c e   t r a i n i n g   s c r i p t . 
 " " " 
 i m p o r t   o s 
 i m p o r t   s y s 
 i m p o r t   j s o n 
 i m p o r t   l o g g i n g 
 f r o m   s r c . v o i c e . v o i c e _ c l o n e   i m p o r t   V o i c e C l o n e r 
 
 #   S e t u p   l o g g i n g 
 l o g g i n g . b a s i c C o n f i g ( 
         l e v e l = l o g g i n g . I N F O , 
         f o r m a t = ' % ( a s c t i m e ) s   -   % ( n a m e ) s   -   % ( l e v e l n a m e ) s   -   % ( m e s s a g e ) s ' 
 ) 
 l o g g e r   =   l o g g i n g . g e t L o g g e r ( " v o i c e _ t r a i n e r " ) 
 
 d e f   m a i n ( ) : 
         #   P a r s e   a r g u m e n t s   f r o m   e n v i r o n m e n t 
         v o i c e _ n a m e   =   o s . e n v i r o n . g e t ( " V O I C E _ N A M E " ) 
         s a m p l e s _ d i r   =   o s . e n v i r o n . g e t ( " S A M P L E S _ D I R " ) 
         c o n f i g _ f i l e   =   o s . e n v i r o n . g e t ( " C O N F I G _ F I L E " ) 
         m e t a d a t a _ f i l e   =   o s . e n v i r o n . g e t ( " M E T A D A T A _ F I L E " ) 
         f o r c e   =   o s . e n v i r o n . g e t ( " F O R C E " ,   " f a l s e " ) . l o w e r ( )   = =   " t r u e " 
         
         #   V a l i d a t e   a r g u m e n t s 
         i f   n o t   v o i c e _ n a m e : 
                 l o g g e r . e r r o r ( " V o i c e   n a m e   n o t   p r o v i d e d " ) 
                 r e t u r n   1 
         
         i f   n o t   s a m p l e s _ d i r   o r   n o t   o s . p a t h . i s d i r ( s a m p l e s _ d i r ) : 
                 l o g g e r . e r r o r ( f " S a m p l e s   d i r e c t o r y   i n v a l i d :   { s a m p l e s _ d i r } " ) 
                 r e t u r n   1 
         
         #   F i n d   a u d i o   s a m p l e s 
         a u d i o _ s a m p l e s   =   [ ] 
         f o r   r o o t ,   _ ,   f i l e s   i n   o s . w a l k ( s a m p l e s _ d i r ) : 
                 f o r   f i l e   i n   f i l e s : 
                         i f   f i l e . l o w e r ( ) . e n d s w i t h ( ( ' . w a v ' ,   ' . m p 3 ' ) ) : 
                                 a u d i o _ s a m p l e s . a p p e n d ( o s . p a t h . j o i n ( r o o t ,   f i l e ) ) 
         
         i f   l e n ( a u d i o _ s a m p l e s )   <   5 : 
                 l o g g e r . e r r o r ( f " N o t   e n o u g h   a u d i o   s a m p l e s .   N e e d   a t   l e a s t   5 ,   f o u n d   { l e n ( a u d i o _ s a m p l e s ) } " ) 
                 r e t u r n   1 
         
         l o g g e r . i n f o ( f " F o u n d   { l e n ( a u d i o _ s a m p l e s ) }   a u d i o   s a m p l e s " ) 
         
         #   L o a d   m e t a d a t a   i f   p r o v i d e d 
         m e t a d a t a   =   N o n e 
         i f   m e t a d a t a _ f i l e   a n d   o s . p a t h . i s f i l e ( m e t a d a t a _ f i l e ) : 
                 t r y : 
                         w i t h   o p e n ( m e t a d a t a _ f i l e ,   ' r ' )   a s   f : 
                                 m e t a d a t a   =   j s o n . l o a d ( f ) 
                         l o g g e r . i n f o ( f " L o a d e d   m e t a d a t a   f r o m   { m e t a d a t a _ f i l e } " ) 
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   l o a d i n g   m e t a d a t a :   { s t r ( e ) } " ) 
                         r e t u r n   1 
         
         #   I n i t i a l i z e   v o i c e   c l o n e r 
         v o i c e _ c l o n e r   =   V o i c e C l o n e r ( c o n f i g _ f i l e ) 
         
         #   C h e c k   i f   v o i c e   e x i s t s   a n d   f o r c e   f l a g 
         v o i c e s   =   v o i c e _ c l o n e r . l i s t _ v o i c e s ( ) 
         i f   v o i c e _ n a m e   i n   v o i c e s : 
                 i f   n o t   f o r c e : 
                         l o g g e r . e r r o r ( f " V o i c e   ' { v o i c e _ n a m e } '   a l r e a d y   e x i s t s .   U s e   - - f o r c e   t o   o v e r w r i t e " ) 
                         r e t u r n   1 
                 
                 #   D e l e t e   e x i s t i n g   v o i c e   i f   f o r c e   i s   t r u e 
                 s u c c e s s ,   m e s s a g e   =   v o i c e _ c l o n e r . d e l e t e _ v o i c e ( v o i c e _ n a m e ) 
                 i f   n o t   s u c c e s s : 
                         l o g g e r . e r r o r ( f " F a i l e d   t o   d e l e t e   e x i s t i n g   v o i c e :   { m e s s a g e } " ) 
                         r e t u r n   1 
         
         #   C r e a t e   t h e   v o i c e 
         l o g g e r . i n f o ( f " C r e a t i n g   v o i c e   ' { v o i c e _ n a m e } '   w i t h   { l e n ( a u d i o _ s a m p l e s ) }   s a m p l e s " ) 
         s u c c e s s ,   m e s s a g e   =   v o i c e _ c l o n e r . c r e a t e _ v o i c e ( v o i c e _ n a m e ,   a u d i o _ s a m p l e s ,   m e t a d a t a ) 
         
         i f   s u c c e s s : 
                 l o g g e r . i n f o ( f " V o i c e   c r e a t i o n   s u c c e s s f u l :   { m e s s a g e } " ) 
                 r e t u r n   0 
         e l s e : 
                 l o g g e r . e r r o r ( f " V o i c e   c r e a t i o n   f a i l e d :   { m e s s a g e } " ) 
                 r e t u r n   1 
 
 i f   _ _ n a m e _ _   = =   " _ _ m a i n _ _ " : 
         s y s . e x i t ( m a i n ( ) ) 
 E O F 
 
 #   C r e a t e   m e t a d a t a   f i l e   i f   n o t   p r o v i d e d 
 i f   [   - z   " $ M E T A D A T A _ F I L E "   ]   & &   [   " $ F O R C E "   =   t r u e   ] ;   t h e n 
         M E T A D A T A _ F I L E = " . . / d a t a / t e m p / m e t a d a t a _ $ V O I C E _ N A M E . j s o n " 
         e c h o   " { \ " n a m e \ " :   \ " $ V O I C E _ N A M E \ " ,   \ " d e s c r i p t i o n \ " :   \ " A u t o - g e n e r a t e d   v o i c e   m o d e l \ " } "   >   " $ M E T A D A T A _ F I L E " 
 f i 
 
 #   R u n   t h e   P y t h o n   s c r i p t 
 e c h o   " S t a r t i n g   v o i c e   t r a i n i n g   f o r   $ V O I C E _ N A M E . . . " 
 e x p o r t   V O I C E _ N A M E = " $ V O I C E _ N A M E " 
 e x p o r t   S A M P L E S _ D I R = " $ S A M P L E S _ D I R " 
 e x p o r t   C O N F I G _ F I L E = " $ C O N F I G _ F I L E " 
 e x p o r t   M E T A D A T A _ F I L E = " $ M E T A D A T A _ F I L E " 
 e x p o r t   F O R C E = " $ F O R C E " 
 
 #   C h a n g e   t o   t h e   p r o j e c t   r o o t   d i r e c t o r y 
 S C R I P T _ D I R = " $ ( c d   " $ ( d i r n a m e   " $ { B A S H _ S O U R C E [ 0 ] } " ) "   & &   p w d ) " 
 c d   " $ S C R I P T _ D I R / . . "   | |   e x i t   1 
 
 #   R u n   t h e   P y t h o n   s c r i p t 
 p y t h o n 3   - m   s r c . v o i c e . t r a i n _ v o i c e 
 
 #   C h e c k   e x i t   s t a t u s 
 i f   [   $ ?   - e q   0   ] ;   t h e n 
         e c h o   " V o i c e   t r a i n i n g   c o m p l e t e d   s u c c e s s f u l l y ! " 
         e x i t   0 
 e l s e 
         e c h o   " V o i c e   t r a i n i n g   f a i l e d . " 
         e x i t   1 
 f i 