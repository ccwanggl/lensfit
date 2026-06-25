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
  const width = samples?.length ?? 256;
  const height = 64;
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d")!;

  // Black background
  ctx.fillStyle = "#000000";
  ctx.fillRect(0, 0, width, height);

  if (samples && samples.length > 0) {
    // Intensity varies horizontally so it maps to the screen's width axis
    // (perpendicular to the vertical slit), producing vertical bright/dark fringes.
    for (let col = 0; col < samples.length; col++) {
      const intensity = samples[col].intensity;
      // Gamma boost so faint side lobes remain visible on the 3D screen.
      const alpha = Math.max(0, Math.min(1, intensity ** 0.45));
      ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${alpha})`;
      ctx.fillRect(col, 0, 1, height);
    }
  } else {
    // Fallback central spot
    const gradient = ctx.createLinearGradient(0, 0, width, 0);
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

function drawIntensityMonitor(
  canvas: HTMLCanvasElement,
  samples: Array<{ y_mm: number; intensity: number }>,
  color: Rgb
) {
  const cssWidth = 200;
  const cssHeight = 100;
  const dpr = Math.min(window.devicePixelRatio, 2);
  canvas.width = cssWidth * dpr;
  canvas.height = cssHeight * dpr;
  canvas.style.width = `${cssWidth}px`;
  canvas.style.height = `${cssHeight}px`;

  const ctx = canvas.getContext("2d")!;
  ctx.scale(dpr, dpr);

  // Oscilloscope-style dark background
  ctx.fillStyle = "#020617";
  ctx.fillRect(0, 0, cssWidth, cssHeight);

  // Grid
  ctx.strokeStyle = "rgba(148, 163, 184, 0.2)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  for (let x = 0; x <= cssWidth; x += 40) {
    ctx.moveTo(x, 0);
    ctx.lineTo(x, cssHeight);
  }
  for (let y = 0; y <= cssHeight; y += 25) {
    ctx.moveTo(0, y);
    ctx.lineTo(cssWidth, y);
  }
  ctx.stroke();

  if (samples.length === 0) return;

  const yMin = samples[0].y_mm;
  const yMax = samples[samples.length - 1].y_mm;
  const pad = 6;
  const plotW = cssWidth - 2 * pad;
  const plotH = cssHeight - 2 * pad;

  const xFor = (y_mm: number) =>
    pad + ((y_mm - yMin) / (yMax - yMin)) * plotW;
  const yFor = (intensity: number) =>
    pad + plotH - Math.min(1, intensity ** 0.45) * plotH;

  // Glow fill under curve
  const gradient = ctx.createLinearGradient(0, pad, 0, cssHeight - pad);
  gradient.addColorStop(0, `rgba(${color.r}, ${color.g}, ${color.b}, 0.55)`);
  gradient.addColorStop(1, `rgba(${color.r}, ${color.g}, ${color.b}, 0.05)`);

  ctx.beginPath();
  ctx.moveTo(xFor(samples[0].y_mm), cssHeight - pad);
  for (const s of samples) {
    ctx.lineTo(xFor(s.y_mm), yFor(s.intensity));
  }
  ctx.lineTo(xFor(samples[samples.length - 1].y_mm), cssHeight - pad);
  ctx.closePath();
  ctx.fillStyle = gradient;
  ctx.fill();

  // Curve outline
  ctx.beginPath();
  for (const s of samples) {
    ctx.lineTo(xFor(s.y_mm), yFor(s.intensity));
  }
  ctx.strokeStyle = `rgb(${color.r}, ${color.g}, ${color.b})`;
  ctx.lineWidth = 1.5;
  ctx.stroke();

  // Labels
  ctx.fillStyle = "#94a3b8";
  ctx.font = "10px sans-serif";
  ctx.fillText("相对强度", pad + 2, pad + 10);
  ctx.fillText(`${yMin.toFixed(2)} mm`, pad, cssHeight - 4);
  ctx.fillText(`${yMax.toFixed(2)} mm`, cssWidth - pad - 45, cssHeight - 4);
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

  // Clear transparent background first
  ctx.clearRect(0, 0, width, height);

  // Opaque plate with transparent slits
  ctx.fillStyle = "#1e293b";
  ctx.fillRect(0, 0, width, height);

  // Clear slit regions (transparent)
  ctx.globalCompositeOperation = "destination-out";

  // Visual mapping: slits are vertical (tall rectangles) and, for double-slit,
  // separated horizontally.
  const visualWidth = width * 0.6;
  const centerX = width / 2;
  const centerY = height / 2;
  const slitH = height * 0.6;

  // Scale: map up to 200 μm slit width / 1000 μm separation to the visual width
  const maxWidthUm = 200;
  const maxSepUm = 1000;
  const widthScale = Math.min(1, slitWidthUm / maxWidthUm);
  const sepScale = Math.min(1, slitSeparationUm / maxSepUm);

  const slitW = Math.max(4, visualWidth * 0.12 * widthScale);
  const gap = Math.max(slitW + 8, visualWidth * 0.45 * sepScale);

  if (isDoubleSlit) {
    const leftSlitX = centerX - gap / 2 - slitW / 2;
    const rightSlitX = centerX + gap / 2 - slitW / 2;
    ctx.fillRect(leftSlitX, centerY - slitH / 2, slitW, slitH);
    ctx.fillRect(rightSlitX, centerY - slitH / 2, slitW, slitH);
  } else {
    const slitX = centerX - slitW / 2;
    ctx.fillRect(slitX, centerY - slitH / 2, slitW, slitH);
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
  const monitorRef = useRef<HTMLCanvasElement>(null);

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
    camera.position.set(2.5, 1.5, 2.5);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.target.set(0.6, 0, 0);
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
      opacity: 0.22,
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
      transparent: true,
      side: THREE.DoubleSide,
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

    // Update camera and controls target to keep both aperture and screen in view
    if (cameraRef.current && controlsRef.current) {
      cameraRef.current.position.set(screenX + 1.5, 1.5, 2.0);
      controlsRef.current.target.set(screenX / 2, 0, 0);
      controlsRef.current.update();
    }

    // Update aperture texture
    const newApertureTex = createApertureTexture(isDoubleSlit, slit_width_um, slit_separation_um);
    const apertureMat = apertureRef.current.material as THREE.MeshBasicMaterial;
    if (apertureTextureRef.current) apertureTextureRef.current.dispose();
    apertureTextureRef.current = newApertureTex;
    apertureMat.map = newApertureTex;
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

    // Update oscilloscope-style monitor overlay
    if (monitorRef.current && samples && samples.length > 0) {
      drawIntensityMonitor(monitorRef.current, samples, rgb);
    }
  }, [result, isDoubleSlit]);

  return (
    <div
      ref={containerRef}
      className={`relative h-96 w-full overflow-hidden rounded-lg border border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-900 ${
        isFetching ? "opacity-70" : "opacity-100"
      } transition-opacity duration-200`}
    >
      <canvas
        ref={monitorRef}
        className="absolute right-2 top-2 z-10 rounded border border-slate-700/50 bg-slate-950 shadow-lg"
        width={200}
        height={100}
      />
      {isFetching && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-300 border-t-indigo-500" />
        </div>
      )}
    </div>
  );
}
