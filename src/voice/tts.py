" " " 
 T e x t - t o - S p e e c h   m o d u l e   u s i n g   S e s a m e   C S M . 
 C o n v e r t s   t e x t   t o   s p e e c h   w i t h   c o n f i g u r a b l e   v o i c e   m o d e l s . 
 " " " 
 i m p o r t   o s 
 i m p o r t   l o g g i n g 
 i m p o r t   t e m p f i l e 
 i m p o r t   y a m l 
 i m p o r t   j s o n 
 i m p o r t   s u b p r o c e s s 
 i m p o r t   r e q u e s t s 
 f r o m   t y p i n g   i m p o r t   O p t i o n a l ,   D i c t ,   A n y ,   U n i o n ,   T u p l e 
 
 l o g g e r   =   l o g g i n g . g e t L o g g e r ( _ _ n a m e _ _ ) 
 
 c l a s s   T e x t T o S p e e c h : 
         " " " 
         T e x t - t o - s p e e c h   c o n v e r s i o n   u s i n g   S e s a m e   C S M   o r   a l t e r n a t i v e   e n g i n e s . 
         " " " 
         
         d e f   _ _ i n i t _ _ ( s e l f ,   c o n f i g _ p a t h :   O p t i o n a l [ s t r ]   =   N o n e ) : 
                 " " " 
                 I n i t i a l i z e   t h e   T T S   e n g i n e   w i t h   c o n f i g u r a t i o n . 
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
                 s e l f . e n g i n e   =   " s e s a m e " 
                 s e l f . v o i c e   =   " d e f a u l t " 
                 s e l f . r a t e   =   1 . 0 
                 s e l f . p i t c h   =   1 . 0 
                 s e l f . a u d i o _ f o r m a t   =   " w a v " 
                 s e l f . a p i _ u r l   =   " h t t p : / / l o c a l h o s t : 8 0 8 0 / a p i / t t s " 
                 
                 #   L o a d   c o n f i g u r a t i o n 
                 s e l f . _ l o a d _ c o n f i g ( ) 
                 
                 #   C a c h e   f o r   v o i c e   m o d e l s 
                 s e l f . v o i c e _ m o d e l s   =   { } 
                 
                 l o g g e r . i n f o ( f " T T S   i n i t i a l i z e d   w i t h   e n g i n e :   { s e l f . e n g i n e } ,   v o i c e :   { s e l f . v o i c e } " ) 
         
         d e f   _ l o a d _ c o n f i g ( s e l f )   - >   N o n e : 
                 " " " 
                 L o a d   T T S   c o n f i g u r a t i o n   f r o m   Y A M L   f i l e . 
                 " " " 
                 t r y : 
                         w i t h   o p e n ( s e l f . c o n f i g _ p a t h ,   ' r ' )   a s   f : 
                                 c o n f i g   =   y a m l . s a f e _ l o a d ( f ) 
                         
                         i f   c o n f i g   a n d   ' v o i c e '   i n   c o n f i g   a n d   ' t t s '   i n   c o n f i g [ ' v o i c e ' ] : 
                                 t t s _ c o n f i g   =   c o n f i g [ ' v o i c e ' ] [ ' t t s ' ] 
                                 
                                 i f   ' e n g i n e '   i n   t t s _ c o n f i g : 
                                         s e l f . e n g i n e   =   t t s _ c o n f i g [ ' e n g i n e ' ] 
                                 
                                 i f   ' v o i c e '   i n   t t s _ c o n f i g : 
                                         s e l f . v o i c e   =   t t s _ c o n f i g [ ' v o i c e ' ] 
                                 
                                 i f   ' r a t e '   i n   t t s _ c o n f i g : 
                                         s e l f . r a t e   =   f l o a t ( t t s _ c o n f i g [ ' r a t e ' ] ) 
                                 
                                 i f   ' p i t c h '   i n   t t s _ c o n f i g : 
                                         s e l f . p i t c h   =   f l o a t ( t t s _ c o n f i g [ ' p i t c h ' ] ) 
                                 
                                 i f   ' a u d i o _ f o r m a t '   i n   t t s _ c o n f i g : 
                                         s e l f . a u d i o _ f o r m a t   =   t t s _ c o n f i g [ ' a u d i o _ f o r m a t ' ] 
                                 
                                 i f   ' a p i _ u r l '   i n   t t s _ c o n f i g : 
                                         s e l f . a p i _ u r l   =   t t s _ c o n f i g [ ' a p i _ u r l ' ] 
                                 
                         l o g g e r . i n f o ( f " L o a d e d   T T S   c o n f i g u r a t i o n   f r o m   { s e l f . c o n f i g _ p a t h } " ) 
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   l o a d i n g   c o n f i g u r a t i o n :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
         
         d e f   s y n t h e s i z e ( s e l f ,   t e x t :   s t r ,   v o i c e :   O p t i o n a l [ s t r ]   =   N o n e ,   
                                     o p t i o n s :   O p t i o n a l [ D i c t [ s t r ,   A n y ] ]   =   N o n e )   - >   b y t e s : 
                 " " " 
                 C o n v e r t   t e x t   t o   s p e e c h . 
                 
                 A r g s : 
                         t e x t :   T h e   t e x t   t o   c o n v e r t   t o   s p e e c h 
                         v o i c e :   O v e r r i d e   t h e   d e f a u l t   v o i c e 
                         o p t i o n s :   A d d i t i o n a l   o p t i o n s   f o r   s y n t h e s i s 
                         
                 R e t u r n s : 
                         A u d i o   d a t a   a s   b y t e s 
                 " " " 
                 i f   n o t   t e x t : 
                         l o g g e r . w a r n i n g ( " E m p t y   t e x t   p r o v i d e d   f o r   s y n t h e s i s ,   r e t u r n i n g   e m p t y   a u d i o " ) 
                         r e t u r n   b " " 
                 
                 #   S e l e c t   t h e   a p p r o p r i a t e   e n g i n e 
                 i f   s e l f . e n g i n e   = =   " s e s a m e " : 
                         r e t u r n   s e l f . _ s y n t h e s i z e _ s e s a m e ( t e x t ,   v o i c e ,   o p t i o n s ) 
                 e l i f   s e l f . e n g i n e   = =   " p y t t s x 3 " : 
                         r e t u r n   s e l f . _ s y n t h e s i z e _ p y t t s x 3 ( t e x t ,   v o i c e ,   o p t i o n s ) 
                 e l i f   s e l f . e n g i n e   = =   " a p i " : 
                         r e t u r n   s e l f . _ s y n t h e s i z e _ a p i ( t e x t ,   v o i c e ,   o p t i o n s ) 
                 e l s e : 
                         l o g g e r . e r r o r ( f " U n s u p p o r t e d   T T S   e n g i n e :   { s e l f . e n g i n e } " ) 
                         r e t u r n   b " " 
         
         d e f   _ s y n t h e s i z e _ s e s a m e ( s e l f ,   t e x t :   s t r ,   v o i c e :   O p t i o n a l [ s t r ]   =   N o n e ,   
                                                     o p t i o n s :   O p t i o n a l [ D i c t [ s t r ,   A n y ] ]   =   N o n e )   - >   b y t e s : 
                 " " " 
                 S y n t h e s i z e   s p e e c h   u s i n g   S e s a m e   C S M . 
                 
                 A r g s : 
                         t e x t :   T h e   t e x t   t o   c o n v e r t   t o   s p e e c h 
                         v o i c e :   O v e r r i d e   t h e   d e f a u l t   v o i c e 
                         o p t i o n s :   A d d i t i o n a l   o p t i o n s   f o r   s y n t h e s i s 
                         
                 R e t u r n s : 
                         A u d i o   d a t a   a s   b y t e s 
                 " " " 
                 t r y : 
                         #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   u s e   t h e   S e s a m e   C S M   A P I 
                         #   F o r   n o w ,   w e ' l l   s i m u l a t e   t h e   o u t p u t 
                         
                         v o i c e _ t o _ u s e   =   v o i c e   o r   s e l f . v o i c e 
                         l o g g e r . i n f o ( f " S y n t h e s i z i n g   w i t h   S e s a m e   C S M ,   v o i c e :   { v o i c e _ t o _ u s e } " ) 
                         
                         #   S i m u l a t e d   a u d i o   d a t a 
                         #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   b e   a c t u a l   a u d i o   d a t a   r e t u r n e d   f r o m   S e s a m e   C S M 
                         r e t u r n   b " S I M U L A T E D _ A U D I O _ D A T A _ F R O M _ S E S A M E " 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   i n   S e s a m e   s y n t h e s i s :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         r e t u r n   b " " 
         
         d e f   _ s y n t h e s i z e _ p y t t s x 3 ( s e l f ,   t e x t :   s t r ,   v o i c e :   O p t i o n a l [ s t r ]   =   N o n e ,   
                                                       o p t i o n s :   O p t i o n a l [ D i c t [ s t r ,   A n y ] ]   =   N o n e )   - >   b y t e s : 
                 " " " 
                 S y n t h e s i z e   s p e e c h   u s i n g   p y t t s x 3   ( o f f l i n e   T T S ) . 
                 
                 A r g s : 
                         t e x t :   T h e   t e x t   t o   c o n v e r t   t o   s p e e c h 
                         v o i c e :   O v e r r i d e   t h e   d e f a u l t   v o i c e 
                         o p t i o n s :   A d d i t i o n a l   o p t i o n s   f o r   s y n t h e s i s 
                         
                 R e t u r n s : 
                         A u d i o   d a t a   a s   b y t e s 
                 " " " 
                 t r y : 
                         #   T h i s   i s   a   p l a c e h o l d e r   f o r   t h e   p y t t s x 3   i m p l e m e n t a t i o n 
                         #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   u s e   p y t t s x 3   A P I 
                         i m p o r t   p y t t s x 3 
                         
                         v o i c e _ t o _ u s e   =   v o i c e   o r   s e l f . v o i c e 
                         l o g g e r . i n f o ( f " S y n t h e s i z i n g   w i t h   p y t t s x 3 ,   v o i c e :   { v o i c e _ t o _ u s e } " ) 
                         
                         #   C r e a t e   a   t e m p o r a r y   f i l e   f o r   t h e   a u d i o   o u t p u t 
                         w i t h   t e m p f i l e . N a m e d T e m p o r a r y F i l e ( s u f f i x = f " . { s e l f . a u d i o _ f o r m a t } " ,   d e l e t e = F a l s e )   a s   t e m p _ f i l e : 
                                 o u t p u t _ p a t h   =   t e m p _ f i l e . n a m e 
                         
                         #   I n i t i a l i z e   t h e   T T S   e n g i n e 
                         e n g i n e   =   p y t t s x 3 . i n i t ( ) 
                         
                         #   S e t   v o i c e   p r o p e r t i e s 
                         v o i c e s   =   e n g i n e . g e t P r o p e r t y ( ' v o i c e s ' ) 
                         f o r   v   i n   v o i c e s : 
                                 i f   v o i c e _ t o _ u s e   i n   v . i d   o r   v o i c e _ t o _ u s e   i n   v . n a m e : 
                                         e n g i n e . s e t P r o p e r t y ( ' v o i c e ' ,   v . i d ) 
                                         b r e a k 
                         
                         #   S e t   r a t e   a n d   p i t c h 
                         e n g i n e . s e t P r o p e r t y ( ' r a t e ' ,   i n t ( s e l f . r a t e   *   2 0 0 ) )     #   D e f a u l t   i s   2 0 0 
                         #   p y t t s x 3   d o e s n ' t   d i r e c t l y   s u p p o r t   p i t c h ,   w o u l d   n e e d   t o   u s e   a d d i t i o n a l   p r o c e s s i n g 
                         
                         #   S a v e   t o   f i l e 
                         e n g i n e . s a v e _ t o _ f i l e ( t e x t ,   o u t p u t _ p a t h ) 
                         e n g i n e . r u n A n d W a i t ( ) 
                         
                         #   R e a d   t h e   f i l e   b a c k   a s   b y t e s 
                         w i t h   o p e n ( o u t p u t _ p a t h ,   ' r b ' )   a s   f : 
                                 a u d i o _ d a t a   =   f . r e a d ( ) 
                         
                         #   C l e a n   u p 
                         o s . u n l i n k ( o u t p u t _ p a t h ) 
                         
                         r e t u r n   a u d i o _ d a t a 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   i n   p y t t s x 3   s y n t h e s i s :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         r e t u r n   b " " 
         
         d e f   _ s y n t h e s i z e _ a p i ( s e l f ,   t e x t :   s t r ,   v o i c e :   O p t i o n a l [ s t r ]   =   N o n e ,   
                                               o p t i o n s :   O p t i o n a l [ D i c t [ s t r ,   A n y ] ]   =   N o n e )   - >   b y t e s : 
                 " " " 
                 S y n t h e s i z e   s p e e c h   u s i n g   a n   e x t e r n a l   A P I . 
                 
                 A r g s : 
                         t e x t :   T h e   t e x t   t o   c o n v e r t   t o   s p e e c h 
                         v o i c e :   O v e r r i d e   t h e   d e f a u l t   v o i c e 
                         o p t i o n s :   A d d i t i o n a l   o p t i o n s   f o r   s y n t h e s i s 
                         
                 R e t u r n s : 
                         A u d i o   d a t a   a s   b y t e s 
                 " " " 
                 t r y : 
                         v o i c e _ t o _ u s e   =   v o i c e   o r   s e l f . v o i c e 
                         l o g g e r . i n f o ( f " S y n t h e s i z i n g   w i t h   A P I ,   v o i c e :   { v o i c e _ t o _ u s e } " ) 
                         
                         #   P r e p a r e   r e q u e s t   d a t a 
                         r e q u e s t _ d a t a   =   { 
                                 " t e x t " :   t e x t , 
                                 " v o i c e " :   v o i c e _ t o _ u s e , 
                                 " r a t e " :   s e l f . r a t e , 
                                 " p i t c h " :   s e l f . p i t c h , 
                                 " f o r m a t " :   s e l f . a u d i o _ f o r m a t 
                         } 
                         
                         #   A d d   a n y   a d d i t i o n a l   o p t i o n s 
                         i f   o p t i o n s : 
                                 r e q u e s t _ d a t a . u p d a t e ( o p t i o n s ) 
                         
                         #   M a k e   A P I   r e q u e s t 
                         r e s p o n s e   =   r e q u e s t s . p o s t ( 
                                 s e l f . a p i _ u r l , 
                                 j s o n = r e q u e s t _ d a t a , 
                                 h e a d e r s = { " C o n t e n t - T y p e " :   " a p p l i c a t i o n / j s o n " } , 
                                 t i m e o u t = 3 0 
                         ) 
                         
                         i f   r e s p o n s e . s t a t u s _ c o d e   = =   2 0 0 : 
                                 r e t u r n   r e s p o n s e . c o n t e n t 
                         e l s e : 
                                 l o g g e r . e r r o r ( f " A P I   r e q u e s t   f a i l e d :   { r e s p o n s e . s t a t u s _ c o d e }   -   { r e s p o n s e . t e x t } " ) 
                                 r e t u r n   b " " 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   i n   A P I   s y n t h e s i s :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         r e t u r n   b " " 
         
         d e f   g e t _ a v a i l a b l e _ v o i c e s ( s e l f )   - >   D i c t [ s t r ,   D i c t [ s t r ,   A n y ] ] : 
                 " " " 
                 G e t   a   l i s t   o f   a v a i l a b l e   v o i c e s . 
                 
                 R e t u r n s : 
                         D i c t i o n a r y   o f   a v a i l a b l e   v o i c e s   a n d   t h e i r   p r o p e r t i e s 
                 " " " 
                 a v a i l a b l e _ v o i c e s   =   { } 
                 
                 t r y : 
                         i f   s e l f . e n g i n e   = =   " s e s a m e " : 
                                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   r e t r i e v e   a v a i l a b l e   v o i c e s   f r o m   S e s a m e 
                                 a v a i l a b l e _ v o i c e s   =   { 
                                         " d e f a u l t " :   { " g e n d e r " :   " f e m a l e " ,   " l a n g u a g e " :   " e n - U S " } , 
                                         " m a l e 1 " :   { " g e n d e r " :   " m a l e " ,   " l a n g u a g e " :   " e n - U S " } , 
                                         " f e m a l e 1 " :   { " g e n d e r " :   " f e m a l e " ,   " l a n g u a g e " :   " e n - U S " } 
                                 } 
                         e l i f   s e l f . e n g i n e   = =   " p y t t s x 3 " : 
                                 i m p o r t   p y t t s x 3 
                                 e n g i n e   =   p y t t s x 3 . i n i t ( ) 
                                 f o r   v o i c e   i n   e n g i n e . g e t P r o p e r t y ( ' v o i c e s ' ) : 
                                         a v a i l a b l e _ v o i c e s [ v o i c e . i d ]   =   { 
                                                 " n a m e " :   v o i c e . n a m e , 
                                                 " l a n g u a g e " :   v o i c e . l a n g u a g e s [ 0 ]   i f   v o i c e . l a n g u a g e s   e l s e   " u n k n o w n " , 
                                                 " g e n d e r " :   " u n k n o w n " 
                                         } 
                         e l i f   s e l f . e n g i n e   = =   " a p i " : 
                                 #   G e t   v o i c e s   f r o m   A P I 
                                 r e s p o n s e   =   r e q u e s t s . g e t ( 
                                         f " { s e l f . a p i _ u r l } / v o i c e s " , 
                                         t i m e o u t = 1 0 
                                 ) 
                                 i f   r e s p o n s e . s t a t u s _ c o d e   = =   2 0 0 : 
                                         a v a i l a b l e _ v o i c e s   =   r e s p o n s e . j s o n ( ) 
                                 e l s e : 
                                         l o g g e r . e r r o r ( f " F a i l e d   t o   g e t   v o i c e s   f r o m   A P I :   { r e s p o n s e . s t a t u s _ c o d e } " ) 
                         
                         l o g g e r . i n f o ( f " R e t r i e v e d   { l e n ( a v a i l a b l e _ v o i c e s ) }   a v a i l a b l e   v o i c e s " ) 
                         r e t u r n   a v a i l a b l e _ v o i c e s 
                         
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   g e t t i n g   a v a i l a b l e   v o i c e s :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         r e t u r n   a v a i l a b l e _ v o i c e s 