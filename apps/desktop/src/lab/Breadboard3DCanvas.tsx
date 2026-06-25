import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import type { LabRunResult } from "../utils/api";

interface Breadboard3DCanvasProps {
  result?: LabRunResult;
  presetId?: string;
  isFetching?: boolean;
}

const DISTANCE_SCALE = 2; // 1 m of real distance -> 2 world units
const SCREEN_WORLD_HEIGHT = 1.6;
const APERTURE_WORLD_HEIGHT = 0.8;

interface Rgb {
  r: number;
  g: number;
  b: number;
}

function wavelengthToRgb(wavelength_nm: number): Rgb {
  const w = wavelength_nm;
  let r = 0;
  let g = 0;
  let b = 0;
  if (w < 440) {
    r = Math.round(((440 - w) / (440 - 380)) * 255);
    g = 0;
    b = 255;
  } else if (w < 490) {
    r = 0;
    g = Math.round(((w - 440) / (490 - 440)) * 255);
    b = 255;
  } else if (w < 510) {
    r = 0;
    g = 255;
    b = Math.round(((510 - w) / (510 - 490)) * 255);
  } else if (w < 580) {
    r = Math.round(((w - 510) / (580 - 510)) * 255);
    g = 255;
    b = 0;
  } else if (w < 645) {
    r = 255;
    g = Math.round(((645 - w) / (645 - 580)) * 255);
    b = 0;
  } else {
    r = 255;
    g = 0;
    b = Math.round(((w - 645) / (700 - 645)) * 255);
  }
  return {
    r: Math.max(0, Math.min(255, r)),
    g: Math.max(0, Math.min(255, g)),
    b: Math.max(0, Math.min(255, b)),
  };
}

