import * as React from 'react';
import { useScheduler } from '../../motion/performance/scheduler';
import { assertExists } from '../../utils/assert';

type DrawFunction = (ctx: CanvasRenderingContext2D, width: number, height: number, frameCount: number) => void;

interface CanvasRendererProps {
  width: number;
  height: number;
  draw: DrawFunction;
  className?: string;
  renderMode?: 'raf' | 'scheduled'; 
  maxFps?: number; 
}

const CanvasRenderer: React.FC<CanvasRendererProps> = ({
  width,
  height,
  draw,
  className = '',
  renderMode = 'raf',
  maxFps = 60,
}) => {
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  const { canRunAnimation } = useScheduler();
  const animationFrameIdRef = React.useRef<number | null>(null);
  const frameCountRef = React.useRef(0);
  const lastRenderTimeRef = React.useRef(performance.now());

  const loop = React.useCallback((timestamp: number) => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const ctx = canvas.getContext('2d');
    assertExists(ctx, 'Canvas context must be available for drawing.');

    const deltaTime = timestamp - lastRenderTimeRef.current;
    const requiredDelta = 1000 / maxFps;

    // Throttle rendering if in 'raf' mode and maxFps is set
    if (renderMode === 'raf' && deltaTime < requiredDelta) {
      animationFrameIdRef.current = requestAnimationFrame(loop);
      return;
    }


    ctx.clearRect(0, 0, width, height);
    draw(ctx, width, height, frameCountRef.current);

    frameCountRef.current += 1;
    lastRenderTimeRef.current = timestamp;

    if (renderMode === 'raf') {
      animationFrameIdRef.current = requestAnimationFrame(loop);
    }
  }, [width, height, draw, maxFps, renderMode]);

  const scheduleRender = React.useCallback(() => {
    if (!canRunAnimation()) {
      animationFrameIdRef.current = setTimeout(scheduleRender, 1000 / 10) as unknown as number; 
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const ctx = canvas.getContext('2d');
    assertExists(ctx, 'Canvas context must be available for drawing.');


    ctx.clearRect(0, 0, width, height);
    draw(ctx, width, height, frameCountRef.current);
    frameCountRef.current += 1;
    

    animationFrameIdRef.current = requestAnimationFrame(scheduleRender);
  }, [width, height, draw, canRunAnimation]);

  React.useEffect(() => {
    // Cleanup previous loop
    if (animationFrameIdRef.current !== null) {
      if (renderMode === 'raf') {
        cancelAnimationFrame(animationFrameIdRef.current);
      } else {
        clearTimeout(animationFrameIdRef.current);
      }
      animationFrameIdRef.current = null;
    }

    if (renderMode === 'raf') {
      animationFrameIdRef.current = requestAnimationFrame(loop);
    } else if (renderMode === 'scheduled') {
      scheduleRender();
    }
    
    return () => {
      if (animationFrameIdRef.current !== null) {
        if (renderMode === 'raf') {
          cancelAnimationFrame(animationFrameIdRef.current);
        } else {
          clearTimeout(animationFrameIdRef.current);
        }
      }
    };
  }, [loop, scheduleRender, renderMode]);

  return (
    <div className={`relative ${className}`} style={{ width, height }}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="block"
      />
    </div>
  );
};

export default CanvasRenderer;