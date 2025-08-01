import { useState, useEffect, useRef, useCallback } from 'react';

export const useSmartScroll = () => {
    const [userHasScrolledUp, setUserHasScrolledUp] = useState(false);
    const scrollContainerRef = useRef<HTMLDivElement | null>(null);

    // Memoized function to scroll to the bottom
    const scrollToBottom = useCallback(() => {
        if (scrollContainerRef.current) {
            scrollContainerRef.current.scrollTo({
                top: scrollContainerRef.current.scrollHeight,
                behavior: 'smooth',
            });
            setUserHasScrolledUp(false);
        }
    }, []);

    // Effect to detect user scroll
    useEffect(() => {
        const container = scrollContainerRef.current;
        if (!container) return;

        let scrollTimeout: number;
        const handleScroll = () => {
            // Debounce scroll event to avoid rapid state changes
            clearTimeout(scrollTimeout);
            scrollTimeout = window.setTimeout(() => {
                const { scrollTop, scrollHeight, clientHeight } = container;
                // The user is considered to have scrolled up if they are more than a 50px threshold from the bottom.
                const atBottom = scrollHeight - scrollTop - clientHeight < 50;
                setUserHasScrolledUp(!atBottom);
            }, 150);
        };

        container.addEventListener('scroll', handleScroll, { passive: true });

        // Cleanup function
        return () => {
            clearTimeout(scrollTimeout);
            container.removeEventListener('scroll', handleScroll);
        };
    }, []); 

    // Callback for the typing animation to trigger auto-scroll
    const onTyping = useCallback(() => {
        if (!userHasScrolledUp && scrollContainerRef.current) {
            // Use instant scroll to keep up with fast-typing text
            scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
        }
    }, [userHasScrolledUp]); // Depends on whether the user has scrolled up

    return { scrollContainerRef, userHasScrolledUp, scrollToBottom, onTyping };
};