function createScreenTexture(
  samples: Array<{ y_mm: number; intensity: number }> | undefined,
  color: Rgb
): THREE.CanvasTexture {
  const canvas = document.createElement("canvas");
  const width = 64;
  const height = samples?.length ?? 256;
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d")!;

  // Black background
  ctx.fillStyle = "#000000";
  ctx.fillRect(0, 0, width, height);

  if (samples && samples.length > 0) {
    for (let row = 0; row < samples.length; row++) {
      const intensity = samples[row].intensity;
      const alpha = intensity;
      ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${alpha})`;
      ctx.fillRect(0, height - 1 - row, width, 1);
    }
  } else {
    // Fallback central spot
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, "rgba(0,0,0,0)");
    gradient.addColorStop(0.5, `rgba(${color.r}, ${color.g}, ${color.b}, 1)`);
    gradient.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.needsUpdate = true;
  return texture;
}

function createApertureTexture(
  isDoubleSlit: boolean,
  slitWidthUm: number,
  slitSeparationUm: number
): THREE.CanvasTexture {
  const canvas = document.createElement("canvas");
  const width = 128;
  const height = 256;
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d")!;

  // Opaque plate
  ctx.fillStyle = "#1e293b";
  ctx.fillRect(0, 0, width, height);

  // Clear slit regions (transparent)
  ctx.globalCompositeOperation = "destination-out";

  // Visual mapping: keep slits within the middle 60% of the plate
  const visualHeight = height * 0.6;
  const centerY = height / 2;
  const topY = centerY - visualHeight / 2;

  // Scale: map up to 200 μm slit width / 1000 μm separation to the visual height
  const maxWidthUm = 200;
  const maxSepUm = 1000;
  const widthScale = Math.min(1, slitWidthUm / maxWidthUm);
  const sepScale = Math.min(1, slitSeparationUm / maxSepUm);

  const slitH = Math.max(4, visualHeight * 0.15 * widthScale);
  const gap = Math.max(slitH + 4, visualHeight * 0.4 * sepScale);

  const slitW = width * 0.6;
  const slitX = (width - slitW) / 2;

  if (isDoubleSlit) {
    const topSlitY = topY + visualHeight * 0.35 - gap / 2 - slitH / 2;
    const bottomSlitY = topY + visualHeight * 0.35 + gap / 2 + slitH / 2;
    ctx.fillRect(slitX, topSlitY, slitW, slitH);
    ctx.fillRect(slitX, bottomSlitY, slitW, slitH);
  } else {
    const slitY = topY + visualHeight * 0.35 - slitH / 2;
    ctx.fillRect(slitX, slitY, slitW, slitH);
  }

  ctx.globalCompositeOperation = "source-over";

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.needsUpdate = true;
  return texture;
}

export function Breadboard3DCanvas({
  result,
  presetId,
  isFetching,
}: Breadboard3DCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const rafRef = useRef<number | null>(null);

  const beamRef = useRef<THREE.Mesh | null>(null);
  const screenRef = useRef<THREE.Mesh | null>(null);
  const apertureRef = useRef<THREE.Mesh | null>(null);
  const laserMatRef = useRef<THREE.MeshStandardMaterial | null>(null);

  const screenTextureRef = useRef<THREE.CanvasTexture | null>(null);
  const apertureTextureRef = useRef<THREE.CanvasTexture | null>(null);

  const isDoubleSlit = presetId === "double-slit-breadboard";

  // Initialize scene once
  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8fafc);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 1.4, 4.5);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.target.set(0.8, 0, 0);
    controlsRef.current = controls;

    // Lights
    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
    dirLight.position.set(2, 3, 2);
    scene.add(dirLight);

    // Optical table grid
    const grid = new THREE.GridHelper(10, 20, 0x94a3b8, 0xe2e8f0);
    scene.add(grid);

    // Laser source
    const laserGeo = new THREE.BoxGeometry(0.3, 0.18, 0.18);
    const laserMat = new THREE.MeshStandardMaterial({
      color: 0x334155,
      roughness: 0.5,
      metalness: 0.3,
    });
    const laser = new THREE.Mesh(laserGeo, laserMat);
    laser.position.set(-0.5, 0, 0);
    scene.add(laser);
    laserMatRef.current = laserMat;

    // Laser emitter tip (glow)
    const emitterGeo = new THREE.CircleGeometry(0.06, 16);
    const emitterMat = new THREE.MeshBasicMaterial({ color: 0x000000 });
    const emitter = new THREE.Mesh(emitterGeo, emitterMat);
    emitter.position.set(-0.35, 0, 0);
    emitter.rotation.y = Math.PI / 2;
    scene.add(emitter);

    // Beam cone (from aperture toward screen)
    const beamGeo = new THREE.ConeGeometry(0.1, 1, 32, 1, true);
    const beamMat = new THREE.MeshBasicMaterial({
      color: 0xff0000,
      transparent: true,
      opacity: 0.12,
      side: THREE.DoubleSide,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    const beam = new THREE.Mesh(beamGeo, beamMat);
    beam.rotation.z = -Math.PI / 2;
    scene.add(beam);
    beamRef.current = beam;

    // Aperture plate
    const apertureGeo = new THREE.PlaneGeometry(APERTURE_WORLD_HEIGHT * 0.75, APERTURE_WORLD_HEIGHT);
    const apertureMat = new THREE.MeshBasicMaterial({
      color: 0x1e293b,
      transparent: true,
      alphaTest: 0.1,
    });
    const aperture = new THREE.Mesh(apertureGeo, apertureMat);
    aperture.position.set(0, 0, 0);
    aperture.rotation.y = Math.PI / 2;
    scene.add(aperture);
    apertureRef.current = aperture;

    // Screen
    const screenGeo = new THREE.PlaneGeometry(SCREEN_WORLD_HEIGHT * 0.5, SCREEN_WORLD_HEIGHT);
    const screenMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const screen = new THREE.Mesh(screenGeo, screenMat);
    screen.rotation.y = -Math.PI / 2;
    scene.add(screen);
    screenRef.current = screen;

    const animate = () => {
      rafRef.current = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!containerRef.current || !cameraRef.current || !rendererRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      cameraRef.current.aspect = w / h;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      controls.dispose();
      renderer.dispose();
      if (renderer.domElement.parentNode === container) {
        container.removeChild(renderer.domElement);
      }
      scene.traverse((obj) => {
        if (obj instanceof THREE.Mesh) {
          obj.geometry.dispose();
          const mat = obj.material;
          if (Array.isArray(mat)) {
            mat.forEach((m) => m.dispose());
          } else {
            mat.dispose();
          }
        }
      });
      screenTextureRef.current?.dispose();
      apertureTextureRef.current?.dispose();
    };
  }, [isDoubleSlit]);

  // Update scene when result changes
  useEffect(() => {
    if (!result?.data || !screenRef.current || !beamRef.current || !apertureRef.current) return;

    const data = result.data;
    const wavelength_nm = Number(data.wavelength_nm ?? 550);
    const screen_distance_m = Number(data.screen_distance_m ?? 1);
    const slit_width_um = Number(data.slit_width_um ?? 50);
    const slit_separation_um = isDoubleSlit
      ? Number(data.slit_separation_um ?? 100)
      : 0;
    const rgb = wavelengthToRgb(wavelength_nm);
    const color = new THREE.Color(`rgb(${rgb.r},${rgb.g},${rgb.b})`);

    // Update laser glow
    if (laserMatRef.current) {
      laserMatRef.current.emissive = color;
      laserMatRef.current.emissiveIntensity = 0.6;
    }

    // Update screen position
    const screenX = 0.2 + screen_distance_m * DISTANCE_SCALE;
    screenRef.current.position.set(screenX, 0, 0);

    // Update beam geometry
    const beamMat = beamRef.current.material as THREE.MeshBasicMaterial;
    beamMat.color = color;
    const beamLength = Math.max(0.2, screenX);
    const beamRadius = (SCREEN_WORLD_HEIGHT / 2) * 0.85;
    beamRef.current.geometry.dispose();
    beamRef.current.geometry = new THREE.ConeGeometry(beamRadius, beamLength, 32, 1, true);
    beamRef.current.position.set(screenX / 2, 0, 0);

    // Update controls target to keep scene centered
    if (controlsRef.current) {
      controlsRef.current.target.set(screenX / 2, 0, 0);
      controlsRef.current.update();
    }

    // Update aperture texture
    const newApertureTex = createApertureTexture(isDoubleSlit, slit_width_um, slit_separation_um);
    const apertureMat = apertureRef.current.material as THREE.MeshBasicMaterial;
    if (apertureTextureRef.current) apertureTextureRef.current.dispose();
    apertureTextureRef.current = newApertureTex;
    apertureMat.map = newApertureTex;
    apertureMat.alphaMap = newApertureTex;
    apertureMat.transparent = true;
    apertureMat.alphaTest = 0.1;
    apertureMat.needsUpdate = true;

    // Update screen texture
    const samples = data.intensity_samples as
      | Array<{ y_mm: number; intensity: number }>
      | undefined;
    const newScreenTex = createScreenTexture(samples, rgb);
    const screenMat = screenRef.current.material as THREE.MeshBasicMaterial;
    if (screenTextureRef.current) screenTextureRef.current.dispose();
    screenTextureRef.current = newScreenTex;
    screenMat.map = newScreenTex;
    screenMat.needsUpdate = true;
  }, [result, isDoubleSlit]);

  return (
    <div
      ref={containerRef}
      className={`relative h-96 w-full overflow-hidden rounded-lg border border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-900 ${
        isFetching ? "opacity-70" : "opacity-100"
      } transition-opacity duration-200`}
    >
      {isFetching && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-300 border-t-indigo-500" />
        </div>
      )}
    </div>
  );
}
