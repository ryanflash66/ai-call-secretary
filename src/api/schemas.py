" " " 
 P y d a n t i c   s c h e m a s   f o r   A P I   v a l i d a t i o n . 
 " " " 
 f r o m   t y p i n g   i m p o r t   L i s t ,   D i c t ,   O p t i o n a l ,   A n y ,   U n i o n 
 f r o m   e n u m   i m p o r t   E n u m 
 f r o m   d a t e t i m e   i m p o r t   d a t e t i m e 
 f r o m   p y d a n t i c   i m p o r t   B a s e M o d e l ,   F i e l d ,   E m a i l S t r ,   v a l i d a t o r 
 
 
 c l a s s   C a l l S t a t u s ( s t r ,   E n u m ) : 
         " " " C a l l   s t a t u s   e n u m . " " " 
         A C T I V E   =   " a c t i v e " 
         C O M P L E T E D   =   " c o m p l e t e d " 
         F A I L E D   =   " f a i l e d " 
         T R A N S F E R R E D   =   " t r a n s f e r r e d " 
         V O I C E M A I L   =   " v o i c e m a i l " 
 
 
 c l a s s   F l o w T y p e ( s t r ,   E n u m ) : 
         " " " F l o w   t y p e   e n u m . " " " 
         G E N E R A L   =   " g e n e r a l " 
         A P P O I N T M E N T   =   " a p p o i n t m e n t " 
         M E S S A G E   =   " m e s s a g e " 
         I N F O R M A T I O N   =   " i n f o " 
         E S C A L A T I O N   =   " e s c a l a t i o n " 
 
 
 c l a s s   A c t i o n T y p e ( s t r ,   E n u m ) : 
         " " " A c t i o n   t y p e   e n u m . " " " 
         S C H E D U L E _ A P P O I N T M E N T   =   " s c h e d u l e _ a p p o i n t m e n t " 
         C A N C E L _ A P P O I N T M E N T   =   " c a n c e l _ a p p o i n t m e n t " 
         T A K E _ M E S S A G E   =   " t a k e _ m e s s a g e " 
         T R A N S F E R _ C A L L   =   " t r a n s f e r _ c a l l " 
         L O O K U P _ I N F O   =   " l o o k u p _ i n f o " 
         S A V E _ C O N T A C T   =   " s a v e _ c o n t a c t " 
         S E T _ R E M I N D E R   =   " s e t _ r e m i n d e r " 
         S E N D _ E M A I L   =   " s e n d _ e m a i l " 
         S E N D _ S M S   =   " s e n d _ s m s " 
 
 
 c l a s s   C a l l E v e n t T y p e ( s t r ,   E n u m ) : 
         " " " C a l l   e v e n t   t y p e   e n u m . " " " 
         C A L L _ S T A R T E D   =   " c a l l _ s t a r t e d " 
         C A L L _ C O N N E C T E D   =   " c a l l _ c o n n e c t e d " 
         U S E R _ S P O K E   =   " u s e r _ s p o k e " 
         A S S I S T A N T _ S P O K E   =   " a s s i s t a n t _ s p o k e " 
         F L O W _ C H A N G E D   =   " f l o w _ c h a n g e d " 
         A C T I O N _ E X E C U T E D   =   " a c t i o n _ e x e c u t e d " 
         C A L L _ E N D E D   =   " c a l l _ e n d e d " 
         E R R O R   =   " e r r o r " 
 
 
 c l a s s   C a l l E v e n t ( B a s e M o d e l ) : 
         " " " C a l l   e v e n t   m o d e l . " " " 
         e v e n t _ t y p e :   C a l l E v e n t T y p e 
         t i m e s t a m p :   d a t e t i m e   =   F i e l d ( d e f a u l t _ f a c t o r y = d a t e t i m e . n o w ) 
         c a l l _ i d :   s t r 
         d a t a :   O p t i o n a l [ D i c t [ s t r ,   A n y ] ]   =   N o n e 
 
 
 c l a s s   T r a n s c r i p t I t e m ( B a s e M o d e l ) : 
         " " " T r a n s c r i p t   i t e m   m o d e l . " " " 
         s p e a k e r :   s t r     #   " u s e r "   o r   " a s s i s t a n t " 
         t e x t :   s t r 
         t i m e s t a m p :   d a t e t i m e   =   F i e l d ( d e f a u l t _ f a c t o r y = d a t e t i m e . n o w ) 
         c o n f i d e n c e :   O p t i o n a l [ f l o a t ]   =   N o n e 
 
 
 c l a s s   C a l l T r a n s c r i p t ( B a s e M o d e l ) : 
         " " " C a l l   t r a n s c r i p t   m o d e l . " " " 
         c a l l _ i d :   s t r 
         i t e m s :   L i s t [ T r a n s c r i p t I t e m ]   =   [ ] 
 
 
 c l a s s   A c t i o n R e s u l t ( B a s e M o d e l ) : 
         " " " A c t i o n   r e s u l t   m o d e l . " " " 
         a c t i o n _ t y p e :   A c t i o n T y p e 
         s u c c e s s :   b o o l 
         t i m e s t a m p :   d a t e t i m e   =   F i e l d ( d e f a u l t _ f a c t o r y = d a t e t i m e . n o w ) 
         d e t a i l s :   O p t i o n a l [ D i c t [ s t r ,   A n y ] ]   =   N o n e 
         e r r o r :   O p t i o n a l [ s t r ]   =   N o n e 
 
 
 c l a s s   C a l l D e t a i l ( B a s e M o d e l ) : 
         " " " C a l l   d e t a i l   m o d e l . " " " 
         c a l l _ i d :   s t r 
         c a l l e r _ n u m b e r :   s t r 
         c a l l e r _ n a m e :   O p t i o n a l [ s t r ]   =   N o n e 
         s t a r t _ t i m e :   d a t e t i m e 
         e n d _ t i m e :   O p t i o n a l [ d a t e t i m e ]   =   N o n e 
         d u r a t i o n :   O p t i o n a l [ i n t ]   =   N o n e     #   s e c o n d s 
         s t a t u s :   C a l l S t a t u s 
         c u r r e n t _ f l o w :   O p t i o n a l [ F l o w T y p e ]   =   N o n e 
         a c t i o n s :   L i s t [ A c t i o n R e s u l t ]   =   [ ] 
         t r a n s c r i p t :   O p t i o n a l [ C a l l T r a n s c r i p t ]   =   N o n e 
         m e t a d a t a :   O p t i o n a l [ D i c t [ s t r ,   A n y ] ]   =   N o n e 
 
 
 c l a s s   C a l l S u m m a r y ( B a s e M o d e l ) : 
         " " " C a l l   s u m m a r y   m o d e l . " " " 
         c a l l _ i d :   s t r 
         c a l l e r _ n u m b e r :   s t r 
         c a l l e r _ n a m e :   O p t i o n a l [ s t r ]   =   N o n e 
         s t a r t _ t i m e :   d a t e t i m e 
         e n d _ t i m e :   O p t i o n a l [ d a t e t i m e ]   =   N o n e 
         d u r a t i o n :   O p t i o n a l [ i n t ]   =   N o n e     #   s e c o n d s 
         s t a t u s :   C a l l S t a t u s 
         s u m m a r y :   O p t i o n a l [ s t r ]   =   N o n e 
 
 
 #   R e q u e s t / R e s p o n s e   M o d e l s 
 
 c l a s s   T o k e n R e s p o n s e ( B a s e M o d e l ) : 
         " " " T o k e n   r e s p o n s e   m o d e l . " " " 
         a c c e s s _ t o k e n :   s t r 
         t o k e n _ t y p e :   s t r   =   " b e a r e r " 
         e x p i r e s _ i n :   i n t   =   3 6 0 0 
 
 
 c l a s s   E r r o r R e s p o n s e ( B a s e M o d e l ) : 
         " " " E r r o r   r e s p o n s e   m o d e l . " " " 
         e r r o r :   s t r 
         d e t a i l :   O p t i o n a l [ s t r ]   =   N o n e 
 
 
 c l a s s   C a l l L i s t R e s p o n s e ( B a s e M o d e l ) : 
         " " " C a l l   l i s t   r e s p o n s e   m o d e l . " " " 
         c a l l s :   L i s t [ C a l l S u m m a r y ] 
         t o t a l :   i n t 
         p a g e :   i n t 
         p a g e _ s i z e :   i n t 
 
 
 c l a s s   C a l l F i l t e r P a r a m s ( B a s e M o d e l ) : 
         " " " C a l l   f i l t e r   p a r a m e t e r s   m o d e l . " " " 
         s t a r t _ d a t e :   O p t i o n a l [ d a t e t i m e ]   =   N o n e 
         e n d _ d a t e :   O p t i o n a l [ d a t e t i m e ]   =   N o n e 
         s t a t u s :   O p t i o n a l [ C a l l S t a t u s ]   =   N o n e 
         c a l l e r _ n u m b e r :   O p t i o n a l [ s t r ]   =   N o n e 
         p a g e :   i n t   =   1 
         p a g e _ s i z e :   i n t   =   5 0 
 
 
 c l a s s   A c t i o n R e q u e s t ( B a s e M o d e l ) : 
         " " " A c t i o n   r e q u e s t   m o d e l . " " " 
         a c t i o n _ t y p e :   A c t i o n T y p e 
         p a r a m s :   D i c t [ s t r ,   A n y ] 
 
 
 c l a s s   A p p o i n t m e n t R e q u e s t ( B a s e M o d e l ) : 
         " " " A p p o i n t m e n t   r e q u e s t   m o d e l . " " " 
         d a t e :   s t r     #   I S O   f o r m a t   d a t e 
         t i m e :   s t r 
         d u r a t i o n :   i n t   =   3 0     #   m i n u t e s 
         n a m e :   s t r 
         p h o n e :   O p t i o n a l [ s t r ]   =   N o n e 
         e m a i l :   O p t i o n a l [ E m a i l S t r ]   =   N o n e 
         p u r p o s e :   O p t i o n a l [ s t r ]   =   N o n e 
         n o t e s :   O p t i o n a l [ s t r ]   =   N o n e 
 
 
 c l a s s   M e s s a g e R e q u e s t ( B a s e M o d e l ) : 
         " " " M e s s a g e   r e q u e s t   m o d e l . " " " 
         m e s s a g e :   s t r 
         c a l l e r _ n a m e :   s t r 
         c a l l e r _ n u m b e r :   O p t i o n a l [ s t r ]   =   N o n e 
         u r g e n c y :   s t r   =   " n o r m a l "     #   l o w ,   n o r m a l ,   h i g h ,   c r i t i c a l 
         c a l l b a c k _ r e q u e s t e d :   b o o l   =   F a l s e 
 
 
 c l a s s   S y s t e m S t a t u s ( B a s e M o d e l ) : 
         " " " S y s t e m   s t a t u s   m o d e l . " " " 
         s t a t u s :   s t r 
         v e r s i o n :   s t r 
         u p t i m e :   i n t     #   s e c o n d s 
         a c t i v e _ c a l l s :   i n t 
         t o t a l _ c a l l s _ t o d a y :   i n t 
         c o m p o n e n t s :   D i c t [ s t r ,   s t r ]     #   c o m p o n e n t   n a m e   - >   s t a t u s 
 