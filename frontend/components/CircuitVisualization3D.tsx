'use client'

import { useRef, useState, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Text, RoundedBox, Line } from '@react-three/drei'
import * as THREE from 'three'

interface Gate {
  type: string
  qubit: number
  control?: number
  target?: number
  angle?: number
  name?: string
}

interface CircuitVisualization3DProps {
  gates: Gate[]
  qubits: number
  className?: string
}

// Color mapping (matching 2D visualization)
const getGateColor = (gateType: string): string => {
  const type = gateType.toLowerCase()
  const colors: Record<string, string> = {
    h: '#3B82F6', // Blue
    x: '#EF4444', // Red
    y: '#10B981', // Green
    z: '#8B5CF6', // Purple
    s: '#06B6D4', // Cyan
    t: '#14B8A6', // Teal
    rx: '#F59E0B', // Amber
    ry: '#F59E0B',
    rz: '#F59E0B',
    p: '#F59E0B',
    measure: '#6B7280', // Gray
    cx: '#6B7280', // Control line color
    swap: '#6B7280',
  }
  return colors[type] || '#9CA3AF'
}

const GateLabel = ({ position, text }: { position: [number, number, number], text: string }) => {
  return (
    <Text
      position={[position[0], position[1], position[2] + 0.6]}
      fontSize={0.5}
      color="white"
      anchorX="center"
      anchorY="middle"
    >
      {text}
    </Text>
  )
}

const Gate3D = ({ gate, x, y, qubitSpacing }: { gate: Gate, x: number, y: number, qubitSpacing: number }) => {
  const [hovered, setHovered] = useState(false)
  const color = getGateColor(gate.type)
  const type = gate.type.toLowerCase()

  // Handle multi-qubit gates (CNOT, SWAP, CZ)
  if (type === 'cx' || type === 'cnot' || type === 'cz' || type === 'swap') {
    if (gate.control !== undefined && gate.target !== undefined) {
      const controlY = -(gate.control * qubitSpacing)
      const targetY = -(gate.target * qubitSpacing)
      const midY = (controlY + targetY) / 2
      const height = Math.abs(controlY - targetY)

      return (
        <group position={[x, 0, 0]}>
          {/* Control Dot */}
          <mesh position={[0, controlY, 0]}>
            <sphereGeometry args={[0.3, 32, 32]} />
            <meshStandardMaterial color={hovered ? '#ffffff' : color} />
          </mesh>
          
          {/* Target Symbol (X for CNOT, Dot for CZ) */}
          <mesh
            position={[0, targetY, 0]}
            rotation={type === 'cz' ? [0, 0, 0] : [Math.PI / 2, 0, 0]}
            onPointerOver={() => setHovered(true)}
            onPointerOut={() => setHovered(false)}
          >
            {type === 'cz' ? (
              <sphereGeometry args={[0.3, 32, 32]} />
            ) : (
              <cylinderGeometry args={[0.3, 0.3, 0.1, 32]} />
            )}
            <meshStandardMaterial color={hovered ? '#ffffff' : color} />
          </mesh>

          {/* Vertical Line */}
          <mesh position={[0, midY, 0]}>
            <cylinderGeometry args={[0.05, 0.05, height, 8]} />
            <meshStandardMaterial color={color} />
          </mesh>
        </group>
      )
    }
  }

  // Single Qubit Gates
  return (
    <group position={[x, y, 0]}>
      <RoundedBox
        args={[0.8, 0.8, 0.8]} // Width, Height, Depth
        radius={0.1}
        smoothness={4}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <meshStandardMaterial color={hovered ? '#ffffff' : color} />
      </RoundedBox>
      <GateLabel position={[0, 0, 0]} text={gate.name || gate.type.substring(0, 2).toUpperCase()} />
    </group>
  )
}

const QubitLine = ({ y, length, label }: { y: number, length: number, label: string }) => {
  return (
    <group position={[0, y, 0]}>
      {/* Label */}
       <Text
        position={[-2, 0, 0]}
        fontSize={0.5}
        color="#9CA3AF"
        anchorX="right"
        anchorY="middle"
      >
        {label}
      </Text>
      
      {/* Wire */}
      <mesh position={[length / 2 - 1, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.02, 0.02, length + 2, 8]} />
        <meshStandardMaterial color="#4B5563" />
      </mesh>
    </group>
  )
}

const CircuitScene = ({ gates, qubits }: { gates: Gate[], qubits: number }) => {
  const gateSpacing = 1.5
  const qubitSpacing = 1.5
  const circuitLength = Math.max(10, gates.length * gateSpacing)

  return (
    <group position={[-circuitLength / 2 + 2, (qubits * qubitSpacing) / 2 - 1, 0]}>
      {/* Draw Qubit Lines */}
      {Array.from({ length: qubits }).map((_, i) => (
        <QubitLine 
            key={`qubit-${i}`} 
            y={-(i * qubitSpacing)} 
            length={circuitLength} 
            label={`q${i}`} 
        />
      ))}

      {/* Draw Gates */}
      {gates.map((gate, i) => (
        <Gate3D
          key={`gate-${i}`}
          gate={gate}
          x={i * gateSpacing}
          y={-(gate.qubit * qubitSpacing)}
          qubitSpacing={qubitSpacing}
        />
      ))}
    </group>
  )
}

export default function CircuitVisualization3D({ gates, qubits, className = '' }: CircuitVisualization3DProps) {
  return (
    <div className={`relative ${className}`}>
      {gates.length === 0 ? (
        <div className="flex items-center justify-center h-full border-2 border-dashed border-gray-600 rounded-lg">
          <p className="text-gray-400 text-sm">No circuit to visualize</p>
        </div>
      ) : (
        <Canvas camera={{ position: [5, 5, 10], fov: 50 }}>
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} intensity={1} />
            <spotLight position={[-10, 10, 10]} angle={0.3} penumbra={1} intensity={1} />
            <CircuitScene gates={gates} qubits={qubits} />
            <OrbitControls makeDefault />

        </Canvas>
      )}
      
      {/* Overlay Instructions */}
      <div className="absolute bottom-4 right-4 bg-black/70 text-white text-xs px-2 py-1 rounded">
        Drag to rotate • Scroll to zoom • Right-click pan
      </div>
    </div>
  )
}
