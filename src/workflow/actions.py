" " " 
 W o r k f l o w   a c t i o n s   f o r   a u t o m a t i o n . 
 D e f i n e s   a c t i o n s   t h a t   c a n   b e   p e r f o r m e d   b a s e d   o n   c o n v e r s a t i o n   a n a l y s i s . 
 " " " 
 i m p o r t   o s 
 i m p o r t   l o g g i n g 
 i m p o r t   j s o n 
 i m p o r t   r e 
 i m p o r t   t i m e 
 i m p o r t   y a m l 
 i m p o r t   d a t e t i m e 
 f r o m   t y p i n g   i m p o r t   D i c t ,   L i s t ,   O p t i o n a l ,   A n y ,   U n i o n ,   T u p l e 
 
 l o g g e r   =   l o g g i n g . g e t L o g g e r ( _ _ n a m e _ _ ) 
 
 c l a s s   A c t i o n H a n d l e r : 
         " " " 
         H a n d l e s   e x t r a c t i n g   a n d   e x e c u t i n g   a c t i o n s   f r o m   L L M   r e s p o n s e s . 
         " " " 
         
         d e f   _ _ i n i t _ _ ( s e l f ,   c o n f i g _ p a t h :   O p t i o n a l [ s t r ]   =   N o n e ) : 
                 " " " 
                 I n i t i a l i z e   t h e   a c t i o n   h a n d l e r   w i t h   c o n f i g u r a t i o n . 
                 
                 A r g s : 
                         c o n f i g _ p a t h :   P a t h   t o   t h e   c o n f i g u r a t i o n   f i l e 
                 " " " 
                 s e l f . c o n f i g _ p a t h   =   c o n f i g _ p a t h   o r   o s . p a t h . j o i n ( 
                         o s . p a t h . d i r n a m e ( _ _ f i l e _ _ ) ,   
                         " . . / . . / c o n f i g / d e f a u l t . y m l " 
                 ) 
                 
                 #   L o a d   c o n f i g u r a t i o n 
                 s e l f . _ l o a d _ c o n f i g ( ) 
                 
                 #   I n i t i a l i z e   a c t i o n   r e g i s t r y 
                 s e l f . a c t i o n _ r e g i s t r y   =   { 
                         " s c h e d u l e _ a p p o i n t m e n t " :   s e l f . _ a c t i o n _ s c h e d u l e _ a p p o i n t m e n t , 
                         " c a n c e l _ a p p o i n t m e n t " :   s e l f . _ a c t i o n _ c a n c e l _ a p p o i n t m e n t , 
                         " t a k e _ m e s s a g e " :   s e l f . _ a c t i o n _ t a k e _ m e s s a g e , 
                         " t r a n s f e r _ c a l l " :   s e l f . _ a c t i o n _ t r a n s f e r _ c a l l , 
                         " l o o k u p _ i n f o " :   s e l f . _ a c t i o n _ l o o k u p _ i n f o , 
                         " s a v e _ c o n t a c t " :   s e l f . _ a c t i o n _ s a v e _ c o n t a c t , 
                         " s e t _ r e m i n d e r " :   s e l f . _ a c t i o n _ s e t _ r e m i n d e r , 
                         " s e n d _ e m a i l " :   s e l f . _ a c t i o n _ s e n d _ e m a i l , 
                         " s e n d _ s m s " :   s e l f . _ a c t i o n _ s e n d _ s m s 
                 } 
                 
                 l o g g e r . i n f o ( " A c t i o n   h a n d l e r   i n i t i a l i z e d " ) 
         
         d e f   _ l o a d _ c o n f i g ( s e l f )   - >   N o n e : 
                 " " " 
                 L o a d   c o n f i g u r a t i o n   f r o m   Y A M L   f i l e . 
                 " " " 
                 t r y : 
                         w i t h   o p e n ( s e l f . c o n f i g _ p a t h ,   ' r ' )   a s   f : 
                                 c o n f i g   =   y a m l . s a f e _ l o a d ( f ) 
                         
                         #   A n y   s p e c i f i c   c o n f i g u r a t i o n   c a n   b e   l o a d e d   h e r e 
                         s e l f . c o n f i g   =   c o n f i g . g e t ( ' w o r k f l o w ' ,   { } ) . g e t ( ' a c t i o n s ' ,   { } ) 
                         
                         l o g g e r . i n f o ( f " L o a d e d   a c t i o n   c o n f i g u r a t i o n   f r o m   { s e l f . c o n f i g _ p a t h } " ) 
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   l o a d i n g   c o n f i g u r a t i o n :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         s e l f . c o n f i g   =   { } 
         
         d e f   e x t r a c t _ a c t i o n s ( s e l f ,   t e x t :   s t r )   - >   L i s t [ D i c t [ s t r ,   A n y ] ] : 
                 " " " 
                 E x t r a c t   a c t i o n s   f r o m   t e x t . 
                 
                 A r g s : 
                         t e x t :   T e x t   t o   e x t r a c t   a c t i o n s   f r o m   ( t y p i c a l l y   L L M   r e s p o n s e ) 
                         
                 R e t u r n s : 
                         L i s t   o f   a c t i o n   d i c t i o n a r i e s   w i t h   ' t y p e '   a n d   ' p a r a m s '   k e y s 
                 " " " 
                 a c t i o n s   =   [ ] 
                 
                 #   L o o k   f o r   p a t t e r n s   l i k e   [ A C T I O N : a c t i o n _ t y p e { p a r a m 1 : v a l u e 1 , p a r a m 2 : v a l u e 2 } ] 
                 a c t i o n _ p a t t e r n   =   r ' \ [ A C T I O N : ( \ w + ) \ { ( [ ^ } ] * ) \ } \ ] ' 
                 m a t c h e s   =   r e . f i n d i t e r ( a c t i o n _ p a t t e r n ,   t e x t ) 
                 
                 f o r   m a t c h   i n   m a t c h e s : 
                         a c t i o n _ t y p e   =   m a t c h . g r o u p ( 1 ) 
                         p a r a m s _ s t r   =   m a t c h . g r o u p ( 2 ) 
                         
                         #   P a r s e   p a r a m e t e r s 
                         p a r a m s   =   { } 
                         f o r   p a r a m   i n   p a r a m s _ s t r . s p l i t ( ' , ' ) : 
                                 i f   ' : '   i n   p a r a m : 
                                         k e y ,   v a l u e   =   p a r a m . s p l i t ( ' : ' ,   1 ) 
                                         p a r a m s [ k e y . s t r i p ( ) ]   =   v a l u e . s t r i p ( ) 
                         
                         a c t i o n s . a p p e n d ( { 
                                 ' t y p e ' :   a c t i o n _ t y p e , 
                                 ' p a r a m s ' :   p a r a m s 
                         } ) 
                 
                 #   A l s o   l o o k   f o r   J S O N - l i k e   a c t i o n   b l o c k s 
                 j s o n _ p a t t e r n   =   r ' ` ` ` a c t i o n \ s * \ n ( . * ? ) \ n ` ` ` ' 
                 m a t c h e s   =   r e . f i n d i t e r ( j s o n _ p a t t e r n ,   t e x t ,   r e . D O T A L L ) 
                 
                 f o r   m a t c h   i n   m a t c h e s : 
                         t r y : 
                                 a c t i o n _ j s o n   =   j s o n . l o a d s ( m a t c h . g r o u p ( 1 ) ) 
                                 i f   i s i n s t a n c e ( a c t i o n _ j s o n ,   d i c t )   a n d   ' t y p e '   i n   a c t i o n _ j s o n : 
                                         a c t i o n s . a p p e n d ( a c t i o n _ j s o n ) 
                         e x c e p t   j s o n . J S O N D e c o d e E r r o r : 
                                 l o g g e r . w a r n i n g ( f " C o u l d   n o t   p a r s e   a c t i o n   J S O N :   { m a t c h . g r o u p ( 1 ) } " ) 
                 
                 l o g g e r . i n f o ( f " E x t r a c t e d   { l e n ( a c t i o n s ) }   a c t i o n s   f r o m   t e x t " ) 
                 r e t u r n   a c t i o n s 
         
         d e f   e x e c u t e _ a c t i o n ( s e l f ,   a c t i o n :   D i c t [ s t r ,   A n y ] )   - >   A n y : 
                 " " " 
                 E x e c u t e   a n   a c t i o n . 
                 
                 A r g s : 
                         a c t i o n :   A c t i o n   d i c t i o n a r y   w i t h   ' t y p e '   a n d   ' p a r a m s '   k e y s 
                         
                 R e t u r n s : 
                         R e s u l t   o f   t h e   a c t i o n   e x e c u t i o n 
                 " " " 
                 a c t i o n _ t y p e   =   a c t i o n . g e t ( ' t y p e ' ) 
                 p a r a m s   =   a c t i o n . g e t ( ' p a r a m s ' ,   { } ) 
                 
                 i f   a c t i o n _ t y p e   n o t   i n   s e l f . a c t i o n _ r e g i s t r y : 
                         l o g g e r . w a r n i n g ( f " U n k n o w n   a c t i o n   t y p e :   { a c t i o n _ t y p e } " ) 
                         r e t u r n   { " e r r o r " :   f " U n k n o w n   a c t i o n   t y p e :   { a c t i o n _ t y p e } " } 
                 
                 t r y : 
                         l o g g e r . i n f o ( f " E x e c u t i n g   a c t i o n :   { a c t i o n _ t y p e } " ) 
                         r e s u l t   =   s e l f . a c t i o n _ r e g i s t r y [ a c t i o n _ t y p e ] ( p a r a m s ) 
                         l o g g e r . i n f o ( f " A c t i o n   { a c t i o n _ t y p e }   e x e c u t e d   s u c c e s s f u l l y " ) 
                         r e t u r n   r e s u l t 
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   e x e c u t i n g   a c t i o n   { a c t i o n _ t y p e } :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
                         r e t u r n   { " e r r o r " :   s t r ( e ) } 
         
         d e f   _ a c t i o n _ s c h e d u l e _ a p p o i n t m e n t ( s e l f ,   p a r a m s :   D i c t [ s t r ,   A n y ] )   - >   D i c t [ s t r ,   A n y ] : 
                 " " " 
                 S c h e d u l e   a n   a p p o i n t m e n t . 
                 
                 A r g s : 
                         p a r a m s :   P a r a m e t e r s   f o r   t h e   a c t i o n 
                         
                 R e t u r n s : 
                         R e s u l t   o f   t h e   a c t i o n 
                 " " " 
                 r e q u i r e d _ p a r a m s   =   [ ' d a t e ' ,   ' t i m e ' ,   ' d u r a t i o n ' ] 
                 f o r   p a r a m   i n   r e q u i r e d _ p a r a m s : 
                         i f   p a r a m   n o t   i n   p a r a m s : 
                                 r a i s e   V a l u e E r r o r ( f " M i s s i n g   r e q u i r e d   p a r a m e t e r :   { p a r a m } " ) 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   i n t e r f a c e   w i t h   a   c a l e n d a r   s y s t e m 
                 #   F o r   n o w ,   w e ' l l   j u s t   s i m u l a t e   t h e   a p p o i n t m e n t   c r e a t i o n 
                 a p p o i n t m e n t _ i d   =   f " a p t _ { i n t ( t i m e . t i m e ( ) ) } " 
                 
                 #   F o r m a t   d a t e   a n d   t i m e 
                 t r y : 
                         d a t e _ o b j   =   d a t e t i m e . d a t e t i m e . s t r p t i m e ( p a r a m s [ ' d a t e ' ] ,   ' % Y - % m - % d ' ) 
                         f o r m a t t e d _ d a t e   =   d a t e _ o b j . s t r f t i m e ( ' % A ,   % B   % d ,   % Y ' ) 
                 e x c e p t   V a l u e E r r o r : 
                         f o r m a t t e d _ d a t e   =   p a r a m s [ ' d a t e ' ]     #   U s e   a s - i s   i f   n o t   i n   e x p e c t e d   f o r m a t 
                 
                 a p p o i n t m e n t   =   { 
                         ' i d ' :   a p p o i n t m e n t _ i d , 
                         ' d a t e ' :   p a r a m s [ ' d a t e ' ] , 
                         ' f o r m a t t e d _ d a t e ' :   f o r m a t t e d _ d a t e , 
                         ' t i m e ' :   p a r a m s [ ' t i m e ' ] , 
                         ' d u r a t i o n ' :   p a r a m s [ ' d u r a t i o n ' ] , 
                         ' n a m e ' :   p a r a m s . g e t ( ' n a m e ' ,   ' U n k n o w n ' ) , 
                         ' p h o n e ' :   p a r a m s . g e t ( ' p h o n e ' ,   ' U n k n o w n ' ) , 
                         ' p u r p o s e ' :   p a r a m s . g e t ( ' p u r p o s e ' ,   ' ' ) , 
                         ' n o t e s ' :   p a r a m s . g e t ( ' n o t e s ' ,   ' ' ) , 
                         ' s t a t u s ' :   ' s c h e d u l e d ' , 
                         ' c r e a t e d _ a t ' :   t i m e . t i m e ( ) 
                 } 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   s a v e   t o   d a t a b a s e 
                 l o g g e r . i n f o ( f " S c h e d u l e d   a p p o i n t m e n t :   { a p p o i n t m e n t _ i d } " ) 
                 
                 r e t u r n   { 
                         ' s u c c e s s ' :   T r u e , 
                         ' a p p o i n t m e n t _ i d ' :   a p p o i n t m e n t _ i d , 
                         ' d e t a i l s ' :   a p p o i n t m e n t , 
                         ' m e s s a g e ' :   f " A p p o i n t m e n t   s c h e d u l e d   f o r   { f o r m a t t e d _ d a t e }   a t   { p a r a m s [ ' t i m e ' ] }   f o r   { p a r a m s [ ' d u r a t i o n ' ] }   m i n u t e s . " 
                 } 
         
         d e f   _ a c t i o n _ c a n c e l _ a p p o i n t m e n t ( s e l f ,   p a r a m s :   D i c t [ s t r ,   A n y ] )   - >   D i c t [ s t r ,   A n y ] : 
                 " " " 
                 C a n c e l   a n   a p p o i n t m e n t . 
                 
                 A r g s : 
                         p a r a m s :   P a r a m e t e r s   f o r   t h e   a c t i o n 
                         
                 R e t u r n s : 
                         R e s u l t   o f   t h e   a c t i o n 
                 " " " 
                 i f   ' a p p o i n t m e n t _ i d '   n o t   i n   p a r a m s   a n d   ' d a t e '   n o t   i n   p a r a m s : 
                         r a i s e   V a l u e E r r o r ( " M i s s i n g   r e q u i r e d   p a r a m e t e r :   e i t h e r   a p p o i n t m e n t _ i d   o r   d a t e   i s   r e q u i r e d " ) 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   i n t e r f a c e   w i t h   a   c a l e n d a r   s y s t e m 
                 #   F o r   n o w ,   w e ' l l   j u s t   s i m u l a t e   t h e   a p p o i n t m e n t   c a n c e l l a t i o n 
                 a p p o i n t m e n t _ i d   =   p a r a m s . g e t ( ' a p p o i n t m e n t _ i d ' ,   f " a p t _ { p a r a m s . g e t ( ' d a t e ' ) } " ) 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   c h e c k   i f   a p p o i n t m e n t   e x i s t s 
                 a p p o i n t m e n t _ e x i s t s   =   T r u e     #   S i m u l a t e d 
                 
                 i f   n o t   a p p o i n t m e n t _ e x i s t s : 
                         r e t u r n   { 
                                 ' s u c c e s s ' :   F a l s e , 
                                 ' m e s s a g e ' :   f " A p p o i n t m e n t   { a p p o i n t m e n t _ i d }   n o t   f o u n d . " 
                         } 
                 
                 l o g g e r . i n f o ( f " C a n c e l l e d   a p p o i n t m e n t :   { a p p o i n t m e n t _ i d } " ) 
                 
                 r e t u r n   { 
                         ' s u c c e s s ' :   T r u e , 
                         ' a p p o i n t m e n t _ i d ' :   a p p o i n t m e n t _ i d , 
                         ' m e s s a g e ' :   f " A p p o i n t m e n t   { a p p o i n t m e n t _ i d }   h a s   b e e n   c a n c e l l e d . " 
                 } 
         
         d e f   _ a c t i o n _ t a k e _ m e s s a g e ( s e l f ,   p a r a m s :   D i c t [ s t r ,   A n y ] )   - >   D i c t [ s t r ,   A n y ] : 
                 " " " 
                 T a k e   a   m e s s a g e . 
                 
                 A r g s : 
                         p a r a m s :   P a r a m e t e r s   f o r   t h e   a c t i o n 
                         
                 R e t u r n s : 
                         R e s u l t   o f   t h e   a c t i o n 
                 " " " 
                 r e q u i r e d _ p a r a m s   =   [ ' m e s s a g e ' ] 
                 f o r   p a r a m   i n   r e q u i r e d _ p a r a m s : 
                         i f   p a r a m   n o t   i n   p a r a m s : 
                                 r a i s e   V a l u e E r r o r ( f " M i s s i n g   r e q u i r e d   p a r a m e t e r :   { p a r a m } " ) 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   s a v e   t o   a   d a t a b a s e   o r   s e n d   n o t i f i c a t i o n s 
                 m e s s a g e _ i d   =   f " m s g _ { i n t ( t i m e . t i m e ( ) ) } " 
                 
                 m e s s a g e   =   { 
                         ' i d ' :   m e s s a g e _ i d , 
                         ' c a l l e r _ n a m e ' :   p a r a m s . g e t ( ' c a l l e r _ n a m e ' ,   ' U n k n o w n ' ) , 
                         ' c a l l e r _ n u m b e r ' :   p a r a m s . g e t ( ' c a l l e r _ n u m b e r ' ,   ' U n k n o w n ' ) , 
                         ' m e s s a g e ' :   p a r a m s [ ' m e s s a g e ' ] , 
                         ' u r g e n c y ' :   p a r a m s . g e t ( ' u r g e n c y ' ,   ' n o r m a l ' ) , 
                         ' c a l l b a c k _ r e q u e s t e d ' :   p a r a m s . g e t ( ' c a l l b a c k _ r e q u e s t e d ' ,   F a l s e ) , 
                         ' t i m e s t a m p ' :   t i m e . t i m e ( ) 
                 } 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   s a v e   t o   d a t a b a s e   o r   s e n d   n o t i f i c a t i o n 
                 l o g g e r . i n f o ( f " T o o k   m e s s a g e :   { m e s s a g e _ i d } " ) 
                 
                 r e t u r n   { 
                         ' s u c c e s s ' :   T r u e , 
                         ' m e s s a g e _ i d ' :   m e s s a g e _ i d , 
                         ' d e t a i l s ' :   m e s s a g e , 
                         ' m e s s a g e ' :   f " M e s s a g e   r e c o r d e d .   I D :   { m e s s a g e _ i d } " 
                 } 
         
         d e f   _ a c t i o n _ t r a n s f e r _ c a l l ( s e l f ,   p a r a m s :   D i c t [ s t r ,   A n y ] )   - >   D i c t [ s t r ,   A n y ] : 
                 " " " 
                 T r a n s f e r   a   c a l l . 
                 
                 A r g s : 
                         p a r a m s :   P a r a m e t e r s   f o r   t h e   a c t i o n 
                         
                 R e t u r n s : 
                         R e s u l t   o f   t h e   a c t i o n 
                 " " " 
                 i f   ' d e s t i n a t i o n '   n o t   i n   p a r a m s : 
                         r a i s e   V a l u e E r r o r ( " M i s s i n g   r e q u i r e d   p a r a m e t e r :   d e s t i n a t i o n " ) 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   i n t e r f a c e   w i t h   t h e   t e l e p h o n y   s y s t e m 
                 d e s t i n a t i o n   =   p a r a m s [ ' d e s t i n a t i o n ' ] 
                 t r a n s f e r _ t y p e   =   p a r a m s . g e t ( ' t r a n s f e r _ t y p e ' ,   ' w a r m ' )     #   w a r m   o r   c o l d 
                 
                 #   S i m u l a t e   t h e   t r a n s f e r 
                 l o g g e r . i n f o ( f " T r a n s f e r r i n g   c a l l   t o   { d e s t i n a t i o n }   ( { t r a n s f e r _ t y p e }   t r a n s f e r ) " ) 
                 
                 r e t u r n   { 
                         ' s u c c e s s ' :   T r u e , 
                         ' d e s t i n a t i o n ' :   d e s t i n a t i o n , 
                         ' t r a n s f e r _ t y p e ' :   t r a n s f e r _ t y p e , 
                         ' m e s s a g e ' :   f " C a l l   t r a n s f e r r e d   t o   { d e s t i n a t i o n } . " 
                 } 
         
         d e f   _ a c t i o n _ l o o k u p _ i n f o ( s e l f ,   p a r a m s :   D i c t [ s t r ,   A n y ] )   - >   D i c t [ s t r ,   A n y ] : 
                 " " " 
                 L o o k   u p   i n f o r m a t i o n . 
                 
                 A r g s : 
                         p a r a m s :   P a r a m e t e r s   f o r   t h e   a c t i o n 
                         
                 R e t u r n s : 
                         R e s u l t   o f   t h e   a c t i o n 
                 " " " 
                 i f   ' q u e r y '   n o t   i n   p a r a m s : 
                         r a i s e   V a l u e E r r o r ( " M i s s i n g   r e q u i r e d   p a r a m e t e r :   q u e r y " ) 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   s e a r c h   a   k n o w l e d g e   b a s e   o r   C R M 
                 q u e r y   =   p a r a m s [ ' q u e r y ' ] 
                 c a t e g o r y   =   p a r a m s . g e t ( ' c a t e g o r y ' ,   ' g e n e r a l ' ) 
                 
                 #   S i m u l a t e   i n f o r m a t i o n   l o o k u p 
                 r e s u l t   =   { 
                         ' q u e r y ' :   q u e r y , 
                         ' c a t e g o r y ' :   c a t e g o r y , 
                         ' t i m e s t a m p ' :   t i m e . t i m e ( ) 
                 } 
                 
                 #   D u m m y   r e s p o n s e s   b a s e d   o n   c a t e g o r i e s 
                 i f   c a t e g o r y   = =   ' h o u r s ' : 
                         r e s u l t [ ' i n f o ' ]   =   " M o n d a y - F r i d a y :   9   A M   -   5   P M ,   S a t u r d a y :   1 0   A M   -   2   P M ,   S u n d a y :   C l o s e d " 
                 e l i f   c a t e g o r y   = =   ' l o c a t i o n ' : 
                         r e s u l t [ ' i n f o ' ]   =   " 1 2 3   M a i n   S t r e e t ,   A n y t o w n ,   U S A   1 2 3 4 5 " 
                 e l i f   c a t e g o r y   = =   ' c o n t a c t ' : 
                         r e s u l t [ ' i n f o ' ]   =   " P h o n e :   ( 5 5 5 )   1 2 3 - 4 5 6 7 ,   E m a i l :   i n f o @ e x a m p l e . c o m " 
                 e l s e : 
                         r e s u l t [ ' i n f o ' ]   =   " N o   s p e c i f i c   i n f o r m a t i o n   f o u n d   f o r   t h i s   q u e r y . " 
                 
                 l o g g e r . i n f o ( f " L o o k e d   u p   i n f o r m a t i o n :   { q u e r y }   ( { c a t e g o r y } ) " ) 
                 
                 r e t u r n   { 
                         ' s u c c e s s ' :   T r u e , 
                         ' d e t a i l s ' :   r e s u l t , 
                         ' m e s s a g e ' :   f " I n f o r m a t i o n   l o o k u p   f o r   ' { q u e r y } '   c o m p l e t e . " 
                 } 
         
         d e f   _ a c t i o n _ s a v e _ c o n t a c t ( s e l f ,   p a r a m s :   D i c t [ s t r ,   A n y ] )   - >   D i c t [ s t r ,   A n y ] : 
                 " " " 
                 S a v e   c o n t a c t   i n f o r m a t i o n . 
                 
                 A r g s : 
                         p a r a m s :   P a r a m e t e r s   f o r   t h e   a c t i o n 
                         
                 R e t u r n s : 
                         R e s u l t   o f   t h e   a c t i o n 
                 " " " 
                 r e q u i r e d _ p a r a m s   =   [ ' n a m e ' ] 
                 f o r   p a r a m   i n   r e q u i r e d _ p a r a m s : 
                         i f   p a r a m   n o t   i n   p a r a m s : 
                                 r a i s e   V a l u e E r r o r ( f " M i s s i n g   r e q u i r e d   p a r a m e t e r :   { p a r a m } " ) 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   s a v e   t o   a   C R M   o r   c o n t a c t s   d a t a b a s e 
                 c o n t a c t _ i d   =   f " c o n t a c t _ { i n t ( t i m e . t i m e ( ) ) } " 
                 
                 c o n t a c t   =   { 
                         ' i d ' :   c o n t a c t _ i d , 
                         ' n a m e ' :   p a r a m s [ ' n a m e ' ] , 
                         ' p h o n e ' :   p a r a m s . g e t ( ' p h o n e ' ,   ' ' ) , 
                         ' e m a i l ' :   p a r a m s . g e t ( ' e m a i l ' ,   ' ' ) , 
                         ' c o m p a n y ' :   p a r a m s . g e t ( ' c o m p a n y ' ,   ' ' ) , 
                         ' n o t e s ' :   p a r a m s . g e t ( ' n o t e s ' ,   ' ' ) , 
                         ' c r e a t e d _ a t ' :   t i m e . t i m e ( ) 
                 } 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   s a v e   t o   d a t a b a s e 
                 l o g g e r . i n f o ( f " S a v e d   c o n t a c t :   { c o n t a c t _ i d }   ( { p a r a m s [ ' n a m e ' ] } ) " ) 
                 
                 r e t u r n   { 
                         ' s u c c e s s ' :   T r u e , 
                         ' c o n t a c t _ i d ' :   c o n t a c t _ i d , 
                         ' d e t a i l s ' :   c o n t a c t , 
                         ' m e s s a g e ' :   f " C o n t a c t   i n f o r m a t i o n   f o r   { p a r a m s [ ' n a m e ' ] }   s a v e d . " 
                 } 
         
         d e f   _ a c t i o n _ s e t _ r e m i n d e r ( s e l f ,   p a r a m s :   D i c t [ s t r ,   A n y ] )   - >   D i c t [ s t r ,   A n y ] : 
                 " " " 
                 S e t   a   r e m i n d e r . 
                 
                 A r g s : 
                         p a r a m s :   P a r a m e t e r s   f o r   t h e   a c t i o n 
                         
                 R e t u r n s : 
                         R e s u l t   o f   t h e   a c t i o n 
                 " " " 
                 r e q u i r e d _ p a r a m s   =   [ ' d a t e ' ,   ' t i m e ' ,   ' d e s c r i p t i o n ' ] 
                 f o r   p a r a m   i n   r e q u i r e d _ p a r a m s : 
                         i f   p a r a m   n o t   i n   p a r a m s : 
                                 r a i s e   V a l u e E r r o r ( f " M i s s i n g   r e q u i r e d   p a r a m e t e r :   { p a r a m } " ) 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   i n t e r f a c e   w i t h   a   c a l e n d a r   o r   t a s k   s y s t e m 
                 r e m i n d e r _ i d   =   f " r e m i n d e r _ { i n t ( t i m e . t i m e ( ) ) } " 
                 
                 r e m i n d e r   =   { 
                         ' i d ' :   r e m i n d e r _ i d , 
                         ' d a t e ' :   p a r a m s [ ' d a t e ' ] , 
                         ' t i m e ' :   p a r a m s [ ' t i m e ' ] , 
                         ' d e s c r i p t i o n ' :   p a r a m s [ ' d e s c r i p t i o n ' ] , 
                         ' f o r _ u s e r ' :   p a r a m s . g e t ( ' f o r _ u s e r ' ,   ' s t a f f ' ) , 
                         ' p r i o r i t y ' :   p a r a m s . g e t ( ' p r i o r i t y ' ,   ' n o r m a l ' ) , 
                         ' c r e a t e d _ a t ' :   t i m e . t i m e ( ) 
                 } 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   s a v e   t o   d a t a b a s e   o r   c a l e n d a r 
                 l o g g e r . i n f o ( f " S e t   r e m i n d e r :   { r e m i n d e r _ i d } " ) 
                 
                 r e t u r n   { 
                         ' s u c c e s s ' :   T r u e , 
                         ' r e m i n d e r _ i d ' :   r e m i n d e r _ i d , 
                         ' d e t a i l s ' :   r e m i n d e r , 
                         ' m e s s a g e ' :   f " R e m i n d e r   s e t   f o r   { p a r a m s [ ' d a t e ' ] }   a t   { p a r a m s [ ' t i m e ' ] } . " 
                 } 
         
         d e f   _ a c t i o n _ s e n d _ e m a i l ( s e l f ,   p a r a m s :   D i c t [ s t r ,   A n y ] )   - >   D i c t [ s t r ,   A n y ] : 
                 " " " 
                 S e n d   a n   e m a i l . 
                 
                 A r g s : 
                         p a r a m s :   P a r a m e t e r s   f o r   t h e   a c t i o n 
                         
                 R e t u r n s : 
                         R e s u l t   o f   t h e   a c t i o n 
                 " " " 
                 r e q u i r e d _ p a r a m s   =   [ ' t o ' ,   ' s u b j e c t ' ,   ' b o d y ' ] 
                 f o r   p a r a m   i n   r e q u i r e d _ p a r a m s : 
                         i f   p a r a m   n o t   i n   p a r a m s : 
                                 r a i s e   V a l u e E r r o r ( f " M i s s i n g   r e q u i r e d   p a r a m e t e r :   { p a r a m } " ) 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   u s e   a n   e m a i l   s e r v i c e 
                 e m a i l _ i d   =   f " e m a i l _ { i n t ( t i m e . t i m e ( ) ) } " 
                 
                 e m a i l   =   { 
                         ' i d ' :   e m a i l _ i d , 
                         ' t o ' :   p a r a m s [ ' t o ' ] , 
                         ' s u b j e c t ' :   p a r a m s [ ' s u b j e c t ' ] , 
                         ' b o d y ' :   p a r a m s [ ' b o d y ' ] , 
                         ' c c ' :   p a r a m s . g e t ( ' c c ' ,   ' ' ) , 
                         ' b c c ' :   p a r a m s . g e t ( ' b c c ' ,   ' ' ) , 
                         ' f r o m ' :   p a r a m s . g e t ( ' f r o m ' ,   ' s y s t e m @ e x a m p l e . c o m ' ) , 
                         ' t i m e s t a m p ' :   t i m e . t i m e ( ) 
                 } 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   s e n d   v i a   e m a i l   A P I 
                 l o g g e r . i n f o ( f " S e n t   e m a i l :   { e m a i l _ i d }   t o   { p a r a m s [ ' t o ' ] } " ) 
                 
                 r e t u r n   { 
                         ' s u c c e s s ' :   T r u e , 
                         ' e m a i l _ i d ' :   e m a i l _ i d , 
                         ' d e t a i l s ' :   e m a i l , 
                         ' m e s s a g e ' :   f " E m a i l   s e n t   t o   { p a r a m s [ ' t o ' ] }   w i t h   s u b j e c t   ' { p a r a m s [ ' s u b j e c t ' ] } ' . " 
                 } 
         
         d e f   _ a c t i o n _ s e n d _ s m s ( s e l f ,   p a r a m s :   D i c t [ s t r ,   A n y ] )   - >   D i c t [ s t r ,   A n y ] : 
                 " " " 
                 S e n d   a n   S M S . 
                 
                 A r g s : 
                         p a r a m s :   P a r a m e t e r s   f o r   t h e   a c t i o n 
                         
                 R e t u r n s : 
                         R e s u l t   o f   t h e   a c t i o n 
                 " " " 
                 r e q u i r e d _ p a r a m s   =   [ ' t o ' ,   ' m e s s a g e ' ] 
                 f o r   p a r a m   i n   r e q u i r e d _ p a r a m s : 
                         i f   p a r a m   n o t   i n   p a r a m s : 
                                 r a i s e   V a l u e E r r o r ( f " M i s s i n g   r e q u i r e d   p a r a m e t e r :   { p a r a m } " ) 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   u s e   a n   S M S   s e r v i c e 
                 s m s _ i d   =   f " s m s _ { i n t ( t i m e . t i m e ( ) ) } " 
                 
                 s m s   =   { 
                         ' i d ' :   s m s _ i d , 
                         ' t o ' :   p a r a m s [ ' t o ' ] , 
                         ' m e s s a g e ' :   p a r a m s [ ' m e s s a g e ' ] , 
                         ' f r o m ' :   p a r a m s . g e t ( ' f r o m ' ,   ' s y s t e m ' ) , 
                         ' t i m e s t a m p ' :   t i m e . t i m e ( ) 
                 } 
                 
                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   s e n d   v i a   S M S   A P I 
                 l o g g e r . i n f o ( f " S e n t   S M S :   { s m s _ i d }   t o   { p a r a m s [ ' t o ' ] } " ) 
                 
                 r e t u r n   { 
                         ' s u c c e s s ' :   T r u e , 
                         ' s m s _ i d ' :   s m s _ i d , 
                         ' d e t a i l s ' :   s m s , 
                         ' m e s s a g e ' :   f " S M S   s e n t   t o   { p a r a m s [ ' t o ' ] } . " 
                 } 
 
 
 c l a s s   A c t i o n E x e c u t o r : 
         " " " 
         R e s p o n s i b l e   f o r   e x e c u t i n g   a c t i o n   s e q u e n c e s   b a s e d   o n   c o n v e r s a t i o n   a n a l y s i s . 
         " " " 
         
         d e f   _ _ i n i t _ _ ( s e l f ,   h a n d l e r :   O p t i o n a l [ A c t i o n H a n d l e r ]   =   N o n e ) : 
                 " " " 
                 I n i t i a l i z e   t h e   a c t i o n   e x e c u t o r . 
                 
                 A r g s : 
                         h a n d l e r :   A c t i o n   h a n d l e r   i n s t a n c e 
                 " " " 
                 s e l f . h a n d l e r   =   h a n d l e r   o r   A c t i o n H a n d l e r ( ) 
                 s e l f . e x e c u t e d _ a c t i o n s   =   [ ] 
                 
                 l o g g e r . i n f o ( " A c t i o n   e x e c u t o r   i n i t i a l i z e d " ) 
         
         d e f   e x e c u t e _ a c t i o n s ( s e l f ,   a c t i o n s :   L i s t [ D i c t [ s t r ,   A n y ] ] )   - >   L i s t [ D i c t [ s t r ,   A n y ] ] : 
                 " " " 
                 E x e c u t e   a   s e q u e n c e   o f   a c t i o n s . 
                 
                 A r g s : 
                         a c t i o n s :   L i s t   o f   a c t i o n   d i c t i o n a r i e s 
                         
                 R e t u r n s : 
                         L i s t   o f   a c t i o n   r e s u l t s 
                 " " " 
                 r e s u l t s   =   [ ] 
                 
                 f o r   a c t i o n   i n   a c t i o n s : 
                         r e s u l t   =   s e l f . h a n d l e r . e x e c u t e _ a c t i o n ( a c t i o n ) 
                         r e s u l t s . a p p e n d ( r e s u l t ) 
                         
                         #   R e c o r d   t h e   e x e c u t e d   a c t i o n   a n d   i t s   r e s u l t 
                         s e l f . e x e c u t e d _ a c t i o n s . a p p e n d ( { 
                                 ' a c t i o n ' :   a c t i o n , 
                                 ' r e s u l t ' :   r e s u l t , 
                                 ' t i m e s t a m p ' :   t i m e . t i m e ( ) 
                         } ) 
                 
                 r e t u r n   r e s u l t s 
         
         d e f   g e t _ e x e c u t e d _ a c t i o n s ( s e l f )   - >   L i s t [ D i c t [ s t r ,   A n y ] ] : 
                 " " " 
                 G e t   t h e   l i s t   o f   e x e c u t e d   a c t i o n s . 
                 
                 R e t u r n s : 
                         L i s t   o f   e x e c u t e d   a c t i o n s   w i t h   r e s u l t s 
                 " " " 
                 r e t u r n   s e l f . e x e c u t e d _ a c t i o n s 
         
         d e f   c l e a r _ e x e c u t e d _ a c t i o n s ( s e l f )   - >   N o n e : 
                 " " " 
                 C l e a r   t h e   l i s t   o f   e x e c u t e d   a c t i o n s . 
                 " " " 
                 s e l f . e x e c u t e d _ a c t i o n s   =   [ ] 
                 l o g g e r . i n f o ( " C l e a r e d   e x e c u t e d   a c t i o n s   h i s t o r y " ) 
 
 
 #   A c t i o n   e x t r a c t i o n   u t i l i t y   f u n c t i o n s 
 
 d e f   e x t r a c t _ e n t i t i e s _ f r o m _ t e x t ( t e x t :   s t r )   - >   D i c t [ s t r ,   A n y ] : 
         " " " 
         E x t r a c t   e n t i t i e s   f r o m   t e x t   u s i n g   p a t t e r n   m a t c h i n g . 
         
         A r g s : 
                 t e x t :   T e x t   t o   e x t r a c t   e n t i t i e s   f r o m 
                 
         R e t u r n s : 
                 D i c t i o n a r y   o f   e x t r a c t e d   e n t i t i e s 
         " " " 
         e n t i t i e s   =   { } 
         
         #   E x t r a c t   p h o n e   n u m b e r s 
         p h o n e _ p a t t e r n   =   r ' ( \ + ? \ d { 1 , 3 } [ - . \ s ] ? ) ? ( \ ( ? \ d { 3 } \ ) ? [ - . \ s ] ? \ d { 3 } [ - . \ s ] ? \ d { 4 } ) ' 
         p h o n e _ m a t c h e s   =   r e . f i n d i t e r ( p h o n e _ p a t t e r n ,   t e x t ) 
         p h o n e s   =   [ m a t c h . g r o u p ( 0 )   f o r   m a t c h   i n   p h o n e _ m a t c h e s ] 
         i f   p h o n e s : 
                 e n t i t i e s [ ' p h o n e _ n u m b e r s ' ]   =   p h o n e s 
         
         #   E x t r a c t   e m a i l   a d d r e s s e s 
         e m a i l _ p a t t e r n   =   r ' [ a - z A - Z 0 - 9 . _ % + - ] + @ [ a - z A - Z 0 - 9 . - ] + \ . [ a - z A - Z ] { 2 , } ' 
         e m a i l _ m a t c h e s   =   r e . f i n d i t e r ( e m a i l _ p a t t e r n ,   t e x t ) 
         e m a i l s   =   [ m a t c h . g r o u p ( 0 )   f o r   m a t c h   i n   e m a i l _ m a t c h e s ] 
         i f   e m a i l s : 
                 e n t i t i e s [ ' e m a i l s ' ]   =   e m a i l s 
         
         #   E x t r a c t   d a t e s 
         d a t e _ p a t t e r n s   =   [ 
                 r ' \ b ( \ d { 1 , 2 } ) [ / - ] ( \ d { 1 , 2 } ) [ / - ] ( \ d { 2 , 4 } ) \ b ' ,     #   M M / D D / Y Y Y Y   o r   D D / M M / Y Y Y Y 
                 r ' \ b ( J a n | F e b | M a r | A p r | M a y | J u n | J u l | A u g | S e p | O c t | N o v | D e c ) [ a - z ] *   ( \ d { 1 , 2 } ) ( ? : s t | n d | r d | t h ) ? , ?   ( \ d { 4 } ) \ b ' ,     #   M o n t h   D D ,   Y Y Y Y 
                 r ' \ b ( \ d { 1 , 2 } ) ( ? : s t | n d | r d | t h ) ?   ( J a n | F e b | M a r | A p r | M a y | J u n | J u l | A u g | S e p | O c t | N o v | D e c ) [ a - z ] * , ?   ( \ d { 4 } ) \ b ' ,     #   D D   M o n t h ,   Y Y Y Y 
         ] 
         
         d a t e s   =   [ ] 
         f o r   p a t t e r n   i n   d a t e _ p a t t e r n s : 
                 d a t e _ m a t c h e s   =   r e . f i n d i t e r ( p a t t e r n ,   t e x t ,   r e . I G N O R E C A S E ) 
                 d a t e s . e x t e n d ( [ m a t c h . g r o u p ( 0 )   f o r   m a t c h   i n   d a t e _ m a t c h e s ] ) 
         
         i f   d a t e s : 
                 e n t i t i e s [ ' d a t e s ' ]   =   d a t e s 
         
         #   E x t r a c t   t i m e s 
         t i m e _ p a t t e r n   =   r ' \ b ( \ d { 1 , 2 } ) : ( \ d { 2 } ) ( ? : : ( \ d { 2 } ) ) ? \ s * ( a m | p m | A M | P M ) ? \ b ' 
         t i m e _ m a t c h e s   =   r e . f i n d i t e r ( t i m e _ p a t t e r n ,   t e x t ) 
         t i m e s   =   [ m a t c h . g r o u p ( 0 )   f o r   m a t c h   i n   t i m e _ m a t c h e s ] 
         i f   t i m e s : 
                 e n t i t i e s [ ' t i m e s ' ]   =   t i m e s 
         
         #   E x t r a c t   n a m e s   ( t h i s   i s   a   s i m p l e   h e u r i s t i c   a n d   w o u l d   b e   m u c h   m o r e   a d v a n c e d   i n   a   r e a l   s y s t e m ) 
         n a m e _ p a t t e r n   =   r ' ( ? : ( ? : m y | h i s | h e r | t h e i r )   n a m e   i s   | I   a m   | I ' m   | T h i s   i s   ) ( [ A - Z ] [ a - z ] +   [ A - Z ] [ a - z ] + ) ' 
         n a m e _ m a t c h e s   =   r e . f i n d i t e r ( n a m e _ p a t t e r n ,   t e x t ) 
         n a m e s   =   [ m a t c h . g r o u p ( 1 )   f o r   m a t c h   i n   n a m e _ m a t c h e s ] 
         i f   n a m e s : 
                 e n t i t i e s [ ' n a m e s ' ]   =   n a m e s 
         
         r e t u r n   e n t i t i e s 