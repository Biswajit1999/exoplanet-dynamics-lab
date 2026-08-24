import { Line, OrbitControls } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { Fragment, useRef } from "react";
import type { Mesh } from "three";
import type { Simulation } from "./App";

const colors = ["#8bd3ff", "#f2c879", "#f49f7a", "#b8dd9a", "#c5acf4", "#efb9d0"];

function OrbitalScene({ simulation, playing, speed }: { simulation: Simulation; playing: boolean; speed: number }) {
  const planetRefs = useRef<Array<Mesh | null>>([]);
  const frame = useRef(0);
  const names = Object.keys(simulation.trajectories);
  const scale = 7 / Math.max(...names.map((name) => Math.max(...simulation.trajectories[name].a)));
  useFrame((_, delta) => {
    if (playing) frame.current = (frame.current + delta * speed * 12) % simulation.time_years.length;
    const index = Math.floor(frame.current);
    names.forEach((name, planetIndex) => {
      const mesh = planetRefs.current[planetIndex];
      const track = simulation.trajectories[name];
      mesh?.position.set(track.x[index] * scale, track.z[index] * scale, track.y[index] * scale);
    });
  });
  return <>
    <mesh><sphereGeometry args={[0.26, 32, 32]} /><meshBasicMaterial color="#fff2ca" /></mesh>
    {names.map((name, index) => {
      const track = simulation.trajectories[name];
      const stride = Math.max(1, Math.floor(track.x.length / 260));
      const points = track.x.filter((_, i) => i % stride === 0).map((x, i) => [x * scale, track.z[i * stride] * scale, track.y[i * stride] * scale] as [number, number, number]);
      return <Fragment key={name}>
        <Line points={points} color={colors[index % colors.length]} transparent opacity={0.42} lineWidth={1} />
        <mesh ref={(element) => { planetRefs.current[index] = element; }} aria-label={`${name} simulated position`}>
          <sphereGeometry args={[0.065 + index * 0.01, 16, 16]} />
          <meshStandardMaterial color={colors[index % colors.length]} roughness={0.7} />
        </mesh>
      </Fragment>;
    })}
  </>;
}

export default function OrbitalCanvas({ simulation, playing, speed }: { simulation: Simulation; playing: boolean; speed: number }) {
  return <Canvas camera={{ position: [0, 8, 10], fov: 43 }} aria-label={`Interactive 3D N-body model of ${simulation.system}`}>
    <ambientLight intensity={1.1} /><directionalLight position={[5, 8, 5]} intensity={1.8} />
    <OrbitalScene simulation={simulation} playing={playing} speed={speed} />
    <OrbitControls makeDefault enablePan={false} minDistance={4} maxDistance={24} />
  </Canvas>;
}
