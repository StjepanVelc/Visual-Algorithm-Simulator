import React from 'react'
import { Layer, Line, Stage, Circle, Text, Group, Rect } from 'react-konva'
import { buildLevelLayout } from '../../hooks/useTreeLayout'

const TreeCanvas = ({ rows = [], traversalId = null }) => {
    const { positions } = buildLevelLayout(rows, 140, 110)
    const width = 1040
    const height = 520

    return (
        <div className="canvas-shell">
            <Stage width={width} height={height}>
                <Layer>
                    {rows.map((node) => {
                        if (node.parent_id == null) {
                            return null
                        }
                        const from = positions.get(node.parent_id)
                        const to = positions.get(node.id)
                        if (!from || !to) {
                            return null
                        }
                        return (
                            <Line
                                key={`edge-${node.id}`}
                                points={[from.x, from.y, to.x, to.y]}
                                stroke={Number(node.id) === Number(traversalId) ? '#ea580c' : '#64748b'}
                                strokeWidth={Number(node.id) === Number(traversalId) ? 4 : 2}
                            />
                        )
                    })}

                    {rows.map((node) => {
                        const pos = positions.get(node.id)
                        if (!pos) {
                            return null
                        }
                        const active = Number(node.id) === Number(traversalId)
                        return (
                            <Group key={`node-${node.id}`}>
                                <Rect
                                    x={pos.x - 36}
                                    y={pos.y - 22}
                                    width={72}
                                    height={44}
                                    cornerRadius={12}
                                    fill={active ? '#c2410c' : '#155e75'}
                                    shadowBlur={active ? 14 : 8}
                                    shadowColor={active ? '#ea580c' : '#155e75'}
                                    shadowOpacity={0.4}
                                />
                                <Text
                                    x={pos.x - 30}
                                    y={pos.y - 7}
                                    width={60}
                                    align="center"
                                    text={String(node.vrijednost)}
                                    fill="#ffffff"
                                    fontStyle="bold"
                                    fontSize={14}
                                />
                            </Group>
                        )
                    })}
                </Layer>
            </Stage>
        </div>
    )
}

export default TreeCanvas
