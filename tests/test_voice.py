" " " 
 T e s t s   f o r   v o i c e   f u n c t i o n a l i t y . 
 " " " 
 i m p o r t   o s 
 i m p o r t   u n i t t e s t 
 i m p o r t   t e m p f i l e 
 i m p o r t   j s o n 
 i m p o r t   s h u t i l 
 f r o m   u n i t t e s t . m o c k   i m p o r t   M a g i c M o c k ,   p a t c h 
 
 i m p o r t   s y s 
 s y s . p a t h . a p p e n d ( o s . p a t h . d i r n a m e ( o s . p a t h . d i r n a m e ( o s . p a t h . a b s p a t h ( _ _ f i l e _ _ ) ) ) ) 
 
 f r o m   s r c . v o i c e . s t t   i m p o r t   S p e e c h T o T e x t 
 f r o m   s r c . v o i c e . t t s   i m p o r t   T e x t T o S p e e c h 
 f r o m   s r c . v o i c e . v o i c e _ c l o n e   i m p o r t   V o i c e C l o n e r 
 
 c l a s s   T e s t S p e e c h T o T e x t ( u n i t t e s t . T e s t C a s e ) : 
         " " " T e s t   c a s e s   f o r   t h e   S p e e c h T o T e x t   c l a s s . " " " 
         
         d e f   s e t U p ( s e l f ) : 
                 " " " S e t   u p   t e s t   f i x t u r e s . " " " 
                 #   M o c k   t h e   w h i s p e r   m o d e l   a n d   c o n f i g   l o a d i n g 
                 s e l f . w h i s p e r _ p a t c h e r   =   p a t c h ( ' w h i s p e r . l o a d _ m o d e l ' ) 
                 s e l f . w h i s p e r _ m o c k   =   s e l f . w h i s p e r _ p a t c h e r . s t a r t ( ) 
                 
                 #   M o c k   m o d e l   i n s t a n c e 
                 s e l f . m o d e l _ m o c k   =   M a g i c M o c k ( ) 
                 s e l f . w h i s p e r _ m o c k . r e t u r n _ v a l u e   =   s e l f . m o d e l _ m o c k 
                 
                 #   S e t   u p   t e s t   t r a n s c r i p t i o n   r e s p o n s e 
                 s e l f . m o d e l _ m o c k . t r a n s c r i b e . r e t u r n _ v a l u e   =   { " t e x t " :   " T h i s   i s   a   t e s t   t r a n s c r i p t i o n " } 
                 
                 #   C r e a t e   a   s t t   i n s t a n c e 
                 s e l f . s t t   =   S p e e c h T o T e x t ( ) 
                 
                 #   F o r c e   m o d e l   l o a d i n g 
                 s e l f . s t t . _ e n s u r e _ m o d e l _ l o a d e d ( ) 
         
         d e f   t e a r D o w n ( s e l f ) : 
                 " " " T e a r   d o w n   t e s t   f i x t u r e s . " " " 
                 s e l f . w h i s p e r _ p a t c h e r . s t o p ( ) 
         
         d e f   t e s t _ m o d e l _ l o a d i n g ( s e l f ) : 
                 " " " T e s t   m o d e l   l o a d i n g . " " " 
                 s e l f . w h i s p e r _ m o c k . a s s e r t _ c a l l e d _ o n c e ( ) 
         
         d e f   t e s t _ t r a n s c r i b e _ b y t e s ( s e l f ) : 
                 " " " T e s t   t r a n s c r i b i n g   f r o m   b y t e s . " " " 
                 r e s u l t   =   s e l f . s t t . t r a n s c r i b e ( b " t e s t   a u d i o   d a t a " ) 
                 
                 #   C h e c k   t h a t   a   t e m p o r a r y   f i l e   w a s   c r e a t e d   ( i n d i r e c t l y   b y   c h e c k i n g   t h e   t r a n s c r i b e   c a l l ) 
                 a r g s ,   k w a r g s   =   s e l f . m o d e l _ m o c k . t r a n s c r i b e . c a l l _ a r g s 
                 s e l f . a s s e r t T r u e ( i s i n s t a n c e ( a r g s [ 0 ] ,   s t r ) )     #   S h o u l d   b e   a   f i l e   p a t h 
                 
                 #   C h e c k   t h e   r e s u l t 
                 s e l f . a s s e r t E q u a l ( r e s u l t ,   " T h i s   i s   a   t e s t   t r a n s c r i p t i o n " ) 
         
         d e f   t e s t _ t r a n s c r i b e _ f i l e _ p a t h ( s e l f ) : 
                 " " " T e s t   t r a n s c r i b i n g   f r o m   a   f i l e   p a t h . " " " 
                 w i t h   t e m p f i l e . N a m e d T e m p o r a r y F i l e ( s u f f i x = " . w a v " )   a s   t e m p _ f i l e : 
                         r e s u l t   =   s e l f . s t t . t r a n s c r i b e ( t e m p _ f i l e . n a m e ) 
                         
                         #   C h e c k   t h a t   t h e   f i l e   p a t h   w a s   p a s s e d   d i r e c t l y 
                         s e l f . m o d e l _ m o c k . t r a n s c r i b e . a s s e r t _ c a l l e d _ w i t h ( t e m p _ f i l e . n a m e ,   l a n g u a g e = " e n " ,   t a s k = " t r a n s c r i b e " ) 
                         
                         #   C h e c k   t h e   r e s u l t 
                         s e l f . a s s e r t E q u a l ( r e s u l t ,   " T h i s   i s   a   t e s t   t r a n s c r i p t i o n " ) 
         
         d e f   t e s t _ t r a n s c r i b e _ e r r o r _ h a n d l i n g ( s e l f ) : 
                 " " " T e s t   e r r o r   h a n d l i n g   d u r i n g   t r a n s c r i p t i o n . " " " 
                 #   M a k e   t h e   m o d e l   r a i s e   a n   e x c e p t i o n 
                 s e l f . m o d e l _ m o c k . t r a n s c r i b e . s i d e _ e f f e c t   =   E x c e p t i o n ( " T e s t   e r r o r " ) 
                 
                 #   S h o u l d   r e t u r n   e m p t y   s t r i n g   o n   e r r o r 
                 r e s u l t   =   s e l f . s t t . t r a n s c r i b e ( b " t e s t   a u d i o   d a t a " ) 
                 s e l f . a s s e r t E q u a l ( r e s u l t ,   " " ) 
 
 
 c l a s s   T e s t T e x t T o S p e e c h ( u n i t t e s t . T e s t C a s e ) : 
         " " " T e s t   c a s e s   f o r   t h e   T e x t T o S p e e c h   c l a s s . " " " 
         
         d e f   s e t U p ( s e l f ) : 
                 " " " S e t   u p   t e s t   f i x t u r e s . " " " 
                 #   C r e a t e   a   t t s   i n s t a n c e 
                 s e l f . t t s   =   T e x t T o S p e e c h ( ) 
                 
                 #   M o c k   t h e   e n g i n e - s p e c i f i c   m e t h o d s 
                 s e l f . s e s a m e _ p a t c h e r   =   p a t c h . o b j e c t ( s e l f . t t s ,   ' _ s y n t h e s i z e _ s e s a m e ' ,   r e t u r n _ v a l u e = b " S E S A M E _ A U D I O " ) 
                 s e l f . p y t t s x 3 _ p a t c h e r   =   p a t c h . o b j e c t ( s e l f . t t s ,   ' _ s y n t h e s i z e _ p y t t s x 3 ' ,   r e t u r n _ v a l u e = b " P Y T T S X 3 _ A U D I O " ) 
                 s e l f . a p i _ p a t c h e r   =   p a t c h . o b j e c t ( s e l f . t t s ,   ' _ s y n t h e s i z e _ a p i ' ,   r e t u r n _ v a l u e = b " A P I _ A U D I O " ) 
                 
                 s e l f . s e s a m e _ m o c k   =   s e l f . s e s a m e _ p a t c h e r . s t a r t ( ) 
                 s e l f . p y t t s x 3 _ m o c k   =   s e l f . p y t t s x 3 _ p a t c h e r . s t a r t ( ) 
                 s e l f . a p i _ m o c k   =   s e l f . a p i _ p a t c h e r . s t a r t ( ) 
         
         d e f   t e a r D o w n ( s e l f ) : 
                 " " " T e a r   d o w n   t e s t   f i x t u r e s . " " " 
                 s e l f . s e s a m e _ p a t c h e r . s t o p ( ) 
                 s e l f . p y t t s x 3 _ p a t c h e r . s t o p ( ) 
                 s e l f . a p i _ p a t c h e r . s t o p ( ) 
         
         d e f   t e s t _ s y n t h e s i z e _ s e s a m e ( s e l f ) : 
                 " " " T e s t   s e s a m e   s y n t h e s i s . " " " 
                 s e l f . t t s . e n g i n e   =   " s e s a m e " 
                 r e s u l t   =   s e l f . t t s . s y n t h e s i z e ( " T e s t   t e x t " ) 
                 
                 s e l f . s e s a m e _ m o c k . a s s e r t _ c a l l e d _ w i t h ( " T e s t   t e x t " ,   N o n e ,   N o n e ) 
                 s e l f . a s s e r t E q u a l ( r e s u l t ,   b " S E S A M E _ A U D I O " ) 
         
         d e f   t e s t _ s y n t h e s i z e _ p y t t s x 3 ( s e l f ) : 
                 " " " T e s t   p y t t s x 3   s y n t h e s i s . " " " 
                 s e l f . t t s . e n g i n e   =   " p y t t s x 3 " 
                 r e s u l t   =   s e l f . t t s . s y n t h e s i z e ( " T e s t   t e x t " ) 
                 
                 s e l f . p y t t s x 3 _ m o c k . a s s e r t _ c a l l e d _ w i t h ( " T e s t   t e x t " ,   N o n e ,   N o n e ) 
                 s e l f . a s s e r t E q u a l ( r e s u l t ,   b " P Y T T S X 3 _ A U D I O " ) 
         
         d e f   t e s t _ s y n t h e s i z e _ a p i ( s e l f ) : 
                 " " " T e s t   A P I   s y n t h e s i s . " " " 
                 s e l f . t t s . e n g i n e   =   " a p i " 
                 r e s u l t   =   s e l f . t t s . s y n t h e s i z e ( " T e s t   t e x t " ) 
                 
                 s e l f . a p i _ m o c k . a s s e r t _ c a l l e d _ w i t h ( " T e s t   t e x t " ,   N o n e ,   N o n e ) 
                 s e l f . a s s e r t E q u a l ( r e s u l t ,   b " A P I _ A U D I O " ) 
         
         d e f   t e s t _ s y n t h e s i z e _ e m p t y _ t e x t ( s e l f ) : 
                 " " " T e s t   s y n t h e s i z i n g   e m p t y   t e x t . " " " 
                 r e s u l t   =   s e l f . t t s . s y n t h e s i z e ( " " ) 
                 s e l f . a s s e r t E q u a l ( r e s u l t ,   b " " ) 
         
         d e f   t e s t _ s y n t h e s i z e _ i n v a l i d _ e n g i n e ( s e l f ) : 
                 " " " T e s t   s y n t h e s i z i n g   w i t h   i n v a l i d   e n g i n e . " " " 
                 s e l f . t t s . e n g i n e   =   " i n v a l i d " 
                 r e s u l t   =   s e l f . t t s . s y n t h e s i z e ( " T e s t   t e x t " ) 
                 s e l f . a s s e r t E q u a l ( r e s u l t ,   b " " ) 
 
 
 c l a s s   T e s t V o i c e C l o n e r ( u n i t t e s t . T e s t C a s e ) : 
         " " " T e s t   c a s e s   f o r   t h e   V o i c e C l o n e r   c l a s s . " " " 
         
         d e f   s e t U p ( s e l f ) : 
                 " " " S e t   u p   t e s t   f i x t u r e s . " " " 
                 #   C r e a t e   a   t e m p o r a r y   d i r e c t o r y   f o r   v o i c e   m o d e l s 
                 s e l f . t e m p _ d i r   =   t e m p f i l e . m k d t e m p ( ) 
                 s e l f . v o i c e _ d i r   =   o s . p a t h . j o i n ( s e l f . t e m p _ d i r ,   " v o i c e s " ) 
                 s e l f . t e m p _ s a m p l e _ d i r   =   o s . p a t h . j o i n ( s e l f . t e m p _ d i r ,   " s a m p l e s " ) 
                 
                 o s . m a k e d i r s ( s e l f . v o i c e _ d i r ,   e x i s t _ o k = T r u e ) 
                 o s . m a k e d i r s ( s e l f . t e m p _ s a m p l e _ d i r ,   e x i s t _ o k = T r u e ) 
                 
                 #   C r e a t e   s o m e   t e s t   a u d i o   f i l e s 
                 s e l f . a u d i o _ s a m p l e s   =   [ ] 
                 f o r   i   i n   r a n g e ( 5 ) : 
                         s a m p l e _ p a t h   =   o s . p a t h . j o i n ( s e l f . t e m p _ s a m p l e _ d i r ,   f " s a m p l e _ { i } . w a v " ) 
                         w i t h   o p e n ( s a m p l e _ p a t h ,   ' w b ' )   a s   f : 
                                 f . w r i t e ( b " F A K E _ A U D I O _ D A T A " ) 
                         s e l f . a u d i o _ s a m p l e s . a p p e n d ( s a m p l e _ p a t h ) 
                 
                 #   C r e a t e   a   m o c k   c o n f i g 
                 s e l f . c o n f i g _ p a t h   =   o s . p a t h . j o i n ( s e l f . t e m p _ d i r ,   " c o n f i g . y m l " ) 
                 w i t h   o p e n ( s e l f . c o n f i g _ p a t h ,   ' w ' )   a s   f : 
                         f . w r i t e ( f " " " 
 v o i c e : 
     v o i c e _ c l o n e : 
         e n a b l e d :   t r u e 
         t r a i n i n g _ s a m p l e s :   3 
         t r a i n i n g _ t i m e :   5 
         v o i c e _ d i r :   { s e l f . v o i c e _ d i r } 
         t e m p _ d i r :   { s e l f . t e m p _ d i r } 
 " " " ) 
                 
                 #   C r e a t e   a   v o i c e   c l o n e r   i n s t a n c e 
                 s e l f . v o i c e _ c l o n e r   =   V o i c e C l o n e r ( s e l f . c o n f i g _ p a t h ) 
         
         d e f   t e a r D o w n ( s e l f ) : 
                 " " " T e a r   d o w n   t e s t   f i x t u r e s . " " " 
                 s h u t i l . r m t r e e ( s e l f . t e m p _ d i r ) 
         
         d e f   t e s t _ c r e a t e _ v o i c e ( s e l f ) : 
                 " " " T e s t   c r e a t i n g   a   v o i c e . " " " 
                 s u c c e s s ,   m e s s a g e   =   s e l f . v o i c e _ c l o n e r . c r e a t e _ v o i c e ( " t e s t _ v o i c e " ,   s e l f . a u d i o _ s a m p l e s ) 
                 
                 s e l f . a s s e r t T r u e ( s u c c e s s ) 
                 s e l f . a s s e r t T r u e ( " c r e a t e d   s u c c e s s f u l l y "   i n   m e s s a g e ) 
                 
                 #   C h e c k   t h a t   t h e   v o i c e   d i r e c t o r y   w a s   c r e a t e d 
                 v o i c e _ p a t h   =   o s . p a t h . j o i n ( s e l f . v o i c e _ d i r ,   " t e s t _ v o i c e " ) 
                 s e l f . a s s e r t T r u e ( o s . p a t h . e x i s t s ( v o i c e _ p a t h ) ) 
                 
                 #   C h e c k   t h a t   m e t a d a t a   w a s   c r e a t e d 
                 m e t a d a t a _ p a t h   =   o s . p a t h . j o i n ( v o i c e _ p a t h ,   " m e t a d a t a . j s o n " ) 
                 s e l f . a s s e r t T r u e ( o s . p a t h . e x i s t s ( m e t a d a t a _ p a t h ) ) 
                 
                 #   C h e c k   t h a t   t h e   m o d e l   f i l e   w a s   c r e a t e d 
                 m o d e l _ p a t h   =   o s . p a t h . j o i n ( v o i c e _ p a t h ,   " m o d e l . b i n " ) 
                 s e l f . a s s e r t T r u e ( o s . p a t h . e x i s t s ( m o d e l _ p a t h ) ) 
         
         d e f   t e s t _ c r e a t e _ v o i c e _ w i t h _ m e t a d a t a ( s e l f ) : 
                 " " " T e s t   c r e a t i n g   a   v o i c e   w i t h   m e t a d a t a . " " " 
                 m e t a d a t a   =   { 
                         " d e s c r i p t i o n " :   " T e s t   v o i c e " , 
                         " g e n d e r " :   " f e m a l e " , 
                         " l a n g u a g e " :   " e n - U S " 
                 } 
                 
                 s u c c e s s ,   m e s s a g e   =   s e l f . v o i c e _ c l o n e r . c r e a t e _ v o i c e ( " t e s t _ v o i c e _ m e t a " ,   s e l f . a u d i o _ s a m p l e s ,   m e t a d a t a ) 
                 
                 s e l f . a s s e r t T r u e ( s u c c e s s ) 
                 
                 #   C h e c k   t h e   m e t a d a t a   w a s   s a v e d   c o r r e c t l y 
                 m e t a d a t a _ p a t h   =   o s . p a t h . j o i n ( s e l f . v o i c e _ d i r ,   " t e s t _ v o i c e _ m e t a " ,   " m e t a d a t a . j s o n " ) 
                 w i t h   o p e n ( m e t a d a t a _ p a t h ,   ' r ' )   a s   f : 
                         s a v e d _ m e t a d a t a   =   j s o n . l o a d ( f ) 
                 
                 #   T h e   m e t a d a t a   s h o u l d   i n c l u d e   b o t h   t h e   p r o v i d e d   v a l u e s   a n d   a u t o - g e n e r a t e d   o n e s 
                 s e l f . a s s e r t E q u a l ( s a v e d _ m e t a d a t a [ " d e s c r i p t i o n " ] ,   " T e s t   v o i c e " ) 
                 s e l f . a s s e r t E q u a l ( s a v e d _ m e t a d a t a [ " g e n d e r " ] ,   " f e m a l e " ) 
                 s e l f . a s s e r t E q u a l ( s a v e d _ m e t a d a t a [ " l a n g u a g e " ] ,   " e n - U S " ) 
                 s e l f . a s s e r t E q u a l ( s a v e d _ m e t a d a t a [ " n a m e " ] ,   " t e s t _ v o i c e _ m e t a " ) 
         
         d e f   t e s t _ l i s t _ v o i c e s ( s e l f ) : 
                 " " " T e s t   l i s t i n g   v o i c e s . " " " 
                 #   C r e a t e   a   c o u p l e   o f   v o i c e s 
                 s e l f . v o i c e _ c l o n e r . c r e a t e _ v o i c e ( " v o i c e 1 " ,   s e l f . a u d i o _ s a m p l e s ) 
                 s e l f . v o i c e _ c l o n e r . c r e a t e _ v o i c e ( " v o i c e 2 " ,   s e l f . a u d i o _ s a m p l e s ) 
                 
                 v o i c e s   =   s e l f . v o i c e _ c l o n e r . l i s t _ v o i c e s ( ) 
                 
                 s e l f . a s s e r t E q u a l ( l e n ( v o i c e s ) ,   2 ) 
                 s e l f . a s s e r t I n ( " v o i c e 1 " ,   v o i c e s ) 
                 s e l f . a s s e r t I n ( " v o i c e 2 " ,   v o i c e s ) 
         
         d e f   t e s t _ d e l e t e _ v o i c e ( s e l f ) : 
                 " " " T e s t   d e l e t i n g   a   v o i c e . " " " 
                 #   C r e a t e   a   v o i c e 
                 s e l f . v o i c e _ c l o n e r . c r e a t e _ v o i c e ( " v o i c e _ t o _ d e l e t e " ,   s e l f . a u d i o _ s a m p l e s ) 
                 
                 #   V e r i f y   i t   e x i s t s 
                 v o i c e _ p a t h   =   o s . p a t h . j o i n ( s e l f . v o i c e _ d i r ,   " v o i c e _ t o _ d e l e t e " ) 
                 s e l f . a s s e r t T r u e ( o s . p a t h . e x i s t s ( v o i c e _ p a t h ) ) 
                 
                 #   D e l e t e   i t 
                 s u c c e s s ,   m e s s a g e   =   s e l f . v o i c e _ c l o n e r . d e l e t e _ v o i c e ( " v o i c e _ t o _ d e l e t e " ) 
                 
                 s e l f . a s s e r t T r u e ( s u c c e s s ) 
                 s e l f . a s s e r t T r u e ( " d e l e t e d   s u c c e s s f u l l y "   i n   m e s s a g e ) 
                 
                 #   V e r i f y   i t   w a s   d e l e t e d 
                 s e l f . a s s e r t F a l s e ( o s . p a t h . e x i s t s ( v o i c e _ p a t h ) ) 
         
         d e f   t e s t _ d e l e t e _ n o n e x i s t e n t _ v o i c e ( s e l f ) : 
                 " " " T e s t   d e l e t i n g   a   n o n e x i s t e n t   v o i c e . " " " 
                 s u c c e s s ,   m e s s a g e   =   s e l f . v o i c e _ c l o n e r . d e l e t e _ v o i c e ( " n o n e x i s t e n t _ v o i c e " ) 
                 
                 s e l f . a s s e r t F a l s e ( s u c c e s s ) 
                 s e l f . a s s e r t T r u e ( " d o e s   n o t   e x i s t "   i n   m e s s a g e ) 
 
 
 i f   _ _ n a m e _ _   = =   ' _ _ m a i n _ _ ' : 
         u n i t t e s t . m a i n ( ) 