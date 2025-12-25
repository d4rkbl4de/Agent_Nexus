import * as React from 'react';
import * as THREE from 'three';
import { useScheduler } from '../../motion/performance/scheduler';
import { assertExists } from '../../utils/assert';

interface WebGLRendererProps {
  width: number;
  height: number;
  setupScene: (scene: THREE.Scene, camera: THREE.PerspectiveCamera | THREE.OrthographicCamera) => void;
  updateScene: (scene: THREE.Scene, renderer: THREE.WebGLRenderer, time: number, deltaTime: number, frameCount: number) => void;
  cameraType?: 'perspective' | 'orthographic';
  fov?: number; 
  near?: number;
  far?: number;
  className?: string;
  maxFps?: number; 
}

const WebGLRenderer: React.FC<WebGLRendererProps> = ({
  width,
  height,
  setupScene,
  updateScene,
  cameraType = 'perspective',
  fov = 75,
  near = 0.1,
  far = 1000,
  className = '',
  maxFps = 60,
}) => {
  const mountRef = React.useRef<HTMLDivElement>(null);
  const { canRunAnimation } = useScheduler();
  
  // Three.js object references
  const sceneRef = React.useRef<THREE.Scene | null>(null);
  const cameraRef = React.useRef<THREE.Camera | null>(null);
  const rendererRef = React.useRef<THREE.WebGLRenderer | null>(null);
  const animationFrameIdRef = React.useRef<number | null>(null);
  
  // Timing state
  const frameCountRef = React.useRef(0);
  const clockRef = React.useRef(new THREE.Clock());

  // Initialization: Setup Scene, Camera, and Renderer
  React.useEffect(() => {
    assertExists(mountRef.current, 'Mount ref must be defined.');

    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const aspectRatio = width / height;
    let camera: THREE.Camera;

    if (cameraType === 'perspective') {
      camera = new THREE.PerspectiveCamera(fov, aspectRatio, near, far);
    } else {
      camera = new THREE.OrthographicCamera(
        width / -2, width / 2, 
        height / 2, height / -2, 
        near, far
      );
    }
    cameraRef.current = camera;
    
    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    rendererRef.current = renderer;

    // Append renderer to DOM
    if (mountRef.current) {
      // Clear previous children
      while (mountRef.current.firstChild) {
        mountRef.current.removeChild(mountRef.current.firstChild);
      }
      mountRef.current.appendChild(renderer.domElement);
    }

    // Call external setup function
    setupScene(scene, camera as THREE.PerspectiveCamera | THREE.OrthographicCamera);

    return () => {
      // Dispose of Three.js objects on unmount
      if (animationFrameIdRef.current !== null) {
        cancelAnimationFrame(animationFrameIdRef.current);
      }
      renderer.dispose();
      scene.clear();
      rendererRef.current = null;
      sceneRef.current = null;
      cameraRef.current = null;
    };
  }, [width, height, setupScene, cameraType, fov, near, far]);

  // Handle resizing of the container
  React.useEffect(() => {
    if (rendererRef.current && cameraRef.current) {
      rendererRef.current.setSize(width, height);

      const camera = cameraRef.current;
      if (camera instanceof THREE.PerspectiveCamera) {
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
      } else if (camera instanceof THREE.OrthographicCamera) {
        camera.left = width / -2;
        camera.right = width / 2;
        camera.top = height / 2;
        camera.bottom = height / -2;
        camera.updateProjectionMatrix();
      }
    }
  }, [width, height]);

  // The main render loop
  const animate = React.useCallback(() => {
    animationFrameIdRef.current = requestAnimationFrame(animate);

    if (!canRunAnimation(1000 / maxFps)) {
      return; 
    }

    const scene = sceneRef.current;
    const camera = cameraRef.current;
    const renderer = rendererRef.current;
    const clock = clockRef.current;

    if (!scene || !camera || !renderer) {
      return;
    }

    const deltaTime = clock.getDelta();
    const time = clock.getElapsedTime();
    
    // Call external update function
    updateScene(scene, renderer, time, deltaTime, frameCountRef.current);

    renderer.render(scene, camera);

    frameCountRef.current += 1;
  }, [updateScene, canRunAnimation, maxFps]);

  // Start the animation loop
  React.useEffect(() => {
    // We only start the loop once the initial setup has finished
    if (rendererRef.current && cameraRef.current) {
        animationFrameIdRef.current = requestAnimationFrame(animate);
    }

    return () => {
      if (animationFrameIdRef.current !== null) {
        cancelAnimationFrame(animationFrameIdRef.current);
      }
    };
  }, [animate]);

  return (
    <div 
      ref={mountRef} 
      className={`relative overflow-hidden ${className}`} 
      style={{ width, height }} 
    />
  );
};

export default WebGLRenderer;