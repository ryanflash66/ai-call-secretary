" " " 
 V o i c e   c l o n i n g   f u n c t i o n a l i t y . 
 A l l o w s   c r e a t i o n   o f   c u s t o m   v o i c e   m o d e l s   f o r   T T S   u s i n g   s a m p l e   r e c o r d i n g s . 
 " " " 
 i m p o r t   o s 
 i m p o r t   l o g g i n g 
 i m p o r t   y a m l 
 i m p o r t   j s o n 
 i m p o r t   t e m p f i l e 
 i m p o r t   s h u t i l 
 i m p o r t   s u b p r o c e s s 
 f r o m   t y p i n g   i m p o r t   O p t i o n a l ,   D i c t ,   A n y ,   L i s t ,   T u p l e ,   U n i o n 
 
 l o g g e r   =   l o g g i n g . g e t L o g g e r ( _ _ n a m e _ _ ) 
 
 c l a s s   V o i c e C l o n e r : 
         " " " 
         V o i c e   c l o n i n g   f u n c t i o n a l i t y   t o   c r e a t e   c u s t o m   T T S   v o i c e s . 
         " " " 
         
         d e f   _ _ i n i t _ _ ( s e l f ,   c o n f i g _ p a t h :   O p t i o n a l [ s t r ]   =   N o n e ) : 
                 " " " 
                 I n i t i a l i z e   t h e   v o i c e   c l o n e r   w i t h   c o n f i g u r a t i o n . 
                 
                 A r g s : 
                         c o n f i g _ p a t h :   P a t h   t o   t h e   c o n f i g u r a t i o n   f i l e 
                 " " " 
                 s e l f . c o n f i g _ p a t h   =   c o n f i g _ p a t h   o r   o s . p a t h . j o i n ( 
                         o s . p a t h . d i r n a m e ( _ _ f i l e _ _ ) ,   
                         " . . / . . / c o n f i g / d e f a u l t . y m l " 
                 ) 
                 
                 #   D e f a u l t   s e t t i n g s 
                 s e l f . e n a b l e d   =   F a l s e 
                 s e l f . t r a i n i n g _ s a m p l e s   =   5 
                 s e l f . t r a i n i n g _ t i m e   =   3 0 0     #   s e c o n d s 
                 s e l f . v o i c e _ d i r   =   o s . p a t h . j o i n ( o s . p a t h . d i r n a m e ( _ _ f i l e _ _ ) ,   " . . / . . / d a t a / v o i c e s " ) 
                 s e l f . t e m p _ d i r   =   o s . p a t h . j o i n ( o s . p a t h . d i r n a m e ( _ _ f i l e _ _ ) ,   " . . / . . / d a t a / t e m p " ) 
                 
                 #   L o a d   c o n f i g u r a t i o n 
                 s e l f . _ l o a d _ c o n f i g ( ) 
                 
                 #   E n s u r e   d i r e c t o r i e s   e x i s t 
                 o s . m a k e d i r s ( s e l f . v o i c e _ d i r ,   e x i s t _ o k = T r u e ) 
                 o s . m a k e d i r s ( s e l f . t e m p _ d i r ,   e x i s t _ o k = T r u e ) 
                 
                 l o g g e r . i n f o ( f " V o i c e   c l o n e r   i n i t i a l i z e d ,   e n a b l e d :   { s e l f . e n a b l e d } " ) 
         
         d e f   _ l o a d _ c o n f i g ( s e l f )   - >   N o n e : 
                 " " " 
                 L o a d   v o i c e   c l o n i n g   c o n f i g u r a t i o n   f r o m   Y A M L   f i l e . 
                 " " " 
                 t r y : 
                         w i t h   o p e n ( s e l f . c o n f i g _ p a t h ,   ' r ' )   a s   f : 
                                 c o n f i g   =   y a m l . s a f e _ l o a d ( f ) 
                         
                         i f   c o n f i g   a n d   ' v o i c e '   i n   c o n f i g   a n d   ' v o i c e _ c l o n e '   i n   c o n f i g [ ' v o i c e ' ] : 
                                 v c _ c o n f i g   =   c o n f i g [ ' v o i c e ' ] [ ' v o i c e _ c l o n e ' ] 
                                 
                                 i f   ' e n a b l e d '   i n   v c _ c o n f i g : 
                                         s e l f . e n a b l e d   =   b o o l ( v c _ c o n f i g [ ' e n a b l e d ' ] ) 
                                 
                                 i f   ' t r a i n i n g _ s a m p l e s '   i n   v c _ c o n f i g : 
                                         s e l f . t r a i n i n g _ s a m p l e s   =   i n t ( v c _ c o n f i g [ ' t r a i n i n g _ s a m p l e s ' ] ) 
                                 
                                 i f   ' t r a i n i n g _ t i m e '   i n   v c _ c o n f i g : 
                                         s e l f . t r a i n i n g _ t i m e   =   i n t ( v c _ c o n f i g [ ' t r a i n i n g _ t i m e ' ] ) 
                                 
                                 i f   ' v o i c e _ d i r '   i n   v c _ c o n f i g : 
                                         s e l f . v o i c e _ d i r   =   v c _ c o n f i g [ ' v o i c e _ d i r ' ] 
                                 
                                 i f   ' t e m p _ d i r '   i n   v c _ c o n f i g : 
                                         s e l f . t e m p _ d i r   =   v c _ c o n f i g [ ' t e m p _ d i r ' ] 
                                 
                         l o g g e r . i n f o ( f " L o a d e d   v o i c e   c l o n i n g   c o n f i g u r a t i o n   f r o m   { s e l f . c o n f i g _ p a t h } " ) 
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   l o a d i n g   c o n f i g u r a t i o n :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
         
         d e f   c r e a t e _ v o i c e ( s e l f ,   v o i c e _ n a m e :   s t r ,   a u d i o _ s a m p l e s :   L i s t [ U n i o n [ s t r ,   b y t e s ] ] ,   
                                         m e t a d a t a :   O p t i o n a l [ D i c t [ s t r ,   A n y ] ]   =   N o n e )   - >   T u p l e [ b o o l ,   s t r ] : 
                 " " " 
                 C r e a t e   a   n e w   v o i c e   m o d e l   f r o m   a u d i o   s a m p l e s . 
                 
                 A r g s : 
                         v o i c e _ n a m e :   N a m e   f o r   t h e   n e w   v o i c e 
                         a u d i o _ s a m p l e s :   L i s t   o f   a u d i o   s a m p l e s   ( f i l e   p a t h s   o r   a u d i o   d a t a ) 
                         m e t a d a t a :   O p t i o n a l   m e t a d a t a   f o r   t h e   v o i c e 
                         
                 R e t u r n s : 
                         T u p l e   o f   ( s u c c e s s ,   m e s s a g e ) 
                 " " " 
                 i f   n o t   s e l f . e n a b l e d : 
                         l o g g e r . w a r n i n g ( " V o i c e   c l o n i n g   i s   d i s a b l e d   i n   c o n f i g u r a t i o n " ) 
                         r e t u r n   F a l s e ,   " V o i c e   c l o n i n g   i s   d i s a b l e d " 
                 
                 i f   l e n ( a u d i o _ s a m p l e s )   <   s e l f . t r a i n i n g _ s a m p l e s : 
                         l o g g e r . w a r n i n g ( f " N o t   e n o u g h   a u d i o   s a m p l e s   p r o v i d e d .   N e e d   a t   l e a s t   { s e l f . t r a i n i n g _ s a m p l e s } " ) 
                         r e t u r n   F a l s e ,   f " N o t   e n o u g h   a u d i o   s a m p l e s .   N e e d   a t   l e a s t   { s e l f . t r a i n i n g _ s a m p l e s } " 
                 
                 t r y : 
                         l o g g e r . i n f o ( f " C r e a t i n g   v o i c e   m o d e l :   { v o i c e _ n a m e } " ) 
                         
                         #   C r e a t e   a   u n i q u e   v o i c e   d i r e c t o r y 
                         v o i c e _ p a t h   =   o s . p a t h . j o i n ( s e l f . v o i c e _ d i r ,   v o i c e _ n a m e ) 
                         i f   o s . p a t h . e x i s t s ( v o i c e _ p a t h ) : 
                                 l o g g e r . w a r n i n g ( f " V o i c e   ' { v o i c e _ n a m e } '   a l r e a d y   e x i s t s " ) 
                                 r e t u r n   F a l s e ,   f " V o i c e   ' { v o i c e _ n a m e } '   a l r e a d y   e x i s t s " 
                         
                         o s . m a k e d i r s ( v o i c e _ p a t h ,   e x i s t _ o k = T r u e ) 
                         
                         #   P r o c e s s   a u d i o   s a m p l e s 
                         s a m p l e _ p a t h s   =   [ ] 
                         f o r   i ,   s a m p l e   i n   e n u m e r a t e ( a u d i o _ s a m p l e s ) : 
                                 s a m p l e _ p a t h   =   s e l f . _ p r o c e s s _ a u d i o _ s a m p l e ( s a m p l e ,   v o i c e _ n a m e ,   i ) 
                                 i f   s a m p l e _ p a t h : 
                                         s a m p l e _ p a t h s . a p p e n d ( s a m p l e _ p a t h ) 
                         
                         i f   l e n ( s a m p l e _ p a t h s )   <   s e l f . t r a i n i n g _ s a m p l e s : 
                                 l o g g e r . w a r n i n g ( f " N o t   e n o u g h   v a l i d   a u d i o   s a m p l e s   a f t e r   p r o c e s s i n g " ) 
                                 s h u t i l . r m t r e e ( v o i c e _ p a t h ) 
                                 r e t u r n   F a l s e ,   " N o t   e n o u g h   v a l i d   a u d i o   s a m p l e s   a f t e r   p r o c e s s i n g " 
                         
                         #   T r a i n   t h e   v o i c e   m o d e l 
                         #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   c a l l   t h e   v o i c e   c l o n i n g   s y s t e m 
                         #   F o r   t h i s   e x a m p l e ,   w e ' l l   s i m u l a t e   t h e   t r a i n i n g   p r o c e s s 
                         s u c c e s s ,   m e s s a g e   =   s e l f . _ t r a i n _ v o i c e _ m o d e l ( v o i c e _ n a m e ,   s a m p l e _ p a t h s ,   m e t a d a t a ) 
                         
                         i f   n o t   s u c c e s s : 
                                 l o g g e r . e r r o r ( f " V o i c e   t r a i n i n g   f a i l e d :   { m e s s a g e } " ) 
                                 s h u t i l . r m t r e e ( v o i c e _ p a t h ) 
                                 r e t u r n   F a l s e ,   m e s s a g e 
                         
                         l o g g e r . i n f o ( f " V o i c e   ' { v o i c e _ n a m e } '   c r e a t e d   s u c c e s s f u l l y " ) 
                         r e t u r n   T r u e ,   f " V o i c e   ' { v o i c e _ n a m e } '   c r e a t e d   s u c c e s s f u l l y " 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   c r e a t i n g   v o i c e :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         #   C l e a n   u p   a n y   p a r t i a l   d i r e c t o r y 
                         i f   o s . p a t h . e x i s t s ( v o i c e _ p a t h ) : 
                                 s h u t i l . r m t r e e ( v o i c e _ p a t h ) 
                         r e t u r n   F a l s e ,   f " E r r o r   c r e a t i n g   v o i c e :   { s t r ( e ) } " 
         
         d e f   _ p r o c e s s _ a u d i o _ s a m p l e ( s e l f ,   s a m p l e :   U n i o n [ s t r ,   b y t e s ] ,   v o i c e _ n a m e :   s t r ,   i n d e x :   i n t )   - >   O p t i o n a l [ s t r ] : 
                 " " " 
                 P r o c e s s   a n   a u d i o   s a m p l e   f o r   v o i c e   t r a i n i n g . 
                 
                 A r g s : 
                         s a m p l e :   T h e   a u d i o   s a m p l e   ( f i l e   p a t h   o r   a u d i o   d a t a ) 
                         v o i c e _ n a m e :   N a m e   o f   t h e   v o i c e   b e i n g   c r e a t e d 
                         i n d e x :   S a m p l e   i n d e x 
                         
                 R e t u r n s : 
                         P a t h   t o   t h e   p r o c e s s e d   s a m p l e   o r   N o n e   i f   p r o c e s s i n g   f a i l e d 
                 " " " 
                 t r y : 
                         #   C r e a t e   a   u n i q u e   s a m p l e   n a m e 
                         s a m p l e _ n a m e   =   f " { v o i c e _ n a m e } _ s a m p l e _ { i n d e x : 0 3 d } . w a v " 
                         s a m p l e _ p a t h   =   o s . p a t h . j o i n ( s e l f . v o i c e _ d i r ,   v o i c e _ n a m e ,   s a m p l e _ n a m e ) 
                         
                         #   P r o c e s s   t h e   s a m p l e   b a s e d   o n   i t s   t y p e 
                         i f   i s i n s t a n c e ( s a m p l e ,   s t r )   a n d   o s . p a t h . e x i s t s ( s a m p l e ) : 
                                 #   I t ' s   a   f i l e   p a t h 
                                 l o g g e r . i n f o ( f " P r o c e s s i n g   a u d i o   s a m p l e   f r o m   f i l e :   { s a m p l e } " ) 
                                 
                                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   w e   w o u l d   n o r m a l i z e   a u d i o ,   c h e c k   q u a l i t y ,   e t c . 
                                 #   F o r   n o w ,   w e ' l l   j u s t   c o p y   t h e   f i l e 
                                 s h u t i l . c o p y 2 ( s a m p l e ,   s a m p l e _ p a t h ) 
                                 
                         e l i f   i s i n s t a n c e ( s a m p l e ,   b y t e s ) : 
                                 #   I t ' s   a u d i o   d a t a 
                                 l o g g e r . i n f o ( f " P r o c e s s i n g   a u d i o   s a m p l e   f r o m   b i n a r y   d a t a " ) 
                                 
                                 #   S a v e   t o   a   t e m p o r a r y   f i l e 
                                 w i t h   o p e n ( s a m p l e _ p a t h ,   ' w b ' )   a s   f : 
                                         f . w r i t e ( s a m p l e ) 
                                 
                                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   w e   w o u l d   n o r m a l i z e   t h e   a u d i o   h e r e 
                         
                         l o g g e r . i n f o ( f " A u d i o   s a m p l e   p r o c e s s e d :   { s a m p l e _ p a t h } " ) 
                         r e t u r n   s a m p l e _ p a t h 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   p r o c e s s i n g   a u d i o   s a m p l e :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         r e t u r n   N o n e 
         
         d e f   _ t r a i n _ v o i c e _ m o d e l ( s e l f ,   v o i c e _ n a m e :   s t r ,   s a m p l e _ p a t h s :   L i s t [ s t r ] , 
                                                     m e t a d a t a :   O p t i o n a l [ D i c t [ s t r ,   A n y ] ]   =   N o n e )   - >   T u p l e [ b o o l ,   s t r ] : 
                 " " " 
                 T r a i n   a   v o i c e   m o d e l   f r o m   p r o c e s s e d   s a m p l e s . 
                 
                 A r g s : 
                         v o i c e _ n a m e :   N a m e   o f   t h e   v o i c e   b e i n g   c r e a t e d 
                         s a m p l e _ p a t h s :   L i s t   o f   p a t h s   t o   p r o c e s s e d   a u d i o   s a m p l e s 
                         m e t a d a t a :   O p t i o n a l   m e t a d a t a   f o r   t h e   v o i c e 
                         
                 R e t u r n s : 
                         T u p l e   o f   ( s u c c e s s ,   m e s s a g e ) 
                 " " " 
                 t r y : 
                         l o g g e r . i n f o ( f " T r a i n i n g   v o i c e   m o d e l   ' { v o i c e _ n a m e } '   w i t h   { l e n ( s a m p l e _ p a t h s ) }   s a m p l e s " ) 
                         
                         v o i c e _ p a t h   =   o s . p a t h . j o i n ( s e l f . v o i c e _ d i r ,   v o i c e _ n a m e ) 
                         
                         #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   c a l l   t h e   v o i c e   c l o n i n g   s y s t e m 
                         #   W e ' l l   s i m u l a t e   t h e   t r a i n i n g   p r o c e s s   w i t h   a   w a i t 
                         l o g g e r . i n f o ( f " V o i c e   t r a i n i n g   w o u l d   t a k e   a p p r o x i m a t e l y   { s e l f . t r a i n i n g _ t i m e }   s e c o n d s " ) 
                         
                         #   C r e a t e   a   m e t a d a t a   f i l e 
                         m o d e l _ m e t a d a t a   =   { 
                                 " n a m e " :   v o i c e _ n a m e , 
                                 " s a m p l e s " :   l e n ( s a m p l e _ p a t h s ) , 
                                 " c r e a t e d _ a t " :   o s . p a t h . g e t m t i m e ( v o i c e _ p a t h ) , 
                                 " t r a i n i n g _ t i m e " :   s e l f . t r a i n i n g _ t i m e 
                         } 
                         
                         i f   m e t a d a t a : 
                                 m o d e l _ m e t a d a t a . u p d a t e ( m e t a d a t a ) 
                         
                         #   S a v e   m e t a d a t a 
                         w i t h   o p e n ( o s . p a t h . j o i n ( v o i c e _ p a t h ,   " m e t a d a t a . j s o n " ) ,   ' w ' )   a s   f : 
                                 j s o n . d u m p ( m o d e l _ m e t a d a t a ,   f ,   i n d e n t = 2 ) 
                         
                         #   C r e a t e   a   d u m m y   m o d e l   f i l e   t o   s i m u l a t e   t h e   t r a i n e d   m o d e l 
                         w i t h   o p e n ( o s . p a t h . j o i n ( v o i c e _ p a t h ,   " m o d e l . b i n " ) ,   ' w b ' )   a s   f : 
                                 f . w r i t e ( b " S I M U L A T E D _ V O I C E _ M O D E L _ D A T A " ) 
                         
                         l o g g e r . i n f o ( f " V o i c e   m o d e l   ' { v o i c e _ n a m e } '   t r a i n e d   s u c c e s s f u l l y " ) 
                         r e t u r n   T r u e ,   " V o i c e   m o d e l   t r a i n e d   s u c c e s s f u l l y " 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   t r a i n i n g   v o i c e   m o d e l :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         r e t u r n   F a l s e ,   f " E r r o r   t r a i n i n g   v o i c e   m o d e l :   { s t r ( e ) } " 
         
         d e f   l i s t _ v o i c e s ( s e l f )   - >   D i c t [ s t r ,   D i c t [ s t r ,   A n y ] ] : 
                 " " " 
                 L i s t   a l l   a v a i l a b l e   c u s t o m   v o i c e s . 
                 
                 R e t u r n s : 
                         D i c t i o n a r y   o f   v o i c e   n a m e s   a n d   t h e i r   m e t a d a t a 
                 " " " 
                 v o i c e s   =   { } 
                 
                 t r y : 
                         #   C h e c k   i f   v o i c e   d i r e c t o r y   e x i s t s 
                         i f   n o t   o s . p a t h . e x i s t s ( s e l f . v o i c e _ d i r ) : 
                                 l o g g e r . w a r n i n g ( f " V o i c e   d i r e c t o r y   d o e s   n o t   e x i s t :   { s e l f . v o i c e _ d i r } " ) 
                                 r e t u r n   v o i c e s 
                         
                         #   S c a n   t h e   v o i c e   d i r e c t o r y   f o r   v o i c e   m o d e l s 
                         f o r   v o i c e _ n a m e   i n   o s . l i s t d i r ( s e l f . v o i c e _ d i r ) : 
                                 v o i c e _ p a t h   =   o s . p a t h . j o i n ( s e l f . v o i c e _ d i r ,   v o i c e _ n a m e ) 
                                 
                                 i f   o s . p a t h . i s d i r ( v o i c e _ p a t h ) : 
                                         #   C h e c k   f o r   m e t a d a t a   f i l e 
                                         m e t a d a t a _ p a t h   =   o s . p a t h . j o i n ( v o i c e _ p a t h ,   " m e t a d a t a . j s o n " ) 
                                         i f   o s . p a t h . e x i s t s ( m e t a d a t a _ p a t h ) : 
                                                 w i t h   o p e n ( m e t a d a t a _ p a t h ,   ' r ' )   a s   f : 
                                                         t r y : 
                                                                 m e t a d a t a   =   j s o n . l o a d ( f ) 
                                                                 v o i c e s [ v o i c e _ n a m e ]   =   m e t a d a t a 
                                                         e x c e p t   j s o n . J S O N D e c o d e E r r o r : 
                                                                 l o g g e r . w a r n i n g ( f " I n v a l i d   m e t a d a t a   f o r   v o i c e :   { v o i c e _ n a m e } " ) 
                                                                 v o i c e s [ v o i c e _ n a m e ]   =   { " n a m e " :   v o i c e _ n a m e ,   " e r r o r " :   " I n v a l i d   m e t a d a t a " } 
                                         e l s e : 
                                                 #   C r e a t e   b a s i c   m e t a d a t a   f r o m   d i r e c t o r y 
                                                 v o i c e s [ v o i c e _ n a m e ]   =   { 
                                                         " n a m e " :   v o i c e _ n a m e , 
                                                         " c r e a t e d _ a t " :   o s . p a t h . g e t m t i m e ( v o i c e _ p a t h ) 
                                                 } 
                         
                         l o g g e r . i n f o ( f " F o u n d   { l e n ( v o i c e s ) }   c u s t o m   v o i c e s " ) 
                         r e t u r n   v o i c e s 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   l i s t i n g   v o i c e s :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         r e t u r n   v o i c e s 
         
         d e f   d e l e t e _ v o i c e ( s e l f ,   v o i c e _ n a m e :   s t r )   - >   T u p l e [ b o o l ,   s t r ] : 
                 " " " 
                 D e l e t e   a   c u s t o m   v o i c e . 
                 
                 A r g s : 
                         v o i c e _ n a m e :   N a m e   o f   t h e   v o i c e   t o   d e l e t e 
                         
                 R e t u r n s : 
                         T u p l e   o f   ( s u c c e s s ,   m e s s a g e ) 
                 " " " 
                 t r y : 
                         v o i c e _ p a t h   =   o s . p a t h . j o i n ( s e l f . v o i c e _ d i r ,   v o i c e _ n a m e ) 
                         
                         i f   n o t   o s . p a t h . e x i s t s ( v o i c e _ p a t h ) : 
                                 l o g g e r . w a r n i n g ( f " V o i c e   ' { v o i c e _ n a m e } '   d o e s   n o t   e x i s t " ) 
                                 r e t u r n   F a l s e ,   f " V o i c e   ' { v o i c e _ n a m e } '   d o e s   n o t   e x i s t " 
                         
                         #   R e m o v e   t h e   v o i c e   d i r e c t o r y 
                         s h u t i l . r m t r e e ( v o i c e _ p a t h ) 
                         
                         l o g g e r . i n f o ( f " V o i c e   ' { v o i c e _ n a m e } '   d e l e t e d   s u c c e s s f u l l y " ) 
                         r e t u r n   T r u e ,   f " V o i c e   ' { v o i c e _ n a m e } '   d e l e t e d   s u c c e s s f u l l y " 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   d e l e t i n g   v o i c e :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         r e t u r n   F a l s e ,   f " E r r o r   d e l e t i n g   v o i c e :   { s t r ( e ) } " 