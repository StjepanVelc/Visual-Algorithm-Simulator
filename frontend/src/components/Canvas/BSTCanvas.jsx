import React from 'react'
import { Layer, Line, Stage, Circle, Text, Group } from 'react-konva'
import { buildLevelLayout } from '../../hooks/useTreeLayout'

const BSTCanvas = ({ rows = [], traversalId = null, insertPath = [], deleteGhost = null }) => {
    const { positions } = buildLevelLayout(rows, 140, 115)
    const width = 1040
    const height = 520
    const insertPairSet = new Set()
    if (Array.isArray(insertPath)) {
        for (let i = 0; i < insertPath.length - 1; i += 1) {
            insertPairSet.add(`${insertPath[i]}->${insertPath[i + 1]}`)
        }
    }

    const ghostPos = (() => {
        if (!deleteGhost) {
            return null
        }
        const byId = positions.get(deleteGhost.id)
        if (byId) {
            return byId
        }
        const root = rows.find((node) => node.parent_id == null)
        return root ? positions.get(root.id) : { x: 90, y: 70 }
    })()

    return (
        <div className="canvas-shell">
            <Stage width={width} height={height}>
                <Layer>
                    {rows.map((node) => {
                        const from = positions.get(node.id)
                        if (!from) {
                            return null
                        }

                        const edges = []
                        if (node.lijevi_id != null && positions.has(node.lijevi_id)) {
                            const to = positions.get(node.lijevi_id)
                            edges.push(
                                <Line
                                    key={`e-${node.id}-L`}
                                    points={[from.x, from.y, to.x, to.y]}
                                    stroke={insertPairSet.has(`${node.id}->${node.lijevi_id}`) ? '#22c55e' : '#64748b'}
                                    strokeWidth={insertPairSet.has(`${node.id}->${node.lijevi_id}`) ? 4 : 2}
                                />,
                            )
                        }
                        if (node.desni_id != null && positions.has(node.desni_id)) {
                            const to = positions.get(node.desni_id)
                            edges.push(
                                <Line
                                    key={`e-${node.id}-R`}
                                    points={[from.x, from.y, to.x, to.y]}
                                    stroke={insertPairSet.has(`${node.id}->${node.desni_id}`) ? '#22c55e' : '#64748b'}
                                    strokeWidth={insertPairSet.has(`${node.id}->${node.desni_id}`) ? 4 : 2}
                                />,
                            )
                        }
                        return <Group key={`g-${node.id}`}>{edges}</Group>
                    })}

                    {rows.map((node) => {
                        const pos = positions.get(node.id)
                        if (!pos) {
                            return null
                        }
                        const active = Number(node.id) === Number(traversalId)
                        const inInsertPath = Array.isArray(insertPath) && insertPath.some((id) => Number(id) === Number(node.id))
                        return (
                            <Group key={`n-${node.id}`}>
                                <Circle
                                    x={pos.x}
                                    y={pos.y}
                                    radius={28}
                                    fill={active ? '#ea580c' : inInsertPath ? '#22c55e' : '#0f766e'}
                                    shadowBlur={active ? 16 : 8}
                                    shadowColor={active ? '#ea580c' : inInsertPath ? '#22c55e' : '#0f766e'}
                                    shadowOpacity={0.45}
                                />
                                <Text
                                    x={pos.x - 22}
                                    y={pos.y - 8}
                                    width={44}
                                    align="center"
                                    text={String(node.vrijednost)}
                                    fill="#ffffff"
                                    fontStyle="bold"
                                    fontSize={16}
                                />
                            </Group>
                        )
                    })}

                    {deleteGhost && ghostPos && (
                        <Group>
                            <Circle
                                x={ghostPos.x}
                                y={ghostPos.y}
                                radius={34}
                                stroke="#ef4444"
                                strokeWidth={4}
                                opacity={0.6}
                            />
                            <Text
                                x={ghostPos.x - 36}
                                y={ghostPos.y - 56}
                                width={72}
                                align="center"
                                text={`Deleted ${deleteGhost.value}`}
                                fill="#ef4444"
                                fontStyle="bold"
                                fontSize={13}
                            />
                        </Group>
                    )}
                </Layer>
            </Stage>
        </div>
    )
}

export default BSTCanvas
