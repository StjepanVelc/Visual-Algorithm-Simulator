import { useCallback, useEffect, useRef, useState } from 'react'

const clamp = (value, min, max) => Math.max(min, Math.min(max, value))

export const useCanvasViewport = (positions, options = {}) => {
    const {
        nodeRadius = 36,
        defaultHeight = 560,
        padding = 56,
        minScale = 0.35,
        maxScale = 2.4,
    } = options

    const shellRef = useRef(null)
    const [viewport, setViewport] = useState({ width: 1040, height: defaultHeight })
    const [transform, setTransform] = useState({ scale: 1, x: 0, y: 0 })

    const fitToContent = useCallback(() => {
        const values = Array.from(positions.values())
        if (!values.length) {
            setTransform({ scale: 1, x: 0, y: 0 })
            return
        }

        const minX = Math.min(...values.map((p) => p.x)) - nodeRadius
        const maxX = Math.max(...values.map((p) => p.x)) + nodeRadius
        const minY = Math.min(...values.map((p) => p.y)) - nodeRadius
        const maxY = Math.max(...values.map((p) => p.y)) + nodeRadius

        const contentWidth = Math.max(1, maxX - minX)
        const contentHeight = Math.max(1, maxY - minY)

        const targetScale = clamp(
            Math.min(
                (viewport.width - padding * 2) / contentWidth,
                (viewport.height - padding * 2) / contentHeight,
            ),
            minScale,
            maxScale,
        )

        const centeredX = (viewport.width - contentWidth * targetScale) / 2 - minX * targetScale
        const centeredY = (viewport.height - contentHeight * targetScale) / 2 - minY * targetScale

        setTransform({
            scale: targetScale,
            x: centeredX,
            y: centeredY,
        })
    }, [maxScale, minScale, nodeRadius, padding, positions, viewport.height, viewport.width])

    useEffect(() => {
        const node = shellRef.current
        if (!node) {
            return undefined
        }

        const observer = new ResizeObserver((entries) => {
            const rect = entries[0]?.contentRect
            if (!rect) {
                return
            }
            setViewport({
                width: Math.max(320, rect.width),
                height: defaultHeight,
            })
        })

        observer.observe(node)
        return () => observer.disconnect()
    }, [defaultHeight])

    useEffect(() => {
        fitToContent()
    }, [fitToContent])

    const zoomBy = (factor) => {
        setTransform((prev) => {
            const nextScale = clamp(prev.scale * factor, minScale, maxScale)
            const cx = viewport.width / 2
            const cy = viewport.height / 2
            return {
                scale: nextScale,
                x: cx - ((cx - prev.x) / prev.scale) * nextScale,
                y: cy - ((cy - prev.y) / prev.scale) * nextScale,
            }
        })
    }

    return {
        shellRef,
        viewport,
        transform,
        setTransform,
        fitToContent,
        zoomIn: () => zoomBy(1.15),
        zoomOut: () => zoomBy(1 / 1.15),
    }
}
