import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';

// Generate random points for the background once outside the component
const PARTICLE_POSITIONS = new Float32Array(2000 * 3);
for (let i = 0; i < 2000; i++) {
    PARTICLE_POSITIONS[i * 3] = (Math.random() - 0.5) * 10;
    PARTICLE_POSITIONS[i * 3 + 1] = (Math.random() - 0.5) * 10;
    PARTICLE_POSITIONS[i * 3 + 2] = (Math.random() - 0.5) * 10;
}

function ParticleField() {
    const ref = useRef();

    const [positions] = useMemo(() => [PARTICLE_POSITIONS], []);

    useFrame((_state, delta) => {
        if (ref.current) {
            ref.current.rotation.x += delta * 0.05;
            ref.current.rotation.y += delta * 0.03;
        }
    });

    return (
        <group rotation={[0, 0, Math.PI / 4]}>
            <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
                <PointMaterial
                    transparent
                    color="#22c55e"
                    size={0.02}
                    sizeAttenuation={true}
                    depthWrite={false}
                    opacity={0.4}
                />
            </Points>
        </group>
    );
}

export const Scene3D = () => {
    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            zIndex: -1,
            pointerEvents: 'none',
            opacity: 0.6
        }}>
            <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
                <color attach="background" args={['#050801']} />
                <ambientLight intensity={0.5} />
                <ParticleField />
            </Canvas>
            <div style={{
                position: 'absolute',
                inset: 0,
                background: 'radial-gradient(circle at center, transparent 0%, #050801 90%)'
            }} />
        </div>
    );
};
