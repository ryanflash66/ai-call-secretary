" " " 
 S p e e c h - t o - T e x t   m o d u l e   u s i n g   W h i s p e r . 
 C o n v e r t s   a u d i o   t o   t e x t   u s i n g   t h e   W h i s p e r   A S R   m o d e l . 
 " " " 
 i m p o r t   o s 
 i m p o r t   l o g g i n g 
 i m p o r t   t e m p f i l e 
 i m p o r t   y a m l 
 i m p o r t   n u m p y   a s   n p 
 f r o m   t y p i n g   i m p o r t   O p t i o n a l ,   D i c t ,   A n y ,   U n i o n 
 i m p o r t   w h i s p e r 
 
 l o g g e r   =   l o g g i n g . g e t L o g g e r ( _ _ n a m e _ _ ) 
 
 c l a s s   S p e e c h T o T e x t : 
         " " " 
         S p e e c h - t o - t e x t   c o n v e r s i o n   u s i n g   W h i s p e r   A S R . 
         " " " 
         
         d e f   _ _ i n i t _ _ ( s e l f ,   c o n f i g _ p a t h :   O p t i o n a l [ s t r ]   =   N o n e ) : 
                 " " " 
                 I n i t i a l i z e   t h e   S T T   e n g i n e   w i t h   c o n f i g u r a t i o n . 
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
                 s e l f . m o d e l _ n a m e   =   " t i n y " 
                 s e l f . l a n g u a g e   =   " e n " 
                 s e l f . d e v i c e   =   " c p u " 
                 s e l f . c o m p u t e _ t y p e   =   " i n t 8 " 
                 
                 #   L o a d   c o n f i g u r a t i o n 
                 s e l f . _ l o a d _ c o n f i g ( ) 
                 
                 #   L o a d   m o d e l   -   d e f e r   u n t i l   f i r s t   u s e   t o   s a v e   m e m o r y 
                 s e l f . m o d e l   =   N o n e 
                 
                 l o g g e r . i n f o ( f " S T T   i n i t i a l i z e d   w i t h   m o d e l :   { s e l f . m o d e l _ n a m e } ,   l a n g u a g e :   { s e l f . l a n g u a g e } " ) 
         
         d e f   _ l o a d _ c o n f i g ( s e l f )   - >   N o n e : 
                 " " " 
                 L o a d   S T T   c o n f i g u r a t i o n   f r o m   Y A M L   f i l e . 
                 " " " 
                 t r y : 
                         w i t h   o p e n ( s e l f . c o n f i g _ p a t h ,   ' r ' )   a s   f : 
                                 c o n f i g   =   y a m l . s a f e _ l o a d ( f ) 
                         
                         i f   c o n f i g   a n d   ' v o i c e '   i n   c o n f i g   a n d   ' s t t '   i n   c o n f i g [ ' v o i c e ' ] : 
                                 s t t _ c o n f i g   =   c o n f i g [ ' v o i c e ' ] [ ' s t t ' ] 
                                 
                                 i f   ' m o d e l '   i n   s t t _ c o n f i g : 
                                         s e l f . m o d e l _ n a m e   =   s t t _ c o n f i g [ ' m o d e l ' ] 
                                 
                                 i f   ' l a n g u a g e '   i n   s t t _ c o n f i g : 
                                         s e l f . l a n g u a g e   =   s t t _ c o n f i g [ ' l a n g u a g e ' ] 
                                 
                                 i f   ' d e v i c e '   i n   s t t _ c o n f i g : 
                                         s e l f . d e v i c e   =   s t t _ c o n f i g [ ' d e v i c e ' ] 
                                 
                                 i f   ' c o m p u t e _ t y p e '   i n   s t t _ c o n f i g : 
                                         s e l f . c o m p u t e _ t y p e   =   s t t _ c o n f i g [ ' c o m p u t e _ t y p e ' ] 
                                 
                         l o g g e r . i n f o ( f " L o a d e d   S T T   c o n f i g u r a t i o n   f r o m   { s e l f . c o n f i g _ p a t h } " ) 
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   l o a d i n g   c o n f i g u r a t i o n :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
         
         d e f   _ e n s u r e _ m o d e l _ l o a d e d ( s e l f )   - >   N o n e : 
                 " " " 
                 E n s u r e   t h e   W h i s p e r   m o d e l   i s   l o a d e d . 
                 " " " 
                 i f   s e l f . m o d e l   i s   N o n e : 
                         t r y : 
                                 l o g g e r . i n f o ( f " L o a d i n g   W h i s p e r   m o d e l :   { s e l f . m o d e l _ n a m e } " ) 
                                 s e l f . m o d e l   =   w h i s p e r . l o a d _ m o d e l ( 
                                         s e l f . m o d e l _ n a m e , 
                                         d e v i c e = s e l f . d e v i c e , 
                                         c o m p u t e _ t y p e = s e l f . c o m p u t e _ t y p e 
                                 ) 
                                 l o g g e r . i n f o ( " W h i s p e r   m o d e l   l o a d e d   s u c c e s s f u l l y " ) 
                         e x c e p t   E x c e p t i o n   a s   e : 
                                 l o g g e r . e r r o r ( f " E r r o r   l o a d i n g   W h i s p e r   m o d e l :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                                 r a i s e   R u n t i m e E r r o r ( f " F a i l e d   t o   l o a d   W h i s p e r   m o d e l :   { s t r ( e ) } " ) 
         
         d e f   t r a n s c r i b e ( s e l f ,   a u d i o _ d a t a :   U n i o n [ b y t e s ,   s t r ,   n p . n d a r r a y ] ,   
                                     o p t i o n s :   O p t i o n a l [ D i c t [ s t r ,   A n y ] ]   =   N o n e )   - >   s t r : 
                 " " " 
                 T r a n s c r i b e   a u d i o   d a t a   t o   t e x t . 
                 
                 A r g s : 
                         a u d i o _ d a t a :   T h e   a u d i o   d a t a   t o   t r a n s c r i b e .   C a n   b e : 
                                 -   b y t e s :   R a w   a u d i o   d a t a   ( w i l l   b e   s a v e d   t o   t e m p o r a r y   f i l e ) 
                                 -   s t r :   P a t h   t o   a n   a u d i o   f i l e 
                                 -   n p . n d a r r a y :   A u d i o   w a v e f o r m   d a t a 
                         o p t i o n s :   A d d i t i o n a l   o p t i o n s   f o r   t h e   t r a n s c r i p t i o n 
                         
                 R e t u r n s : 
                         T r a n s c r i p t i o n   t e x t 
                 " " " 
                 t r y : 
                         #   E n s u r e   m o d e l   i s   l o a d e d 
                         s e l f . _ e n s u r e _ m o d e l _ l o a d e d ( ) 
                         
                         #   S e t   d e f a u l t   o p t i o n s 
                         t r a n s c r i b e _ o p t i o n s   =   { 
                                 " l a n g u a g e " :   s e l f . l a n g u a g e , 
                                 " t a s k " :   " t r a n s c r i b e " 
                         } 
                         
                         #   U p d a t e   w i t h   a n y   u s e r - p r o v i d e d   o p t i o n s 
                         i f   o p t i o n s : 
                                 t r a n s c r i b e _ o p t i o n s . u p d a t e ( o p t i o n s ) 
                         
                         #   H a n d l e   d i f f e r e n t   t y p e s   o f   a u d i o   i n p u t 
                         a u d i o _ i n p u t   =   a u d i o _ d a t a 
                         t e m p _ f i l e   =   N o n e 
                         
                         i f   i s i n s t a n c e ( a u d i o _ d a t a ,   b y t e s ) : 
                                 #   S a v e   b y t e s   t o   t e m p o r a r y   f i l e 
                                 t e m p _ f i l e   =   t e m p f i l e . N a m e d T e m p o r a r y F i l e ( s u f f i x = " . w a v " ,   d e l e t e = F a l s e ) 
                                 t e m p _ f i l e . w r i t e ( a u d i o _ d a t a ) 
                                 t e m p _ f i l e . c l o s e ( ) 
                                 a u d i o _ i n p u t   =   t e m p _ f i l e . n a m e 
                         
                         #   T r a n s c r i b e   t h e   a u d i o 
                         r e s u l t   =   s e l f . m o d e l . t r a n s c r i b e ( a u d i o _ i n p u t ,   * * t r a n s c r i b e _ o p t i o n s ) 
                         t r a n s c r i p t i o n   =   r e s u l t . g e t ( " t e x t " ,   " " ) . s t r i p ( ) 
                         
                         #   C l e a n   u p   t h e   t e m p o r a r y   f i l e   i f   c r e a t e d 
                         i f   t e m p _ f i l e : 
                                 o s . u n l i n k ( t e m p _ f i l e . n a m e ) 
                         
                         l o g g e r . i n f o ( f " T r a n s c r i b e d   a u d i o :   { t r a n s c r i p t i o n [ : 5 0 ] } { ' . . . '   i f   l e n ( t r a n s c r i p t i o n )   >   5 0   e l s e   ' ' } " ) 
                         r e t u r n   t r a n s c r i p t i o n 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   t r a n s c r i b i n g   a u d i o :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         r e t u r n   " " 
         
         d e f   s t r e a m _ t r a n s c r i b e ( s e l f ,   a u d i o _ s t r e a m ,   c h u n k _ d u r a t i o n _ m s :   i n t   =   1 0 0 0 , 
                                                   o p t i o n s :   O p t i o n a l [ D i c t [ s t r ,   A n y ] ]   =   N o n e )   - >   s t r : 
                 " " " 
                 T r a n s c r i b e   s t r e a m i n g   a u d i o   i n   c h u n k s . 
                 
                 A r g s : 
                         a u d i o _ s t r e a m :   A   s t r e a m   o f   a u d i o   d a t a 
                         c h u n k _ d u r a t i o n _ m s :   D u r a t i o n   o f   e a c h   c h u n k   i n   m i l l i s e c o n d s 
                         o p t i o n s :   A d d i t i o n a l   o p t i o n s   f o r   t h e   t r a n s c r i p t i o n 
                         
                 R e t u r n s : 
                         T r a n s c r i p t i o n   t e x t 
                 " " " 
                 #   N O T E :   T h i s   i s   a   s i m p l i f i e d   s t r e a m i n g   t r a n s c r i p t i o n   i m p l e m e n t a t i o n 
                 #   I n   a   p r o d u c t i o n   s y s t e m ,   t h i s   w o u l d   b e   m o r e   s o p h i s t i c a t e d ,   h a n d l i n g 
                 #   p a r t i a l   r e s u l t s ,   t i m e o u t s ,   e t c . 
                 t r y : 
                         #   E n s u r e   m o d e l   i s   l o a d e d 
                         s e l f . _ e n s u r e _ m o d e l _ l o a d e d ( ) 
                         
                         #   I n   a   r e a l   i m p l e m e n t a t i o n ,   w e   w o u l d   a c c u m u l a t e   a u d i o   a n d   t r a n s c r i b e   i n   c h u n k s 
                         #   F o r   n o w ,   w e ' l l   j u s t   a s s u m e   t h e   a u d i o _ s t r e a m   h a s   a   r e a d ( )   m e t h o d   t o   g e t   a l l   d a t a 
                         a u d i o _ d a t a   =   a u d i o _ s t r e a m . r e a d ( ) 
                         r e t u r n   s e l f . t r a n s c r i b e ( a u d i o _ d a t a ,   o p t i o n s ) 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   i n   s t r e a m i n g   t r a n s c r i p t i o n :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         r e t u r n   " " 