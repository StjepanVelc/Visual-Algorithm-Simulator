import React from 'react'
import { Layer, Line, Stage, Circle, Text, Group, Rect } from 'react-konva'
import { buildLevelLayout } from '../../hooks/useTreeLayout'
import { useCanvasViewport } from '../../hooks/useCanvasViewport'

const TreeCanvas = ({ rows = [], traversalId = null }) => {
    const { positions } = buildLevelLayout(rows, 140, 110)
    const {
        shellRef,
        viewport,
        transform,
        setTransform,
        fitToContent,
        zoomIn,
        zoomOut,
    } = useCanvasViewport(positions, {
        nodeRadius: 40,
        defaultHeight: 560,
    })

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
