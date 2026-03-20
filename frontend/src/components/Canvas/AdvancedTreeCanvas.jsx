import React, { useMemo } from 'react'
import { Layer, Line, Stage, Group, Circle, Rect, Text } from 'react-konva'
import { buildLevelLayout } from '../../hooks/useTreeLayout'
import { useCanvasViewport } from '../../hooks/useCanvasViewport'

const buildMultiwayPositions = (nodes = []) => {
    const items = Array.isArray(nodes) ? nodes : []
    if (!items.length) {
        return new Map()
    }

    const byId = new Map(items.map((node) => [node.id, node]))
    const depthMemo = new Map()
    const getDepth = (node) => {
        if (!node || node.parent_id == null) {
            return 0
        }
        if (depthMemo.has(node.id)) {
            return depthMemo.get(node.id)
        }
        const depth = 1 + getDepth(byId.get(node.parent_id))
        depthMemo.set(node.id, depth)
        return depth
    }

    const levels = []
    items.forEach((node) => {
        const depth = getDepth(node)
        if (!levels[depth]) {
            levels[depth] = []
        }
        levels[depth].push(node)
    })

    const positions = new Map()
    levels.forEach((levelNodes, depth) => {
        const sorted = [...levelNodes].sort((a, b) => Number(a.id) - Number(b.id))
        const count = sorted.length
        const baseWidth = Math.max(320, count * 180)
        const gap = count > 1 ? baseWidth / (count - 1) : 0
        sorted.forEach((node, idx) => {
            const width = Math.max(84, (node.keys?.length || 1) * 42)
            const x = 120 + idx * gap
            const y = 90 + depth * 130
            positions.set(node.id, { x, y, width })
        })
    })
    return positions
}

const stageInteractionProps = (transform, setTransform) => ({
    draggable: true,
    onDragEnd: (e) => {
        const pos = e.target.position()
        setTransform((prev) => ({ ...prev, x: pos.x, y: pos.y }))
    },
    onWheel: (e) => {
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
    },
    scaleX: transform.scale,
    scaleY: transform.scale,
    x: transform.x,
    y: transform.y,
})

const BinaryTreeCanvas = ({ nodes = [], activeValue = null, treeType }) => {
    const { positions } = buildLevelLayout(nodes, 140, 115)
    const viewportApi = useCanvasViewport(positions, { nodeRadius: 38, defaultHeight: 560 })
    const { shellRef, viewport, transform, setTransform, fitToContent, zoomIn, zoomOut } = viewportApi

    return (
        <div className="canvas-shell" ref={shellRef}>
            <div className="canvas-toolbar">
                <button type="button" onClick={zoomOut}>-</button>
                <button type="button" onClick={zoomIn}>+</button>
                <button type="button" onClick={fitToContent}>Fit Tree</button>
            </div>
            <Stage width={viewport.width} height={viewport.height} {...stageInteractionProps(transform, setTransform)}>
                <Layer>
                    {nodes.map((node) => {
                        const from = positions.get(node.id)
                        if (!from) {
                            return null
                        }
                        return (node.child_ids || []).map((childId) => {
                            const to = positions.get(childId)
                            if (!to) {
                                return null
                            }
                            return (
                                <Line
                                    key={`edge-${node.id}-${childId}`}
                                    points={[from.x, from.y, to.x, to.y]}
                                    stroke="#64748b"
                                    strokeWidth={2}
                                />
                            )
                        })
                    })}
                    {nodes.map((node) => {
                        const pos = positions.get(node.id)
                        if (!pos) {
                            return null
                        }
                        const active = Number(node.vrijednost) === Number(activeValue)
                        const fill = active ? '#ea580c' : treeType === 'rbtree' && node.color === 'red' ? '#dc2626' : '#0f766e'
                        return (
                            <Group key={`node-${node.id}`}>
                                <Circle
                                    x={pos.x}
                                    y={pos.y}
                                    radius={28}
                                    fill={fill}
                                    shadowBlur={active ? 18 : 8}
                                    shadowColor={fill}
                                    shadowOpacity={0.45}
                                />
                                <Text
                                    x={pos.x - 22}
                                    y={pos.y - 8}
                                    width={44}
                                    align="center"
                                    text={String(node.vrijednost)}
                                    fill="#fff"
                                    fontStyle="bold"
                                    fontSize={16}
                                />
                            </Group>
                        )
                    })}
                </Layer>
            </Stage>
        </div>
    )
}

