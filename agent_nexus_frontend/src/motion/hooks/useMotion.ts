import { 
  useMotionValue, 
  useSpring, 
  MotionValue, 
  useInView, 
  useAnimate, 
  AnimationControls
} from 'framer-motion';
import * as React from 'react';

type MotionControl = {
  value: MotionValue<any>;
  spring: MotionValue<any>;
  controls: AnimationControls;
  isInView: boolean;
};

export function useMotion<T>(initialValue: T, options?: { stiffness?: number; damping?: number }): [React.RefObject<any>, MotionControl] {
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.5 });
  const [scope, controls] = useAnimate();

  const motionValue = useMotionValue(initialValue);
  const springValue = useSpring(motionValue, {
    stiffness: options?.stiffness ?? 100,
    damping: options?.damping ?? 30,
  });

  React.useEffect(() => {
    if (ref.current) {
      // Synchronize the component ref with the animation scope if a different ref is provided
      if (scope.current !== ref.current) {
        scope.current = ref.current;
      }
    }
  }, [ref, scope]);

  return [
    ref,
    {
      value: motionValue,
      spring: springValue,
      controls: controls as AnimationControls,
      isInView: isInView,
    },
  ];
}