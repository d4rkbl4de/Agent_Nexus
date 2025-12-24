import * as React from 'react';

const QUERY = '(prefers-reduced-motion: reduce)';

export function useReducedMotion(): boolean | undefined {
  const [prefersReducedMotion, setPrefersReducedMotion] = React.useState<
    boolean | undefined
  >(undefined);

  React.useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) {
      setPrefersReducedMotion(false);
      return;
    }

    const mediaQueryList = window.matchMedia(QUERY);

    const listener = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    setPrefersReducedMotion(mediaQueryList.matches);

    try {
      mediaQueryList.addEventListener('change', listener);
    } catch (e) {

      mediaQueryList.addListener(listener);
    }

    return () => {
      try {
        mediaQueryList.removeEventListener('change', listener);
      } catch (e) {

        mediaQueryList.removeListener(listener);
      }
    };
  }, []);

  return prefersReducedMotion;
}