import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { MeshDistortMaterial, Sphere, Float, PerspectiveCamera } from '@react-three/drei';

function AbstractPlant({ health = 94 }) {
    const mesh = useRef();

    // Color based on health: Green -> Yellow -> Red
    const color = health > 80 ? '#22c55e' : health > 50 ? '#eab308' : '#ef4444';
    const speed = 2 + (100 - health) / 20; // Faster vibration if low health
    const factor = 0.4 + (100 - health) / 100;

    useFrame(() => {
        if (mesh.current) {
            mesh.current.rotation.y += 0.01;
        }
    });

    return (
        <Float speed={2} rotationIntensity={1} floatIntensity={2}>
            <Sphere ref={mesh} args={[1, 64, 64]}>
                <MeshDistortMaterial
                    color={color}
                    attach="material"
                    distort={factor}
                    speed={speed}
                    roughness={0}
                    metalness={1}
                />
            </Sphere>
        </Float>
    );
}

export const DashboardModel = ({ health }) => {
    return (
        <div style={{ width: '100%', height: '200px' }}>
            <Canvas>
                <PerspectiveCamera makeDefault position={[0, 0, 4]} />
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} />
                <spotLight position={[-10, 10, 10]} angle={0.15} penumbra={1} intensity={1} />
                <AbstractPlant health={health} />
            </Canvas>
        </div>
    );
};
