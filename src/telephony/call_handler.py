" " " 
 C a l l   h a n d l i n g   l o g i c   f o r   i n c o m i n g   c a l l s . 
 T h i s   m o d u l e   p r o c e s s e s   c a l l s   a n d   i n t e g r a t e s   w i t h   S T T ,   L L M ,   a n d   T T S   c o m p o n e n t s . 
 " " " 
 i m p o r t   t i m e 
 i m p o r t   l o g g i n g 
 i m p o r t   a s y n c i o 
 i m p o r t   j s o n 
 i m p o r t   o s 
 f r o m   t y p i n g   i m p o r t   D i c t ,   L i s t ,   O p t i o n a l ,   A n y 
 
 f r o m   s r c . v o i c e . s t t   i m p o r t   S p e e c h T o T e x t 
 f r o m   s r c . v o i c e . t t s   i m p o r t   T e x t T o S p e e c h 
 f r o m   s r c . l l m . c o n t e x t   i m p o r t   C o n v e r s a t i o n C o n t e x t 
 f r o m   s r c . l l m . o l l a m a _ c l i e n t   i m p o r t   O l l a m a C l i e n t 
 f r o m   s r c . w o r k f l o w . a c t i o n s   i m p o r t   A c t i o n H a n d l e r 
 
 l o g g e r   =   l o g g i n g . g e t L o g g e r ( _ _ n a m e _ _ ) 
 
 c l a s s   C a l l H a n d l e r : 
         " " " 
         H a n d l e s   i n c o m i n g   c a l l s ,   m a n a g e s   t h e   c o n v e r s a t i o n ,   a n d   o r c h e s t r a t e s 
         t h e   v a r i o u s   c o m p o n e n t s   ( S T T ,   L L M ,   T T S ) . 
         " " " 
         
         d e f   _ _ i n i t _ _ ( s e l f ,   c a l l _ m e t a d a t a :   D i c t [ s t r ,   A n y ] ) : 
                 " " " 
                 I n i t i a l i z e   t h e   c a l l   h a n d l e r   w i t h   c a l l   m e t a d a t a . 
                 
                 A r g s : 
                         c a l l _ m e t a d a t a :   D i c t i o n a r y   c o n t a i n i n g   c a l l   i n f o r m a t i o n   l i k e   c a l l e r   I D ,   t i m e s t a m p ,   e t c . 
                 " " " 
                 s e l f . c a l l _ m e t a d a t a   =   c a l l _ m e t a d a t a 
                 s e l f . c a l l _ i d   =   c a l l _ m e t a d a t a . g e t ( ' c a l l _ i d ' ,   ' u n k n o w n ' ) 
                 s e l f . c a l l e r _ n u m b e r   =   c a l l _ m e t a d a t a . g e t ( ' c a l l e r _ n u m b e r ' ,   ' u n k n o w n ' ) 
                 s e l f . c a l l e r _ n a m e   =   c a l l _ m e t a d a t a . g e t ( ' c a l l e r _ n a m e ' ,   ' U n k n o w n ' ) 
                 
                 #   I n i t i a l i z e   c o m p o n e n t s 
                 s e l f . s t t   =   S p e e c h T o T e x t ( ) 
                 s e l f . t t s   =   T e x t T o S p e e c h ( ) 
                 s e l f . l l m   =   O l l a m a C l i e n t ( ) 
                 s e l f . c o n t e x t   =   C o n v e r s a t i o n C o n t e x t ( ) 
                 s e l f . a c t i o n _ h a n d l e r   =   A c t i o n H a n d l e r ( ) 
                 
                 #   C a l l   s t a t e 
                 s e l f . c o n v e r s a t i o n _ h i s t o r y   =   [ ] 
                 s e l f . c a l l _ d u r a t i o n   =   0 
                 s e l f . s t a r t _ t i m e   =   t i m e . t i m e ( ) 
                 
                 l o g g e r . i n f o ( f " C a l l   h a n d l e r   i n i t i a l i z e d   f o r   c a l l   { s e l f . c a l l _ i d }   f r o m   { s e l f . c a l l e r _ n a m e }   < { s e l f . c a l l e r _ n u m b e r } > " ) 
         
         d e f   p r o c e s s _ c a l l ( s e l f ,   s e s s i o n )   - >   N o n e : 
                 " " " 
                 M a i n   m e t h o d   t o   p r o c e s s   a   c a l l   f r o m   s t a r t   t o   f i n i s h . 
                 
                 A r g s : 
                         s e s s i o n :   T h e   t e l e p h o n y   s e s s i o n   o b j e c t 
                 " " " 
                 t r y : 
                         #   I n i t i a l i z e   t h e   c o n v e r s a t i o n   c o n t e x t 
                         s e l f . c o n t e x t . i n i t _ c o n v e r s a t i o n ( 
                                 c a l l e r _ n a m e = s e l f . c a l l e r _ n a m e , 
                                 c a l l e r _ n u m b e r = s e l f . c a l l e r _ n u m b e r , 
                                 c a l l _ i d = s e l f . c a l l _ i d 
                         ) 
                         
                         #   P l a y   w e l c o m e   g r e e t i n g 
                         i n i t i a l _ g r e e t i n g   =   " H e l l o ,   t h i s   i s   y o u r   A I   a s s i s t a n t .   H o w   c a n   I   h e l p   y o u   t o d a y ? " 
                         s e l f . _ p l a y _ r e s p o n s e ( s e s s i o n ,   i n i t i a l _ g r e e t i n g ) 
                         
                         #   M a i n   c o n v e r s a t i o n   l o o p 
                         c o n t i n u e _ c a l l   =   T r u e 
                         w h i l e   c o n t i n u e _ c a l l : 
                                 #   L i s t e n   f o r   u s e r   i n p u t 
                                 u s e r _ a u d i o   =   s e l f . _ c a p t u r e _ a u d i o ( s e s s i o n ) 
                                 i f   n o t   u s e r _ a u d i o : 
                                         c o n t i n u e 
                                 
                                 #   C o n v e r t   s p e e c h   t o   t e x t 
                                 u s e r _ t e x t   =   s e l f . s t t . t r a n s c r i b e ( u s e r _ a u d i o ) 
                                 i f   n o t   u s e r _ t e x t   o r   u s e r _ t e x t . s t r i p ( )   = =   " " : 
                                         s e l f . _ p l a y _ r e s p o n s e ( s e s s i o n ,   " I   d i d n ' t   c a t c h   t h a t .   C o u l d   y o u   p l e a s e   r e p e a t ? " ) 
                                         c o n t i n u e 
                                 
                                 l o g g e r . i n f o ( f " U s e r   s a i d :   { u s e r _ t e x t } " ) 
                                 s e l f . c o n v e r s a t i o n _ h i s t o r y . a p p e n d ( { " r o l e " :   " u s e r " ,   " c o n t e n t " :   u s e r _ t e x t } ) 
                                 
                                 #   C h e c k   f o r   c a l l - e n d i n g   p h r a s e s 
                                 i f   s e l f . _ s h o u l d _ e n d _ c a l l ( u s e r _ t e x t ) : 
                                         s e l f . _ p l a y _ r e s p o n s e ( s e s s i o n ,   " T h a n k   y o u   f o r   c a l l i n g .   G o o d b y e ! " ) 
                                         c o n t i n u e _ c a l l   =   F a l s e 
                                         b r e a k 
                                 
                                 #   P r o c e s s   w i t h   L L M 
                                 s e l f . c o n t e x t . a d d _ u s e r _ m e s s a g e ( u s e r _ t e x t ) 
                                 l l m _ r e s p o n s e   =   s e l f . l l m . g e n e r a t e _ r e s p o n s e ( s e l f . c o n t e x t . g e t _ c o n t e x t ( ) ) 
                                 
                                 i f   n o t   l l m _ r e s p o n s e : 
                                         s e l f . _ p l a y _ r e s p o n s e ( s e s s i o n ,   " I   a p o l o g i z e ,   b u t   I ' m   h a v i n g   t r o u b l e   p r o c e s s i n g   y o u r   r e q u e s t . " ) 
                                         c o n t i n u e 
                                 
                                 l o g g e r . i n f o ( f " A I   r e s p o n s e :   { l l m _ r e s p o n s e } " ) 
                                 s e l f . c o n v e r s a t i o n _ h i s t o r y . a p p e n d ( { " r o l e " :   " a s s i s t a n t " ,   " c o n t e n t " :   l l m _ r e s p o n s e } ) 
                                 s e l f . c o n t e x t . a d d _ a s s i s t a n t _ m e s s a g e ( l l m _ r e s p o n s e ) 
                                 
                                 #   C h e c k   f o r   a c t i o n s   t o   p e r f o r m 
                                 a c t i o n s   =   s e l f . a c t i o n _ h a n d l e r . e x t r a c t _ a c t i o n s ( l l m _ r e s p o n s e ) 
                                 f o r   a c t i o n   i n   a c t i o n s : 
                                         a c t i o n _ r e s u l t   =   s e l f . a c t i o n _ h a n d l e r . e x e c u t e _ a c t i o n ( a c t i o n ) 
                                         i f   a c t i o n _ r e s u l t : 
                                                 s e l f . c o n t e x t . a d d _ a c t i o n _ r e s u l t ( a c t i o n ,   a c t i o n _ r e s u l t ) 
                                 
                                 #   S p e a k   t h e   r e s p o n s e 
                                 s e l f . _ p l a y _ r e s p o n s e ( s e s s i o n ,   l l m _ r e s p o n s e ) 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   p r o c e s s i n g   c a l l :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         s e l f . _ p l a y _ r e s p o n s e ( s e s s i o n ,   " I   a p o l o g i z e ,   b u t   t h e r e   w a s   a n   e r r o r   p r o c e s s i n g   y o u r   c a l l .   P l e a s e   t r y   a g a i n   l a t e r . " ) 
                 f i n a l l y : 
                         #   C a l l   c l e a n u p 
                         s e l f . c a l l _ d u r a t i o n   =   t i m e . t i m e ( )   -   s e l f . s t a r t _ t i m e 
                         s e l f . _ s a v e _ c a l l _ r e c o r d ( ) 
                         l o g g e r . i n f o ( f " C a l l   { s e l f . c a l l _ i d }   c o m p l e t e d .   D u r a t i o n :   { s e l f . c a l l _ d u r a t i o n : . 2 f }   s e c o n d s " ) 
         
         d e f   _ c a p t u r e _ a u d i o ( s e l f ,   s e s s i o n ,   m a x _ d u r a t i o n :   i n t   =   1 0 )   - >   O p t i o n a l [ b y t e s ] : 
                 " " " 
                 C a p t u r e s   a u d i o   f r o m   t h e   c a l l   s e s s i o n . 
                 
                 A r g s : 
                         s e s s i o n :   T h e   t e l e p h o n y   s e s s i o n   o b j e c t 
                         m a x _ d u r a t i o n :   M a x i m u m   r e c o r d i n g   d u r a t i o n   i n   s e c o n d s 
                         
                 R e t u r n s : 
                         A u d i o   d a t a   a s   b y t e s   o r   N o n e   i f   c a p t u r e   f a i l e d 
                 " " " 
                 #   I m p l e m e n t a t i o n   d e p e n d s   o n   t h e   s p e c i f i c   t e l e p h o n y   s y s t e m 
                 #   F o r   F r e e S W I T C H ,   w e   w o u l d   u s e   r e c o r d   o r   a u d i o _ f o r k 
                 t r y : 
                         #   F o r   n o w ,   w e ' l l   s i m u l a t e   a u d i o   c a p t u r e 
                         #   I n   p r o d u c t i o n ,   t h i s   w o u l d   i n t e r a c t   w i t h   t h e   s e s s i o n   o b j e c t 
                         l o g g e r . d e b u g ( f " C a p t u r i n g   a u d i o   f o r   u p   t o   { m a x _ d u r a t i o n }   s e c o n d s " ) 
                         
                         #   T h i s   i s   a   p l a c e h o l d e r   -   a c t u a l   i m p l e m e n t a t i o n   w o u l d   u s e   F r e e S W I T C H   A P I s 
                         #   E x a m p l e :   s e s s i o n . e x e c u t e ( " r e c o r d " ,   f " / t m p / { s e l f . c a l l _ i d } . w a v   { m a x _ d u r a t i o n } " ) 
                         
                         #   S i m u l a t i n g   r e c o r d i n g   d e l a y 
                         t i m e . s l e e p ( 2 )     #   P r e t e n d   u s e r   s p o k e   f o r   2   s e c o n d s 
                         
                         #   I n   a   r e a l   i m p l e m e n t a t i o n ,   w e   w o u l d   r e t u r n   t h e   c a p t u r e d   a u d i o   b y t e s 
                         r e t u r n   b " S I M U L A T E D _ A U D I O _ D A T A " 
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   c a p t u r i n g   a u d i o :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         r e t u r n   N o n e 
         
         d e f   _ p l a y _ r e s p o n s e ( s e l f ,   s e s s i o n ,   t e x t :   s t r )   - >   N o n e : 
                 " " " 
                 C o n v e r t s   t e x t   t o   s p e e c h   a n d   p l a y s   i t   t o   t h e   c a l l e r . 
                 
                 A r g s : 
                         s e s s i o n :   T h e   t e l e p h o n y   s e s s i o n   o b j e c t 
                         t e x t :   T h e   t e x t   t o   s p e a k 
                 " " " 
                 t r y : 
                         #   C o n v e r t   t e x t   t o   s p e e c h 
                         a u d i o _ d a t a   =   s e l f . t t s . s y n t h e s i z e ( t e x t ) 
                         
                         #   I n   a   r e a l   i m p l e m e n t a t i o n ,   w e   w o u l d   p l a y   t h i s   a u d i o   t h r o u g h   t h e   s e s s i o n 
                         #   E x a m p l e :   s e s s i o n . e x e c u t e ( " p l a y b a c k " ,   f " / t m p / { s e l f . c a l l _ i d } _ r e s p o n s e . w a v " ) 
                         
                         #   T h i s   i s   a   p l a c e h o l d e r   -   a c t u a l   i m p l e m e n t a t i o n   w o u l d   u s e   F r e e S W I T C H   A P I s 
                         l o g g e r . i n f o ( f " P l a y i n g   r e s p o n s e :   { t e x t } " ) 
                         
                         #   S i m u l a t e   p l a y b a c k   d e l a y   b a s e d   o n   t e x t   l e n g t h 
                         p l a y _ t i m e   =   l e n ( t e x t . s p l i t ( ) )   *   0 . 3     #   R o u g h   e s t i m a t e :   0 . 3   s e c o n d s   p e r   w o r d 
                         t i m e . s l e e p ( m i n ( p l a y _ t i m e ,   1 0 ) )     #   C a p   a t   1 0   s e c o n d s   f o r   s i m u l a t i o n 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   p l a y i n g   r e s p o n s e :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
         
         d e f   _ s h o u l d _ e n d _ c a l l ( s e l f ,   t e x t :   s t r )   - >   b o o l : 
                 " " " 
                 D e t e r m i n e s   i f   t h e   c a l l   s h o u l d   b e   e n d e d   b a s e d   o n   t h e   u s e r ' s   i n p u t . 
                 
                 A r g s : 
                         t e x t :   T h e   u s e r ' s   t r a n s c r i b e d   s p e e c h 
                         
                 R e t u r n s : 
                         T r u e   i f   t h e   c a l l   s h o u l d   e n d ,   F a l s e   o t h e r w i s e 
                 " " " 
                 e n d _ p h r a s e s   =   [ 
                         " g o o d b y e " ,   " b y e " ,   " h a n g   u p " ,   " e n d   c a l l " ,   " t h a n k   y o u   g o o d b y e " , 
                         " t h a t ' s   a l l " ,   " t h a t   i s   a l l " ,   " d i s c o n n e c t " ,   " e n d   t h e   c a l l " 
                 ] 
                 
                 r e t u r n   a n y ( p h r a s e   i n   t e x t . l o w e r ( )   f o r   p h r a s e   i n   e n d _ p h r a s e s ) 
         
         d e f   _ s a v e _ c a l l _ r e c o r d ( s e l f )   - >   N o n e : 
                 " " " 
                 S a v e s   t h e   c a l l   r e c o r d   t o   s t o r a g e   f o r   l a t e r   r e f e r e n c e . 
                 " " " 
                 c a l l _ r e c o r d   =   { 
                         " c a l l _ i d " :   s e l f . c a l l _ i d , 
                         " c a l l e r _ n u m b e r " :   s e l f . c a l l e r _ n u m b e r , 
                         " c a l l e r _ n a m e " :   s e l f . c a l l e r _ n a m e , 
                         " s t a r t _ t i m e " :   s e l f . s t a r t _ t i m e , 
                         " d u r a t i o n " :   s e l f . c a l l _ d u r a t i o n , 
                         " c o n v e r s a t i o n " :   s e l f . c o n v e r s a t i o n _ h i s t o r y 
                 } 
                 
                 #   I n   a   p r o d u c t i o n   s y s t e m ,   t h i s   w o u l d   s a v e   t o   a   d a t a b a s e 
                 #   F o r   n o w ,   w e ' l l   l o g   i t   a n d   s a v e   t o   a   J S O N   f i l e   i n   a   d a t a   d i r e c t o r y 
                 l o g _ d i r   =   o s . p a t h . j o i n ( o s . p a t h . d i r n a m e ( _ _ f i l e _ _ ) ,   " . . / . . / d a t a / c a l l _ l o g s " ) 
                 o s . m a k e d i r s ( l o g _ d i r ,   e x i s t _ o k = T r u e ) 
                 
                 l o g _ f i l e   =   o s . p a t h . j o i n ( l o g _ d i r ,   f " { s e l f . c a l l _ i d } . j s o n " ) 
                 t r y : 
                         w i t h   o p e n ( l o g _ f i l e ,   ' w ' )   a s   f : 
                                 j s o n . d u m p ( c a l l _ r e c o r d ,   f ,   i n d e n t = 2 ) 
                         l o g g e r . i n f o ( f " C a l l   r e c o r d   s a v e d   t o   { l o g _ f i l e } " ) 
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   s a v i n g   c a l l   r e c o r d :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 