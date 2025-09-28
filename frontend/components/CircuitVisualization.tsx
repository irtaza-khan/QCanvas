'use client'

import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

interface Gate {
  type: string
  qubit: number
  control?: number
  target?: number
  angle?: number
  name?: string
}

interface CircuitVisualizationProps {
  gates: Gate[]
  qubits: number
  className?: string
}

export default function CircuitVisualization({ gates, qubits, className = '' }: CircuitVisualizationProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || gates.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove() // Clear previous content

    const margin = { top: 20, right: 20, bottom: 20, left: 60 }
    const width = Math.max(600, gates.length * 80 + margin.left + margin.right)
    const height = qubits * 60 + margin.top + margin.bottom
    const qubitSpacing = 60
    const gateSpacing = 80

    svg.attr('width', width).attr('height', height)

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    // Draw qubit lines
    for (let i = 0; i < qubits; i++) {
      const y = i * qubitSpacing + 30
      
      // Qubit line
      g.append('line')
        .attr('x1', 0)
        .attr('y1', y)
        .attr('x2', width - margin.left - margin.right)
        .attr('y2', y)
        .attr('stroke', '#4B5563')
        .attr('stroke-width', 2)

      // Qubit label
      g.append('text')
        .attr('x', -10)
        .attr('y', y + 5)
        .attr('text-anchor', 'end')
        .attr('fill', '#9CA3AF')
        .attr('font-family', 'monospace')
        .attr('font-size', '14px')
        .text(`q${i}`)
    }

    // Draw gates
    gates.forEach((gate, gateIndex) => {
      const x = gateIndex * gateSpacing + 40
      const y = gate.qubit * qubitSpacing + 30

      switch (gate.type) {
        case 'h':
        case 'hadamard':
          drawHGate(g, x, y, gate.name || 'H')
          break
        case 'x':
        case 'pauli-x':
          drawXGate(g, x, y)
          break
        case 'y':
        case 'pauli-y':
          drawYGate(g, x, y)
          break
        case 'z':
        case 'pauli-z':
          drawZGate(g, x, y)
          break
        case 'cx':
        case 'cnot':
          if (gate.control !== undefined && gate.target !== undefined) {
            drawCNOTGate(g, x, gate.control * qubitSpacing + 30, gate.target * qubitSpacing + 30)
          }
          break
        case 'cz':
          if (gate.control !== undefined && gate.target !== undefined) {
            drawCZGate(g, x, gate.control * qubitSpacing + 30, gate.target * qubitSpacing + 30)
          }
          break
        case 'rz':
        case 'ry':
        case 'rx':
          drawRotationGate(g, x, y, gate.type.toUpperCase(), gate.angle)
          break
        case 'measure':
          drawMeasurementGate(g, x, y)
          break
        default:
          drawGenericGate(g, x, y, gate.type.toUpperCase())
      }
    })

    function drawHGate(g: d3.Selection<SVGGElement, unknown, null, undefined>, x: number, y: number, label: string) {
      g.append('rect')
        .attr('x', x - 15)
        .attr('y', y - 15)
        .attr('width', 30)
        .attr('height', 30)
        .attr('fill', '#3B82F6')
        .attr('stroke', '#1D4ED8')
        .attr('stroke-width', 2)
        .attr('rx', 4)

      g.append('text')
        .attr('x', x)
        .attr('y', y + 5)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .attr('font-family', 'monospace')
        .attr('font-size', '14px')
        .attr('font-weight', 'bold')
        .text(label)
    }

    function drawXGate(g: d3.Selection<SVGGElement, unknown, null, undefined>, x: number, y: number) {
      g.append('circle')
        .attr('cx', x)
        .attr('cy', y)
        .attr('r', 15)
        .attr('fill', '#EF4444')
        .attr('stroke', '#DC2626')
        .attr('stroke-width', 2)

      g.append('text')
        .attr('x', x)
        .attr('y', y + 5)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .attr('font-family', 'monospace')
        .attr('font-size', '14px')
        .attr('font-weight', 'bold')
        .text('X')
    }

    function drawYGate(g: d3.Selection<SVGGElement, unknown, null, undefined>, x: number, y: number) {
      g.append('circle')
        .attr('cx', x)
        .attr('cy', y)
        .attr('r', 15)
        .attr('fill', '#10B981')
        .attr('stroke', '#059669')
        .attr('stroke-width', 2)

      g.append('text')
        .attr('x', x)
        .attr('y', y + 5)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .attr('font-family', 'monospace')
        .attr('font-size', '14px')
        .attr('font-weight', 'bold')
        .text('Y')
    }

    function drawZGate(g: d3.Selection<SVGGElement, unknown, null, undefined>, x: number, y: number) {
      g.append('circle')
        .attr('cx', x)
        .attr('cy', y)
        .attr('r', 15)
        .attr('fill', '#8B5CF6')
        .attr('stroke', '#7C3AED')
        .attr('stroke-width', 2)

      g.append('text')
        .attr('x', x)
        .attr('y', y + 5)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .attr('font-family', 'monospace')
        .attr('font-size', '14px')
        .attr('font-weight', 'bold')
        .text('Z')
    }

    function drawCNOTGate(g: d3.Selection<SVGGElement, unknown, null, undefined>, x: number, controlY: number, targetY: number) {
      // Control dot
      g.append('circle')
        .attr('cx', x)
        .attr('cy', controlY)
        .attr('r', 6)
        .attr('fill', '#1F2937')
        .attr('stroke', '#6B7280')
        .attr('stroke-width', 2)

      // Connecting line
      g.append('line')
        .attr('x1', x)
        .attr('y1', controlY)
        .attr('x2', x)
        .attr('y2', targetY)
        .attr('stroke', '#6B7280')
        .attr('stroke-width', 2)

      // Target (X gate)
      g.append('circle')
        .attr('cx', x)
        .attr('cy', targetY)
        .attr('r', 15)
        .attr('fill', 'none')
        .attr('stroke', '#6B7280')
        .attr('stroke-width', 2)

      // X symbol on target
      g.append('line')
        .attr('x1', x - 8)
        .attr('y1', targetY - 8)
        .attr('x2', x + 8)
        .attr('y2', targetY + 8)
        .attr('stroke', '#6B7280')
        .attr('stroke-width', 2)

      g.append('line')
        .attr('x1', x - 8)
        .attr('y1', targetY + 8)
        .attr('x2', x + 8)
        .attr('y2', targetY - 8)
        .attr('stroke', '#6B7280')
        .attr('stroke-width', 2)
    }

    function drawCZGate(g: d3.Selection<SVGGElement, unknown, null, undefined>, x: number, controlY: number, targetY: number) {
      // Control dot
      g.append('circle')
        .attr('cx', x)
        .attr('cy', controlY)
        .attr('r', 6)
        .attr('fill', '#1F2937')
        .attr('stroke', '#6B7280')
        .attr('stroke-width', 2)

      // Connecting line
      g.append('line')
        .attr('x1', x)
        .attr('y1', controlY)
        .attr('x2', x)
        .attr('y2', targetY)
        .attr('stroke', '#6B7280')
        .attr('stroke-width', 2)

      // Target (Z gate)
      g.append('circle')
        .attr('cx', x)
        .attr('cy', targetY)
        .attr('r', 6)
        .attr('fill', '#1F2937')
        .attr('stroke', '#6B7280')
        .attr('stroke-width', 2)
    }

    function drawRotationGate(g: d3.Selection<SVGGElement, unknown, null, undefined>, x: number, y: number, label: string, angle?: number) {
      g.append('rect')
        .attr('x', x - 20)
        .attr('y', y - 15)
        .attr('width', 40)
        .attr('height', 30)
        .attr('fill', '#F59E0B')
        .attr('stroke', '#D97706')
        .attr('stroke-width', 2)
        .attr('rx', 4)

      g.append('text')
        .attr('x', x)
        .attr('y', y + 2)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .attr('font-family', 'monospace')
        .attr('font-size', '12px')
        .attr('font-weight', 'bold')
        .text(label)

      if (angle !== undefined) {
        g.append('text')
          .attr('x', x)
          .attr('y', y + 12)
          .attr('text-anchor', 'middle')
          .attr('fill', 'white')
          .attr('font-family', 'monospace')
          .attr('font-size', '8px')
          .text(`(${angle.toFixed(2)})`)
      }
    }

    function drawMeasurementGate(g: d3.Selection<SVGGElement, unknown, null, undefined>, x: number, y: number) {
      // Measurement box
      g.append('rect')
        .attr('x', x - 15)
        .attr('y', y - 15)
        .attr('width', 30)
        .attr('height', 30)
        .attr('fill', '#6B7280')
        .attr('stroke', '#4B5563')
        .attr('stroke-width', 2)
        .attr('rx', 4)

      // Measurement arc
      const arc = d3.arc()
        .innerRadius(0)
        .outerRadius(8)
        .startAngle(0)
        .endAngle(Math.PI)

      g.append('path')
        .attr('d', arc as any)
        .attr('transform', `translate(${x}, ${y + 5})`)
        .attr('fill', 'white')

      // Measurement line
      g.append('line')
        .attr('x1', x)
        .attr('y1', y + 5)
        .attr('x2', x + 6)
        .attr('y2', y - 5)
        .attr('stroke', 'white')
        .attr('stroke-width', 2)
    }

    function drawGenericGate(g: d3.Selection<SVGGElement, unknown, null, undefined>, x: number, y: number, label: string) {
      g.append('rect')
        .attr('x', x - 15)
        .attr('y', y - 15)
        .attr('width', 30)
        .attr('height', 30)
        .attr('fill', '#6B7280')
        .attr('stroke', '#4B5563')
        .attr('stroke-width', 2)
        .attr('rx', 4)

      g.append('text')
        .attr('x', x)
        .attr('y', y + 5)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .attr('font-family', 'monospace')
        .attr('font-size', '10px')
        .attr('font-weight', 'bold')
        .text(label)
    }
  }, [gates, qubits])

  if (gates.length === 0) {
    return (
      <div className={`flex items-center justify-center h-32 border-2 border-dashed border-gray-600 rounded-lg ${className}`}>
        <p className="text-gray-400 text-sm">No circuit to visualize</p>
      </div>
    )
  }

  return (
    <div className={`overflow-x-auto ${className}`}>
      <svg ref={svgRef} className="min-w-full"></svg>
    </div>
  )
}
