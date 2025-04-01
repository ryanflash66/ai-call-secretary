" " " 
 C a l l   r o u t i n g   r u l e s   a n d   l o g i c . 
 D e t e r m i n e s   h o w   i n c o m i n g   c a l l s   a r e   h a n d l e d   b a s e d   o n   c a l l e r   I D ,   t i m e   o f   d a y ,   e t c . 
 " " " 
 i m p o r t   l o g g i n g 
 i m p o r t   r e 
 i m p o r t   t i m e 
 i m p o r t   y a m l 
 i m p o r t   o s 
 f r o m   d a t e t i m e   i m p o r t   d a t e t i m e ,   t i m e   a s   d t _ t i m e 
 f r o m   t y p i n g   i m p o r t   D i c t ,   L i s t ,   O p t i o n a l ,   A n y ,   T u p l e 
 
 l o g g e r   =   l o g g i n g . g e t L o g g e r ( _ _ n a m e _ _ ) 
 
 c l a s s   C a l l R o u t e r : 
         " " " 
         R o u t e s   i n c o m i n g   c a l l s   b a s e d   o n   r u l e s   a n d   c o n f i g u r a t i o n . 
         " " " 
         
         d e f   _ _ i n i t _ _ ( s e l f ,   c o n f i g _ p a t h :   O p t i o n a l [ s t r ]   =   N o n e ) : 
                 " " " 
                 I n i t i a l i z e   t h e   c a l l   r o u t e r   w i t h   c o n f i g u r a t i o n . 
                 
                 A r g s : 
                         c o n f i g _ p a t h :   P a t h   t o   t h e   r o u t i n g   c o n f i g u r a t i o n   f i l e 
                 " " " 
                 s e l f . c o n f i g _ p a t h   =   c o n f i g _ p a t h   o r   o s . p a t h . j o i n ( 
                         o s . p a t h . d i r n a m e ( _ _ f i l e _ _ ) ,   
                         " . . / . . / c o n f i g / d e f a u l t . y m l " 
                 ) 
                 s e l f . r o u t i n g _ r u l e s   =   [ ] 
                 s e l f . b l a c k l i s t   =   [ ] 
                 s e l f . w h i t e l i s t   =   [ ] 
                 s e l f . b u s i n e s s _ h o u r s   =   { 
                         " s t a r t " :   d t _ t i m e ( 9 ,   0 ) ,     #   9 : 0 0   A M 
                         " e n d " :   d t _ t i m e ( 1 7 ,   0 )         #   5 : 0 0   P M 
                 } 
                 
                 s e l f . _ l o a d _ c o n f i g ( ) 
                 l o g g e r . i n f o ( " C a l l   r o u t e r   i n i t i a l i z e d " ) 
         
         d e f   _ l o a d _ c o n f i g ( s e l f )   - >   N o n e : 
                 " " " 
                 L o a d   r o u t i n g   c o n f i g u r a t i o n   f r o m   Y A M L   f i l e . 
                 " " " 
                 t r y : 
                         w i t h   o p e n ( s e l f . c o n f i g _ p a t h ,   ' r ' )   a s   f : 
                                 c o n f i g   =   y a m l . s a f e _ l o a d ( f ) 
                         
                         i f   n o t   c o n f i g   o r   ' t e l e p h o n y '   n o t   i n   c o n f i g : 
                                 l o g g e r . w a r n i n g ( f " I n v a l i d   c o n f i g u r a t i o n   i n   { s e l f . c o n f i g _ p a t h } " ) 
                                 r e t u r n 
                         
                         t e l e p h o n y _ c o n f i g   =   c o n f i g [ ' t e l e p h o n y ' ] 
                         
                         #   L o a d   r o u t i n g   r u l e s 
                         i f   ' r o u t i n g _ r u l e s '   i n   t e l e p h o n y _ c o n f i g : 
                                 s e l f . r o u t i n g _ r u l e s   =   t e l e p h o n y _ c o n f i g [ ' r o u t i n g _ r u l e s ' ] 
                         
                         #   L o a d   b l a c k l i s t / w h i t e l i s t 
                         i f   ' b l a c k l i s t '   i n   t e l e p h o n y _ c o n f i g : 
                                 s e l f . b l a c k l i s t   =   t e l e p h o n y _ c o n f i g [ ' b l a c k l i s t ' ] 
                         
                         i f   ' w h i t e l i s t '   i n   t e l e p h o n y _ c o n f i g : 
                                 s e l f . w h i t e l i s t   =   t e l e p h o n y _ c o n f i g [ ' w h i t e l i s t ' ] 
                         
                         #   L o a d   b u s i n e s s   h o u r s 
                         i f   ' b u s i n e s s _ h o u r s '   i n   t e l e p h o n y _ c o n f i g : 
                                 h o u r s   =   t e l e p h o n y _ c o n f i g [ ' b u s i n e s s _ h o u r s ' ] 
                                 i f   ' s t a r t '   i n   h o u r s : 
                                         s t a r t _ p a r t s   =   h o u r s [ ' s t a r t ' ] . s p l i t ( ' : ' ) 
                                         s e l f . b u s i n e s s _ h o u r s [ ' s t a r t ' ]   =   d t _ t i m e ( i n t ( s t a r t _ p a r t s [ 0 ] ) ,   i n t ( s t a r t _ p a r t s [ 1 ] ) ) 
                                 
                                 i f   ' e n d '   i n   h o u r s : 
                                         e n d _ p a r t s   =   h o u r s [ ' e n d ' ] . s p l i t ( ' : ' ) 
                                         s e l f . b u s i n e s s _ h o u r s [ ' e n d ' ]   =   d t _ t i m e ( i n t ( e n d _ p a r t s [ 0 ] ) ,   i n t ( e n d _ p a r t s [ 1 ] ) ) 
                         
                         l o g g e r . i n f o ( f " L o a d e d   c o n f i g u r a t i o n   f r o m   { s e l f . c o n f i g _ p a t h } " ) 
                 e x c e p t   E x c e p t i o n   a s   e : 
                         l o g g e r . e r r o r ( f " E r r o r   l o a d i n g   c o n f i g u r a t i o n :   { s t r ( e ) } " ,   e x c _ i n f o = T r u e ) 
         
         d e f   r o u t e _ c a l l ( s e l f ,   c a l l _ m e t a d a t a :   D i c t [ s t r ,   A n y ] )   - >   T u p l e [ s t r ,   D i c t [ s t r ,   A n y ] ] : 
                 " " " 
                 R o u t e   a n   i n c o m i n g   c a l l   b a s e d   o n   c o n f i g u r e d   r u l e s . 
                 
                 A r g s : 
                         c a l l _ m e t a d a t a :   D i c t i o n a r y   c o n t a i n i n g   c a l l   i n f o r m a t i o n 
                         
                 R e t u r n s : 
                         T u p l e   o f   ( r o u t i n g _ a c t i o n ,   a c t i o n _ p a r a m s ) 
                 " " " 
                 c a l l e r _ n u m b e r   =   c a l l _ m e t a d a t a . g e t ( ' c a l l e r _ n u m b e r ' ,   ' ' ) 
                 c a l l e r _ n a m e   =   c a l l _ m e t a d a t a . g e t ( ' c a l l e r _ n a m e ' ,   ' U n k n o w n ' ) 
                 t i m e s t a m p   =   c a l l _ m e t a d a t a . g e t ( ' t i m e s t a m p ' ,   t i m e . t i m e ( ) ) 
                 
                 #   C h e c k   b l a c k l i s t 
                 i f   s e l f . _ i s _ b l a c k l i s t e d ( c a l l e r _ n u m b e r ) : 
                         l o g g e r . i n f o ( f " B l a c k l i s t e d   c a l l e r :   { c a l l e r _ n u m b e r } " ) 
                         r e t u r n   " r e j e c t " ,   { " r e a s o n " :   " b l a c k l i s t e d " } 
                 
                 #   C h e c k   w h i t e l i s t   ( p r i o r i t y   h a n d l i n g ) 
                 i f   s e l f . _ i s _ w h i t e l i s t e d ( c a l l e r _ n u m b e r ) : 
                         l o g g e r . i n f o ( f " W h i t e l i s t e d   c a l l e r :   { c a l l e r _ n u m b e r }   ( { c a l l e r _ n a m e } ) " ) 
                         r e t u r n   " p r i o r i t y " ,   { " l e v e l " :   " h i g h " } 
                 
                 #   C h e c k   b u s i n e s s   h o u r s 
                 i f   n o t   s e l f . _ i s _ b u s i n e s s _ h o u r s ( t i m e s t a m p ) : 
                         l o g g e r . i n f o ( f " C a l l   o u t s i d e   b u s i n e s s   h o u r s   f r o m   { c a l l e r _ n u m b e r } " ) 
                         r e t u r n   " v o i c e m a i l " ,   { " g r e e t i n g " :   " o u t s i d e _ h o u r s " } 
                 
                 #   A p p l y   s p e c i f i c   r o u t i n g   r u l e s 
                 f o r   r u l e   i n   s e l f . r o u t i n g _ r u l e s : 
                         i f   s e l f . _ r u l e _ m a t c h e s ( r u l e ,   c a l l _ m e t a d a t a ) : 
                                 a c t i o n   =   r u l e . g e t ( ' a c t i o n ' ,   ' d e f a u l t ' ) 
                                 p a r a m s   =   r u l e . g e t ( ' p a r a m s ' ,   { } ) 
                                 l o g g e r . i n f o ( f " A p p l i e d   r u l e   { r u l e . g e t ( ' n a m e ' ,   ' u n n a m e d ' ) }   t o   c a l l   f r o m   { c a l l e r _ n u m b e r } " ) 
                                 r e t u r n   a c t i o n ,   p a r a m s 
                 
                 #   D e f a u l t   h a n d l i n g 
                 l o g g e r . i n f o ( f " D e f a u l t   h a n d l i n g   f o r   c a l l   f r o m   { c a l l e r _ n u m b e r }   ( { c a l l e r _ n a m e } ) " ) 
                 r e t u r n   " d e f a u l t " ,   { " a i _ m o d e l " :   " d e f a u l t " } 
         
         d e f   _ i s _ b l a c k l i s t e d ( s e l f ,   n u m b e r :   s t r )   - >   b o o l : 
                 " " " 
                 C h e c k   i f   a   n u m b e r   i s   b l a c k l i s t e d . 
                 
                 A r g s : 
                         n u m b e r :   T h e   c a l l e r ' s   p h o n e   n u m b e r 
                         
                 R e t u r n s : 
                         T r u e   i f   b l a c k l i s t e d ,   F a l s e   o t h e r w i s e 
                 " " " 
                 f o r   p a t t e r n   i n   s e l f . b l a c k l i s t : 
                         i f   r e . s e a r c h ( p a t t e r n ,   n u m b e r ) : 
                                 r e t u r n   T r u e 
                 r e t u r n   F a l s e 
         
         d e f   _ i s _ w h i t e l i s t e d ( s e l f ,   n u m b e r :   s t r )   - >   b o o l : 
                 " " " 
                 C h e c k   i f   a   n u m b e r   i s   w h i t e l i s t e d . 
                 
                 A r g s : 
                         n u m b e r :   T h e   c a l l e r ' s   p h o n e   n u m b e r 
                         
                 R e t u r n s : 
                         T r u e   i f   w h i t e l i s t e d ,   F a l s e   o t h e r w i s e 
                 " " " 
                 f o r   p a t t e r n   i n   s e l f . w h i t e l i s t : 
                         i f   r e . s e a r c h ( p a t t e r n ,   n u m b e r ) : 
                                 r e t u r n   T r u e 
                 r e t u r n   F a l s e 
         
         d e f   _ i s _ b u s i n e s s _ h o u r s ( s e l f ,   t i m e s t a m p :   f l o a t )   - >   b o o l : 
                 " " " 
                 C h e c k   i f   t h e   c a l l   i s   d u r i n g   b u s i n e s s   h o u r s . 
                 
                 A r g s : 
                         t i m e s t a m p :   T h e   c a l l   t i m e s t a m p   a s   a   U n i x   t i m e s t a m p 
                         
                 R e t u r n s : 
                         T r u e   i f   d u r i n g   b u s i n e s s   h o u r s ,   F a l s e   o t h e r w i s e 
                 " " " 
                 c a l l _ t i m e   =   d a t e t i m e . f r o m t i m e s t a m p ( t i m e s t a m p ) . t i m e ( ) 
                 
                 #   I f   b u s i n e s s   h o u r s   s p a n   a c r o s s   m i d n i g h t 
                 i f   s e l f . b u s i n e s s _ h o u r s [ ' s t a r t ' ]   >   s e l f . b u s i n e s s _ h o u r s [ ' e n d ' ] : 
                         r e t u r n   c a l l _ t i m e   > =   s e l f . b u s i n e s s _ h o u r s [ ' s t a r t ' ]   o r   c a l l _ t i m e   <   s e l f . b u s i n e s s _ h o u r s [ ' e n d ' ] 
                 e l s e : 
                         r e t u r n   c a l l _ t i m e   > =   s e l f . b u s i n e s s _ h o u r s [ ' s t a r t ' ]   a n d   c a l l _ t i m e   <   s e l f . b u s i n e s s _ h o u r s [ ' e n d ' ] 
         
         d e f   _ r u l e _ m a t c h e s ( s e l f ,   r u l e :   D i c t [ s t r ,   A n y ] ,   c a l l _ m e t a d a t a :   D i c t [ s t r ,   A n y ] )   - >   b o o l : 
                 " " " 
                 C h e c k   i f   a   r o u t i n g   r u l e   m a t c h e s   t h e   c a l l   m e t a d a t a . 
                 
                 A r g s : 
                         r u l e :   T h e   r o u t i n g   r u l e   t o   c h e c k 
                         c a l l _ m e t a d a t a :   T h e   c a l l   m e t a d a t a 
                         
                 R e t u r n s : 
                         T r u e   i f   t h e   r u l e   m a t c h e s ,   F a l s e   o t h e r w i s e 
                 " " " 
                 #   N u m b e r   p a t t e r n   m a t c h i n g 
                 i f   ' n u m b e r _ p a t t e r n '   i n   r u l e : 
                         c a l l e r _ n u m b e r   =   c a l l _ m e t a d a t a . g e t ( ' c a l l e r _ n u m b e r ' ,   ' ' ) 
                         i f   n o t   r e . s e a r c h ( r u l e [ ' n u m b e r _ p a t t e r n ' ] ,   c a l l e r _ n u m b e r ) : 
                                 r e t u r n   F a l s e 
                 
                 #   N a m e   p a t t e r n   m a t c h i n g 
                 i f   ' n a m e _ p a t t e r n '   i n   r u l e : 
                         c a l l e r _ n a m e   =   c a l l _ m e t a d a t a . g e t ( ' c a l l e r _ n a m e ' ,   ' ' ) 
                         i f   n o t   r e . s e a r c h ( r u l e [ ' n a m e _ p a t t e r n ' ] ,   c a l l e r _ n a m e ) : 
                                 r e t u r n   F a l s e 
                 
                 #   T i m e   r a n g e   m a t c h i n g 
                 i f   ' t i m e _ r a n g e '   i n   r u l e : 
                         t i m e s t a m p   =   c a l l _ m e t a d a t a . g e t ( ' t i m e s t a m p ' ,   t i m e . t i m e ( ) ) 
                         c a l l _ d t   =   d a t e t i m e . f r o m t i m e s t a m p ( t i m e s t a m p ) 
                         
                         t i m e _ r a n g e   =   r u l e [ ' t i m e _ r a n g e ' ] 
                         i f   ' d a y s '   i n   t i m e _ r a n g e : 
                                 i f   c a l l _ d t . s t r f t i m e ( ' % A ' ) . l o w e r ( )   n o t   i n   [ d . l o w e r ( )   f o r   d   i n   t i m e _ r a n g e [ ' d a y s ' ] ] : 
                                         r e t u r n   F a l s e 
                         
                         i f   ' s t a r t _ t i m e '   i n   t i m e _ r a n g e   a n d   ' e n d _ t i m e '   i n   t i m e _ r a n g e : 
                                 s t a r t _ p a r t s   =   t i m e _ r a n g e [ ' s t a r t _ t i m e ' ] . s p l i t ( ' : ' ) 
                                 e n d _ p a r t s   =   t i m e _ r a n g e [ ' e n d _ t i m e ' ] . s p l i t ( ' : ' ) 
                                 
                                 s t a r t _ t i m e   =   d t _ t i m e ( i n t ( s t a r t _ p a r t s [ 0 ] ) ,   i n t ( s t a r t _ p a r t s [ 1 ] ) ) 
                                 e n d _ t i m e   =   d t _ t i m e ( i n t ( e n d _ p a r t s [ 0 ] ) ,   i n t ( e n d _ p a r t s [ 1 ] ) ) 
                                 
                                 c a l l _ t i m e   =   c a l l _ d t . t i m e ( ) 
                                 
                                 #   I f   t i m e   r a n g e   s p a n s   a c r o s s   m i d n i g h t 
                                 i f   s t a r t _ t i m e   >   e n d _ t i m e : 
                                         i f   c a l l _ t i m e   <   s t a r t _ t i m e   a n d   c a l l _ t i m e   > =   e n d _ t i m e : 
                                                 r e t u r n   F a l s e 
                                 e l s e : 
                                         i f   c a l l _ t i m e   <   s t a r t _ t i m e   o r   c a l l _ t i m e   > =   e n d _ t i m e : 
                                                 r e t u r n   F a l s e 
                 
                 #   C u s t o m   c o n d i t i o n   m a t c h i n g 
                 i f   ' c o n d i t i o n '   i n   r u l e : 
                         c o n d i t i o n   =   r u l e [ ' c o n d i t i o n ' ] 
                         i f   c o n d i t i o n   = =   ' r e p e a t _ c a l l e r ' : 
                                 #   T h i s   w o u l d   c h e c k   i f   t h i s   c a l l e r   h a s   c a l l e d   b e f o r e 
                                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   c h e c k   a   d a t a b a s e 
                                 p a s s 
                         e l i f   c o n d i t i o n   = =   ' h i g h _ p r i o r i t y ' : 
                                 #   T h i s   w o u l d   c h e c k   i f   t h i s   c a l l e r   i s   f l a g g e d   a s   h i g h   p r i o r i t y 
                                 #   I n   a   r e a l   i m p l e m e n t a t i o n ,   t h i s   w o u l d   c h e c k   a   d a t a b a s e   o r   C R M 
                                 p a s s 
                 
                 #   I f   w e ' v e   p a s s e d   a l l   c h e c k s ,   t h e   r u l e   m a t c h e s 
                 r e t u r n   T r u e 