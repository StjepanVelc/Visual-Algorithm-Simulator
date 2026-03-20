import React from 'react'
import { Layer, Line, Stage, Circle, Text, Group } from 'react-konva'
import { buildLevelLayout } from '../../hooks/useTreeLayout'
import { useCanvasViewport } from '../../hooks/useCanvasViewport'

const BSTCanvas = ({ rows = [], traversalId = null, insertPath = [], deleteGhost = null }) => {
    const { positions } = buildLevelLayout(rows, 140, 115)
    const {
        shellRef,
        viewport,
        transform,
        setTransform,
        fitToContent,
        zoomIn,
        zoomOut,
    } = useCanvasViewport(positions, {
        nodeRadius: 38,
        defaultHeight: 560,
    })
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
        <div className="canvas-shell" ref={shellRef}>
            <div className="canvas-toolbar">
                <button type="button" onClick={zoomOut}>-</button>
                <button type="button" onClick={zoomIn}>+</button>
                <button type="button" onClick={fitToContent}>Fit Tree</button>
            </div>
            <Stage
                width={viewport.width}
                height={viewport.height}
                draggable
                onDragEnd={(e) => {
                    const pos = e.target.position()
                    setTransform((prev) => ({ ...prev, x: pos.x, y: pos.y }))
                }}
                onWheel={(e) => {
                    e.evt.preventDefault()
                    const stage = e.target.getStage()
                    if (!stage) {
                        return
                    }

                    const oldScale = transform.scale
                    const pointer = stage.getPointerPosition()
                    if (!pointer) {
                        return
                    }

                    const pointerLocal = {
                        x: (pointer.x - transform.x) / oldScale,
                        y: (pointer.y - transform.y) / oldScale,
                    }

                    const scaleBy = 1.08
                    const direction = e.evt.deltaY > 0 ? -1 : 1
                    const nextScaleRaw = direction > 0 ? oldScale * scaleBy : oldScale / scaleBy
                    const nextScale = Math.max(0.35, Math.min(2.4, nextScaleRaw))

                    setTransform({
                        scale: nextScale,
                        x: pointer.x - pointerLocal.x * nextScale,
                        y: pointer.y - pointerLocal.y * nextScale,
                    })
                }}
                scaleX={transform.scale}
                scaleY={transform.scale}
                x={transform.x}
                y={transform.y}
            >
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
