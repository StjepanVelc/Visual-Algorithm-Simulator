export const buildLevelLayout = (rows = [], xGap = 120, yGap = 110) => {
    const items = Array.isArray(rows) ? rows : []
    if (items.length === 0) {
        return { levels: [], positions: new Map() }
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
        const parent = byId.get(node.parent_id)
        const depth = 1 + getDepth(parent)
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

    levels.forEach((levelNodes, levelIndex) => {
        const sorted = [...levelNodes].sort((a, b) => Number(a.id) - Number(b.id))
        const startX = 90
        sorted.forEach((node, idx) => {
            const x = startX + idx * xGap
            const y = 70 + levelIndex * yGap
            positions.set(node.id, { x, y })
        })
    })

    return { levels, positions }
}
