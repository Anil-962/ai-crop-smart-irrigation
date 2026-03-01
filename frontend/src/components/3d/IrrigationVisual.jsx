import React, { useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { MeshWobbleMaterial, Torus, Float, PerspectiveCamera } from '@react-three/drei';

function MoistureLiquid({ moisture }) {
    const mesh = useRef();

    // Blue color intensity based on moisture
    const blueValue = Math.min(255, Math.max(100, (moisture / 100) * 255));
    const color = `rgb(37, 99, ${blueValue})`;

    const factor = moisture / 100;
    const speed = 1 + factor * 2;

    return (
        <Float speed={3} rotationIntensity={0.5} floatIntensity={0.5}>
            <Torus ref={mesh} args={[1, 0.4, 32, 100]}>
                <MeshWobbleMaterial
                    color={color}
                    factor={factor}
                    speed={speed}
                />
            </Torus>
        </Float>
    );
}

export const IrrigationVisual = ({ moisture }) => {
    return (
        <div style={{ width: '100%', height: '300px' }}>
            <Canvas>
                <PerspectiveCamera makeDefault position={[0, 0, 5]} />
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} />
                <MoistureLiquid moisture={moisture} />
            </Canvas>
        </div>
    );
};
