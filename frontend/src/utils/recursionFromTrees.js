const rowsFromBinary = (nodes = [], label) => {
    const byParent = new Map()
    const items = Array.isArray(nodes) ? nodes : []
    items.forEach((node) => {
        const parentId = node.parent_id ?? null
        if (!byParent.has(parentId)) {
            byParent.set(parentId, [])
        }
        byParent.get(parentId).push(node)
    })

    const rows = []
    let callId = 1
    const visit = (node, parentCallId = null, depth = 0) => {
        const id = callId
        callId += 1
        rows.push({
            id,
            parent_id: parentCallId,
            oznaka: `${label}:${node.vrijednost}`,
            funkcija: `visit_${label.toLowerCase()}`,
            argument: String(node.vrijednost),
            povrat: `depth=${depth}`,
        })
        const children = byParent.get(node.id) || []
        children.forEach((child) => visit(child, id, depth + 1))
    }

        ; (byParent.get(null) || []).forEach((root) => visit(root))
    return rows
}

const rowsFromGeneral = (nodes = [], label) => {
    const byParent = new Map()
    const items = Array.isArray(nodes) ? nodes : []
    items.forEach((node) => {
        const parentId = node.parent_id ?? null
        if (!byParent.has(parentId)) {
            byParent.set(parentId, [])
        }
        byParent.get(parentId).push(node)
    })

    const rows = []
    let callId = 1
    const visit = (node, parentCallId = null, depth = 0) => {
        const id = callId
        callId += 1
        rows.push({
            id,
            parent_id: parentCallId,
            oznaka: `${label}:${node.vrijednost}`,
            funkcija: 'visit_tree',
            argument: String(node.vrijednost),
            povrat: `children=${(byParent.get(node.id) || []).length}`,
        })
            ; (byParent.get(node.id) || []).forEach((child) => visit(child, id, depth + 1))
    }

        ; (byParent.get(null) || []).forEach((root) => visit(root))
    return rows
}

const rowsFromMultiway = (nodes = [], label) => {
    const byParent = new Map()
    const items = Array.isArray(nodes) ? nodes : []
    items.forEach((node) => {
        const parentId = node.parent_id ?? null
        if (!byParent.has(parentId)) {
            byParent.set(parentId, [])
        }
        byParent.get(parentId).push(node)
    })

    const rows = []
    let callId = 1
    const visit = (node, parentCallId = null) => {
        const id = callId
        callId += 1
        rows.push({
            id,
            parent_id: parentCallId,
            oznaka: `${label}:${(node.keys || []).join('|')}`,
            funkcija: `visit_${label.toLowerCase()}`,
            argument: (node.keys || []).join(', '),
            povrat: node.leaf ? 'leaf' : `children=${(node.child_ids || []).length}`,
        })
            ; (byParent.get(node.id) || []).forEach((child) => visit(child, id))
    }

        ; (byParent.get(null) || []).forEach((root) => visit(root))
    return rows
}

export const buildRecursionRowsFromSource = ({ sourceId, bstState, treeState, advancedTreeStates }) => {
    switch (sourceId) {
        case 'bst':
            return rowsFromBinary(bstState || [], 'BST')
        case 'tree':
            return rowsFromGeneral(treeState || [], 'TREE')
        case 'avl':
            return rowsFromBinary(advancedTreeStates?.avl?.nodes || [], 'AVL')
        case 'rbtree':
            return rowsFromBinary(advancedTreeStates?.rbtree?.nodes || [], 'RBT')
        case 'btree':
            return rowsFromMultiway(advancedTreeStates?.btree?.nodes || [], 'BTREE')
        case 'bplustree':
            return rowsFromMultiway(advancedTreeStates?.bplustree?.nodes || [], 'BPLUS')
        default:
            return []
    }
}