const MultiwayTreeCanvas = ({ nodes = [], activeValue = null, leafChain = [], title }) => {
    const positions = useMemo(() => buildMultiwayPositions(nodes), [nodes])
    const viewportApi = useCanvasViewport(positions, { nodeRadius: 70, defaultHeight: 600 })
    const { shellRef, viewport, transform, setTransform, fitToContent, zoomIn, zoomOut } = viewportApi

    return (
        <div className="canvas-shell" ref={shellRef}>
            <div className="canvas-toolbar">
                <button type="button" onClick={zoomOut}>-</button>
                <button type="button" onClick={zoomIn}>+</button>
                <button type="button" onClick={fitToContent}>Fit Tree</button>
            </div>
            <Stage width={viewport.width} height={viewport.height} {...stageInteractionProps(transform, setTransform)}>
                <Layer>
                    {nodes.map((node) => {
                        const from = positions.get(node.id)
                        if (!from) {
                            return null
                        }
                        return (node.child_ids || []).map((childId) => {
                            const to = positions.get(childId)
                            if (!to) {
                                return null
                            }
                            return (
                                <Line
                                    key={`edge-${node.id}-${childId}`}
                                    points={[from.x, from.y + 22, to.x, to.y - 22]}
                                    stroke="#64748b"
                                    strokeWidth={2}
                                />
                            )
                        })
                    })}
                    {nodes.map((node) => {
                        const pos = positions.get(node.id)
                        if (!pos) {
                            return null
                        }
                        const width = pos.width
                        const active = (node.keys || []).some((value) => Number(value) === Number(activeValue))
                        return (
                            <Group key={`node-${node.id}`}>
                                <Rect
                                    x={pos.x - width / 2}
                                    y={pos.y - 24}
                                    width={width}
                                    height={48}
                                    cornerRadius={12}
                                    fill={active ? '#ea580c' : node.leaf ? '#0f766e' : '#155e75'}
                                    shadowBlur={active ? 16 : 8}
                                    shadowColor={active ? '#ea580c' : '#155e75'}
                                    shadowOpacity={0.35}
                                />
                                <Text
                                    x={pos.x - width / 2 + 10}
                                    y={pos.y - 9}
                                    width={width - 20}
                                    align="center"
                                    text={(node.keys || []).join(' | ')}
                                    fill="#fff"
                                    fontStyle="bold"
                                    fontSize={15}
                                />
                            </Group>
                        )
                    })}
                </Layer>
            </Stage>
            {leafChain.length > 0 && (
                <div className="variant-card leaf-chain-card">
                    <h3>{title} Leaf Chain</h3>
                    <div className="chip-row">
                        {leafChain.map((value, idx) => (
                            <span className={`step-chip ${Number(value) === Number(activeValue) ? 'step-chip-active' : ''}`} key={`leaf-${value}-${idx}`}>
                                {value}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

const AdvancedTreeCanvas = ({ treeType, state, activeValue }) => {
    if (!state) {
        return null
    }

    if (treeType === 'avl' || treeType === 'rbtree') {
        return <BinaryTreeCanvas nodes={state.nodes || []} activeValue={activeValue} treeType={treeType} />
    }

    return (
        <MultiwayTreeCanvas
            nodes={state.nodes || []}
            activeValue={activeValue}
            leafChain={state.leaf_chain || []}
            title={treeType === 'bplustree' ? 'B+ Tree' : 'B-Tree'}
        />
    )
}

export default AdvancedTreeCanvas
