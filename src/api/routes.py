" " " 
 A P I   r o u t e s   f o r   t h e   A I   C a l l   S e c r e t a r y . 
 " " " 
 i m p o r t   o s 
 i m p o r t   t i m e 
 i m p o r t   l o g g i n g 
 i m p o r t   y a m l 
 f r o m   t y p i n g   i m p o r t   L i s t ,   D i c t ,   O p t i o n a l ,   A n y 
 f r o m   d a t e t i m e   i m p o r t   d a t e t i m e ,   t i m e d e l t a 
 f r o m   f a s t a p i   i m p o r t   F a s t A P I ,   D e p e n d s ,   H T T P E x c e p t i o n ,   H e a d e r ,   Q u e r y ,   W e b S o c k e t ,   s t a t u s 
 f r o m   f a s t a p i . m i d d l e w a r e . c o r s   i m p o r t   C O R S M i d d l e w a r e 
 f r o m   f a s t a p i . s e c u r i t y   i m p o r t   O A u t h 2 P a s s w o r d B e a r e r ,   O A u t h 2 P a s s w o r d R e q u e s t F o r m 
 i m p o r t   j w t 
 f r o m   p y d a n t i c   i m p o r t   B a s e M o d e l 
 
 f r o m   s r c . a p i . s c h e m a s   i m p o r t   ( 
         C a l l D e t a i l ,   C a l l S u m m a r y ,   C a l l L i s t R e s p o n s e ,   A c t i o n R e q u e s t ,   A c t i o n R e s u l t , 
         A p p o i n t m e n t R e q u e s t ,   M e s s a g e R e q u e s t ,   C a l l F i l t e r P a r a m s ,   S y s t e m S t a t u s , 
         T o k e n R e s p o n s e ,   E r r o r R e s p o n s e ,   C a l l E v e n t ,   C a l l E v e n t T y p e 
 ) 
 f r o m   s r c . w o r k f l o w . a c t i o n s   i m p o r t   A c t i o n H a n d l e r 
 f r o m   s r c . l l m . c o n t e x t   i m p o r t   C o n v e r s a t i o n C o n t e x t 
 f r o m   s r c . t e l e p h o n y . c a l l _ h a n d l e r   i m p o r t   C a l l H a n d l e r 
 f r o m   s r c . w o r k f l o w . f l o w s . f l o w _ m a n a g e r   i m p o r t   F l o w M a n a g e r 
 
 #   I n i t i a l i z e   l o g g i n g 
 l o g g e r   =   l o g g i n g . g e t L o g g e r ( _ _ n a m e _ _ ) 
 
 #   L o a d   c o n f i g u r a t i o n 
 c o n f i g _ p a t h   =   o s . e n v i r o n . g e t ( " C O N F I G _ P A T H " ,   " c o n f i g / d e f a u l t . y m l " ) 
 w i t h   o p e n ( c o n f i g _ p a t h ,   " r " )   a s   f : 
         c o n f i g   =   y a m l . s a f e _ l o a d ( f ) 
 
 #   I n i t i a l i z e   A P I 
 a p p   =   F a s t A P I ( 
         t i t l e = " A I   C a l l   S e c r e t a r y   A P I " , 
         d e s c r i p t i o n = " A P I   f o r   t h e   A I   C a l l   S e c r e t a r y   s y s t e m " , 
         v e r s i o n = " 1 . 0 . 0 " 
 ) 
 
 #   C O R S   m i d d l e w a r e 
 a p p . a d d _ m i d d l e w a r e ( 
         C O R S M i d d l e w a r e , 
         a l l o w _ o r i g i n s = c o n f i g [ " a p i " ] [ " c o r s _ o r i g i n s " ] , 
         a l l o w _ c r e d e n t i a l s = T r u e , 
         a l l o w _ m e t h o d s = [ " * " ] , 
         a l l o w _ h e a d e r s = [ " * " ] , 
 ) 
 
 #   I n i t i a l i z e   c o m p o n e n t s 
 a c t i o n _ h a n d l e r   =   A c t i o n H a n d l e r ( c o n f i g _ p a t h ) 
 f l o w _ m a n a g e r   =   F l o w M a n a g e r ( c o n f i g _ p a t h ) 
 
 #   I n - m e m o r y   s t o r a g e   ( w o u l d   b e   r e p l a c e d   w i t h   d a t a b a s e   i n   p r o d u c t i o n ) 
 c a l l s _ d b   =   { }     #   c a l l _ i d   - >   C a l l D e t a i l 
 a c t i v e _ c a l l _ w e b s o c k e t s   =   { }     #   c a l l _ i d   - >   W e b S o c k e t 
 
 #   A u t h e n t i c a t i o n 
 o a u t h 2 _ s c h e m e   =   O A u t h 2 P a s s w o r d B e a r e r ( t o k e n U r l = " t o k e n " ) 
 J W T _ S E C R E T   =   c o n f i g [ " a p i " ] . g e t ( " j w t _ s e c r e t " ,   " s u p e r s e c r e t " ) 
 J W T _ A L G O R I T H M   =   " H S 2 5 6 " 
 J W T _ E X P I R A T I O N   =   c o n f i g [ " a p i " ] . g e t ( " t o k e n _ e x p i r y " ,   8 6 4 0 0 )     #   2 4   h o u r s 
 
 #   M o c k   u s e r s   ( w o u l d   b e   i n   d a t a b a s e   i n   p r o d u c t i o n ) 
 u s e r s _ d b   =   { 
         " a d m i n " :   { 
                 " u s e r n a m e " :   " a d m i n " , 
                 " h a s h e d _ p a s s w o r d " :   " p a s s w o r d " ,     #   I n   p r o d u c t i o n ,   t h i s   w o u l d   b e   h a s h e d 
                 " d i s a b l e d " :   F a l s e , 
         } 
 } 
 
 
 d e f   g e t _ c u r r e n t _ u s e r ( t o k e n :   s t r   =   D e p e n d s ( o a u t h 2 _ s c h e m e ) ) : 
         t r y : 
                 p a y l o a d   =   j w t . d e c o d e ( t o k e n ,   J W T _ S E C R E T ,   a l g o r i t h m s = [ J W T _ A L G O R I T H M ] ) 
                 u s e r n a m e   =   p a y l o a d . g e t ( " s u b " ) 
                 i f   u s e r n a m e   i s   N o n e : 
                         r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 1 ,   d e t a i l = " I n v a l i d   t o k e n " ) 
         e x c e p t   j w t . P y J W T E r r o r : 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 1 ,   d e t a i l = " I n v a l i d   t o k e n " ) 
         
         u s e r   =   u s e r s _ d b . g e t ( u s e r n a m e ) 
         i f   u s e r   i s   N o n e : 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 1 ,   d e t a i l = " U s e r   n o t   f o u n d " ) 
         
         i f   u s e r [ " d i s a b l e d " ] : 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 1 ,   d e t a i l = " U s e r   i s   d i s a b l e d " ) 
         
         r e t u r n   u s e r 
 
 
 #   A u t h   r o u t e s 
 @ a p p . p o s t ( " / t o k e n " ,   r e s p o n s e _ m o d e l = T o k e n R e s p o n s e ) 
 a s y n c   d e f   l o g i n ( f o r m _ d a t a :   O A u t h 2 P a s s w o r d R e q u e s t F o r m   =   D e p e n d s ( ) ) : 
         u s e r   =   u s e r s _ d b . g e t ( f o r m _ d a t a . u s e r n a m e ) 
         i f   n o t   u s e r : 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 1 ,   d e t a i l = " I n v a l i d   u s e r n a m e   o r   p a s s w o r d " ) 
         
         #   I n   p r o d u c t i o n ,   w o u l d   u s e   a   p a s s w o r d   h a s h i n g   l i b r a r y 
         i f   f o r m _ d a t a . p a s s w o r d   ! =   u s e r [ " h a s h e d _ p a s s w o r d " ] : 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 1 ,   d e t a i l = " I n v a l i d   u s e r n a m e   o r   p a s s w o r d " ) 
         
         #   C r e a t e   J W T   t o k e n 
         e x p i r a t i o n   =   d a t e t i m e . u t c n o w ( )   +   t i m e d e l t a ( s e c o n d s = J W T _ E X P I R A T I O N ) 
         t o k e n _ d a t a   =   { 
                 " s u b " :   u s e r [ " u s e r n a m e " ] , 
                 " e x p " :   e x p i r a t i o n 
         } 
         
         t o k e n   =   j w t . e n c o d e ( t o k e n _ d a t a ,   J W T _ S E C R E T ,   a l g o r i t h m = J W T _ A L G O R I T H M ) 
         
         r e t u r n   { 
                 " a c c e s s _ t o k e n " :   t o k e n , 
                 " t o k e n _ t y p e " :   " b e a r e r " , 
                 " e x p i r e s _ i n " :   J W T _ E X P I R A T I O N 
         } 
 
 
 #   S y s t e m   r o u t e s 
 @ a p p . g e t ( " / " ,   r e s p o n s e _ m o d e l = D i c t [ s t r ,   s t r ] ) 
 a s y n c   d e f   r o o t ( ) : 
         r e t u r n   { " m e s s a g e " :   " W e l c o m e   t o   t h e   A I   C a l l   S e c r e t a r y   A P I " } 
 
 
 @ a p p . g e t ( " / s t a t u s " ,   r e s p o n s e _ m o d e l = S y s t e m S t a t u s ) 
 a s y n c   d e f   s y s t e m _ s t a t u s ( c u r r e n t _ u s e r :   d i c t   =   D e p e n d s ( g e t _ c u r r e n t _ u s e r ) ) : 
         #   C a l c u l a t e   u p t i m e 
         s t a r t _ t i m e   =   g e t a t t r ( a p p ,   " s t a r t _ t i m e " ,   t i m e . t i m e ( ) ) 
         u p t i m e   =   i n t ( t i m e . t i m e ( )   -   s t a r t _ t i m e ) 
         
         #   C o u n t   a c t i v e   c a l l s 
         a c t i v e _ c a l l s   =   s u m ( 1   f o r   c a l l   i n   c a l l s _ d b . v a l u e s ( )   i f   c a l l . s t a t u s   = =   " a c t i v e " ) 
         
         #   C o u n t   c a l l s   f r o m   t o d a y 
         t o d a y   =   d a t e t i m e . n o w ( ) . d a t e ( ) 
         c a l l s _ t o d a y   =   s u m ( 1   f o r   c a l l   i n   c a l l s _ d b . v a l u e s ( )   
                                           i f   c a l l . s t a r t _ t i m e . d a t e ( )   = =   t o d a y ) 
         
         r e t u r n   { 
                 " s t a t u s " :   " o p e r a t i o n a l " , 
                 " v e r s i o n " :   a p p . v e r s i o n , 
                 " u p t i m e " :   u p t i m e , 
                 " a c t i v e _ c a l l s " :   a c t i v e _ c a l l s , 
                 " t o t a l _ c a l l s _ t o d a y " :   c a l l s _ t o d a y , 
                 " c o m p o n e n t s " :   { 
                         " a p i " :   " o p e r a t i o n a l " , 
                         " t e l e p h o n y " :   " o p e r a t i o n a l " , 
                         " l l m " :   " o p e r a t i o n a l " , 
                         " v o i c e " :   " o p e r a t i o n a l " , 
                         " w o r k f l o w " :   " o p e r a t i o n a l " 
                 } 
         } 
 
 
 #   C a l l   r o u t e s 
 @ a p p . g e t ( " / c a l l s " ,   r e s p o n s e _ m o d e l = C a l l L i s t R e s p o n s e ) 
 a s y n c   d e f   l i s t _ c a l l s ( 
         f i l t e r s :   C a l l F i l t e r P a r a m s   =   D e p e n d s ( ) , 
         c u r r e n t _ u s e r :   d i c t   =   D e p e n d s ( g e t _ c u r r e n t _ u s e r ) 
 ) : 
         #   F i l t e r   c a l l s   b a s e d   o n   c r i t e r i a 
         f i l t e r e d _ c a l l s   =   [ ] 
         f o r   c a l l   i n   c a l l s _ d b . v a l u e s ( ) : 
                 #   A p p l y   f i l t e r s 
                 i f   f i l t e r s . s t a r t _ d a t e   a n d   c a l l . s t a r t _ t i m e   <   f i l t e r s . s t a r t _ d a t e : 
                         c o n t i n u e 
                 i f   f i l t e r s . e n d _ d a t e   a n d   c a l l . s t a r t _ t i m e   >   f i l t e r s . e n d _ d a t e : 
                         c o n t i n u e 
                 i f   f i l t e r s . s t a t u s   a n d   c a l l . s t a t u s   ! =   f i l t e r s . s t a t u s : 
                         c o n t i n u e 
                 i f   f i l t e r s . c a l l e r _ n u m b e r   a n d   c a l l . c a l l e r _ n u m b e r   ! =   f i l t e r s . c a l l e r _ n u m b e r : 
                         c o n t i n u e 
                 
                 f i l t e r e d _ c a l l s . a p p e n d ( c a l l ) 
         
         #   S o r t   b y   s t a r t   t i m e   ( n e w e s t   f i r s t ) 
         f i l t e r e d _ c a l l s . s o r t ( k e y = l a m b d a   x :   x . s t a r t _ t i m e ,   r e v e r s e = T r u e ) 
         
         #   P a g i n a t e 
         t o t a l   =   l e n ( f i l t e r e d _ c a l l s ) 
         s t a r t _ i d x   =   ( f i l t e r s . p a g e   -   1 )   *   f i l t e r s . p a g e _ s i z e 
         e n d _ i d x   =   s t a r t _ i d x   +   f i l t e r s . p a g e _ s i z e 
         p a g i n a t e d _ c a l l s   =   f i l t e r e d _ c a l l s [ s t a r t _ i d x : e n d _ i d x ] 
         
         #   C o n v e r t   t o   s u m m a r i e s 
         c a l l _ s u m m a r i e s   =   [ ] 
         f o r   c a l l   i n   p a g i n a t e d _ c a l l s : 
                 s u m m a r y   =   C a l l S u m m a r y ( 
                         c a l l _ i d = c a l l . c a l l _ i d , 
                         c a l l e r _ n u m b e r = c a l l . c a l l e r _ n u m b e r , 
                         c a l l e r _ n a m e = c a l l . c a l l e r _ n a m e , 
                         s t a r t _ t i m e = c a l l . s t a r t _ t i m e , 
                         e n d _ t i m e = c a l l . e n d _ t i m e , 
                         d u r a t i o n = c a l l . d u r a t i o n , 
                         s t a t u s = c a l l . s t a t u s , 
                         s u m m a r y = c a l l . m e t a d a t a . g e t ( " s u m m a r y " )   i f   c a l l . m e t a d a t a   e l s e   N o n e 
                 ) 
                 c a l l _ s u m m a r i e s . a p p e n d ( s u m m a r y ) 
         
         r e t u r n   { 
                 " c a l l s " :   c a l l _ s u m m a r i e s , 
                 " t o t a l " :   t o t a l , 
                 " p a g e " :   f i l t e r s . p a g e , 
                 " p a g e _ s i z e " :   f i l t e r s . p a g e _ s i z e 
         } 
 
 
 @ a p p . g e t ( " / c a l l s / { c a l l _ i d } " ,   r e s p o n s e _ m o d e l = C a l l D e t a i l ) 
 a s y n c   d e f   g e t _ c a l l ( c a l l _ i d :   s t r ,   c u r r e n t _ u s e r :   d i c t   =   D e p e n d s ( g e t _ c u r r e n t _ u s e r ) ) : 
         i f   c a l l _ i d   n o t   i n   c a l l s _ d b : 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 4 ,   d e t a i l = " C a l l   n o t   f o u n d " ) 
         
         r e t u r n   c a l l s _ d b [ c a l l _ i d ] 
 
 
 @ a p p . d e l e t e ( " / c a l l s / { c a l l _ i d } " ,   s t a t u s _ c o d e = 2 0 4 ) 
 a s y n c   d e f   d e l e t e _ c a l l ( c a l l _ i d :   s t r ,   c u r r e n t _ u s e r :   d i c t   =   D e p e n d s ( g e t _ c u r r e n t _ u s e r ) ) : 
         i f   c a l l _ i d   n o t   i n   c a l l s _ d b : 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 4 ,   d e t a i l = " C a l l   n o t   f o u n d " ) 
         
         d e l   c a l l s _ d b [ c a l l _ i d ] 
         r e t u r n   N o n e 
 
 
 #   A c t i o n   r o u t e s 
 @ a p p . p o s t ( " / a c t i o n s " ,   r e s p o n s e _ m o d e l = A c t i o n R e s u l t ) 
 a s y n c   d e f   e x e c u t e _ a c t i o n ( 
         a c t i o n :   A c t i o n R e q u e s t , 
         c u r r e n t _ u s e r :   d i c t   =   D e p e n d s ( g e t _ c u r r e n t _ u s e r ) 
 ) : 
         t r y : 
                 #   C o n v e r t   t o   t h e   f o r m a t   e x p e c t e d   b y   t h e   a c t i o n   h a n d l e r 
                 a c t i o n _ i n p u t   =   { 
                         " t y p e " :   a c t i o n . a c t i o n _ t y p e . v a l u e , 
                         " p a r a m s " :   a c t i o n . p a r a m s 
                 } 
                 
                 #   E x e c u t e   t h e   a c t i o n 
                 r e s u l t   =   a c t i o n _ h a n d l e r . e x e c u t e _ a c t i o n ( a c t i o n _ i n p u t ) 
                 
                 #   C o n v e r t   r e s u l t   t o   A c t i o n R e s u l t 
                 a c t i o n _ r e s u l t   =   A c t i o n R e s u l t ( 
                         a c t i o n _ t y p e = a c t i o n . a c t i o n _ t y p e , 
                         s u c c e s s = r e s u l t . g e t ( " s u c c e s s " ,   F a l s e ) , 
                         t i m e s t a m p = d a t e t i m e . n o w ( ) , 
                         d e t a i l s = r e s u l t . g e t ( " d e t a i l s " ) , 
                         e r r o r = r e s u l t . g e t ( " e r r o r " ) 
                 ) 
                 
                 r e t u r n   a c t i o n _ r e s u l t 
         e x c e p t   E x c e p t i o n   a s   e : 
                 l o g g e r . e r r o r ( f " E r r o r   e x e c u t i n g   a c t i o n :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 5 0 0 ,   d e t a i l = f " E r r o r   e x e c u t i n g   a c t i o n :   { s t r ( e ) } " ) 
 
 
 @ a p p . p o s t ( " / a p p o i n t m e n t s " ,   r e s p o n s e _ m o d e l = A c t i o n R e s u l t ) 
 a s y n c   d e f   c r e a t e _ a p p o i n t m e n t ( 
         a p p o i n t m e n t :   A p p o i n t m e n t R e q u e s t , 
         c u r r e n t _ u s e r :   d i c t   =   D e p e n d s ( g e t _ c u r r e n t _ u s e r ) 
 ) : 
         t r y : 
                 #   C o n v e r t   t o   a c t i o n   r e q u e s t 
                 a c t i o n _ i n p u t   =   { 
                         " t y p e " :   " s c h e d u l e _ a p p o i n t m e n t " , 
                         " p a r a m s " :   a p p o i n t m e n t . d i c t ( ) 
                 } 
                 
                 #   E x e c u t e   t h e   a c t i o n 
                 r e s u l t   =   a c t i o n _ h a n d l e r . e x e c u t e _ a c t i o n ( a c t i o n _ i n p u t ) 
                 
                 #   C o n v e r t   r e s u l t   t o   A c t i o n R e s u l t 
                 a c t i o n _ r e s u l t   =   A c t i o n R e s u l t ( 
                         a c t i o n _ t y p e = " s c h e d u l e _ a p p o i n t m e n t " , 
                         s u c c e s s = r e s u l t . g e t ( " s u c c e s s " ,   F a l s e ) , 
                         t i m e s t a m p = d a t e t i m e . n o w ( ) , 
                         d e t a i l s = r e s u l t . g e t ( " d e t a i l s " ) , 
                         e r r o r = r e s u l t . g e t ( " e r r o r " ) 
                 ) 
                 
                 r e t u r n   a c t i o n _ r e s u l t 
         e x c e p t   E x c e p t i o n   a s   e : 
                 l o g g e r . e r r o r ( f " E r r o r   c r e a t i n g   a p p o i n t m e n t :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 5 0 0 ,   d e t a i l = f " E r r o r   c r e a t i n g   a p p o i n t m e n t :   { s t r ( e ) } " ) 
 
 
 @ a p p . p o s t ( " / m e s s a g e s " ,   r e s p o n s e _ m o d e l = A c t i o n R e s u l t ) 
 a s y n c   d e f   c r e a t e _ m e s s a g e ( 
         m e s s a g e :   M e s s a g e R e q u e s t , 
         c u r r e n t _ u s e r :   d i c t   =   D e p e n d s ( g e t _ c u r r e n t _ u s e r ) 
 ) : 
         t r y : 
                 #   C o n v e r t   t o   a c t i o n   r e q u e s t 
                 a c t i o n _ i n p u t   =   { 
                         " t y p e " :   " t a k e _ m e s s a g e " , 
                         " p a r a m s " :   m e s s a g e . d i c t ( ) 
                 } 
                 
                 #   E x e c u t e   t h e   a c t i o n 
                 r e s u l t   =   a c t i o n _ h a n d l e r . e x e c u t e _ a c t i o n ( a c t i o n _ i n p u t ) 
                 
                 #   C o n v e r t   r e s u l t   t o   A c t i o n R e s u l t 
                 a c t i o n _ r e s u l t   =   A c t i o n R e s u l t ( 
                         a c t i o n _ t y p e = " t a k e _ m e s s a g e " , 
                         s u c c e s s = r e s u l t . g e t ( " s u c c e s s " ,   F a l s e ) , 
                         t i m e s t a m p = d a t e t i m e . n o w ( ) , 
                         d e t a i l s = r e s u l t . g e t ( " d e t a i l s " ) , 
                         e r r o r = r e s u l t . g e t ( " e r r o r " ) 
                 ) 
                 
                 r e t u r n   a c t i o n _ r e s u l t 
         e x c e p t   E x c e p t i o n   a s   e : 
                 l o g g e r . e r r o r ( f " E r r o r   c r e a t i n g   m e s s a g e :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 5 0 0 ,   d e t a i l = f " E r r o r   c r e a t i n g   m e s s a g e :   { s t r ( e ) } " ) 
 
 
 #   W e b S o c k e t   f o r   r e a l - t i m e   c a l l   m o n i t o r i n g 
 @ a p p . w e b s o c k e t ( " / w s / c a l l s / { c a l l _ i d } " ) 
 a s y n c   d e f   w e b s o c k e t _ e n d p o i n t ( w e b s o c k e t :   W e b S o c k e t ,   c a l l _ i d :   s t r ) : 
         a w a i t   w e b s o c k e t . a c c e p t ( ) 
         
         #   S t o r e   t h e   w e b s o c k e t   c o n n e c t i o n 
         i f   c a l l _ i d   n o t   i n   a c t i v e _ c a l l _ w e b s o c k e t s : 
                 a c t i v e _ c a l l _ w e b s o c k e t s [ c a l l _ i d ]   =   [ ] 
         a c t i v e _ c a l l _ w e b s o c k e t s [ c a l l _ i d ] . a p p e n d ( w e b s o c k e t ) 
         
         t r y : 
                 #   S e n d   i n i t i a l   c a l l   d a t a   i f   a v a i l a b l e 
                 i f   c a l l _ i d   i n   c a l l s _ d b : 
                         c a l l _ d a t a   =   c a l l s _ d b [ c a l l _ i d ] . d i c t ( ) 
                         a w a i t   w e b s o c k e t . s e n d _ j s o n ( c a l l _ d a t a ) 
                 
                 #   K e e p   c o n n e c t i o n   o p e n ,   w i l l   b e   u p d a t e d   w h e n   c a l l   e v e n t s   o c c u r 
                 w h i l e   T r u e : 
                         #   J u s t   k e e p   t h e   c o n n e c t i o n   a l i v e 
                         a w a i t   w e b s o c k e t . r e c e i v e _ t e x t ( ) 
         e x c e p t   E x c e p t i o n   a s   e : 
                 l o g g e r . e r r o r ( f " W e b S o c k e t   e r r o r   f o r   c a l l   { c a l l _ i d } :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
         f i n a l l y : 
                 #   R e m o v e   w e b s o c k e t   o n   d i s c o n n e c t 
                 i f   c a l l _ i d   i n   a c t i v e _ c a l l _ w e b s o c k e t s : 
                         a c t i v e _ c a l l _ w e b s o c k e t s [ c a l l _ i d ] . r e m o v e ( w e b s o c k e t ) 
                         i f   n o t   a c t i v e _ c a l l _ w e b s o c k e t s [ c a l l _ i d ] : 
                                 d e l   a c t i v e _ c a l l _ w e b s o c k e t s [ c a l l _ i d ] 
 
 
 #   F u n c t i o n   t o   b r o a d c a s t   c a l l   e v e n t s   t o   w e b s o c k e t   c l i e n t s 
 a s y n c   d e f   b r o a d c a s t _ c a l l _ e v e n t ( c a l l _ e v e n t :   C a l l E v e n t ) : 
         c a l l _ i d   =   c a l l _ e v e n t . c a l l _ i d 
         i f   c a l l _ i d   i n   a c t i v e _ c a l l _ w e b s o c k e t s : 
                 f o r   w e b s o c k e t   i n   a c t i v e _ c a l l _ w e b s o c k e t s [ c a l l _ i d ] : 
                         t r y : 
                                 a w a i t   w e b s o c k e t . s e n d _ j s o n ( c a l l _ e v e n t . d i c t ( ) ) 
                         e x c e p t   E x c e p t i o n   a s   e : 
                                 l o g g e r . e r r o r ( f " E r r o r   s e n d i n g   e v e n t   t o   w e b s o c k e t :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
 
 
 #   S t a r t u p   e v e n t 
 @ a p p . o n _ e v e n t ( " s t a r t u p " ) 
 a s y n c   d e f   s t a r t u p _ e v e n t ( ) : 
         #   R e c o r d   s t a r t   t i m e   f o r   u p t i m e   c a l c u l a t i o n 
         a p p . s t a r t _ t i m e   =   t i m e . t i m e ( ) 
         l o g g e r . i n f o ( " A P I   s e r v e r   s t a r t e d " ) 
 
 
 #   S h u t d o w n   e v e n t 
 @ a p p . o n _ e v e n t ( " s h u t d o w n " ) 
 a s y n c   d e f   s h u t d o w n _ e v e n t ( ) : 
         #   C l o s e   a n y   a c t i v e   w e b s o c k e t s 
         f o r   c a l l _ i d ,   w e b s o c k e t s   i n   a c t i v e _ c a l l _ w e b s o c k e t s . i t e m s ( ) : 
                 f o r   w e b s o c k e t   i n   w e b s o c k e t s : 
                         t r y : 
                                 a w a i t   w e b s o c k e t . c l o s e ( ) 
                         e x c e p t   E x c e p t i o n : 
                                 p a s s 
         
         l o g g e r . i n f o ( " A P I   s e r v e r   s h u t d o w n " ) 
 