import { BSTView, HashView, RecursionView, SystemView, TreeVariantView, TreeView } from '../components/views'
import { hasAlgorithm, registerAlgorithm } from './registry'

const registerIfMissing = (id, config) => {
    if (!hasAlgorithm(id)) {
        registerAlgorithm(id, config)
    }
}

const upcomingTreeAlgorithms = [
    { id: 'avl', label: 'AVL Tree', subtitle: 'Self-balancing BST with rotations.' },
    { id: 'btree', label: 'B-Tree', subtitle: 'Multi-way search tree optimized for storage systems.' },
    { id: 'bplustree', label: 'B+ Tree', subtitle: 'B-Tree variant with linked leaves for fast range scans.' },
    { id: 'rbtree', label: 'RB Tree', subtitle: 'Red-Black balancing strategy for logarithmic operations.' },
]

export const ensureDefaultAlgorithms = () => {
    registerIfMissing('bst', {
        label: 'BST',
        load: async (ctx) => ctx.loadBSTState(),
        render: (ctx) => (
            <BSTView
                rows={ctx.bstState || []}
                output={ctx.output}
                onInsert={ctx.insertBSTNode}
                onDelete={ctx.deleteBSTNode}
                onSearch={async (val) => ctx.setOutput(await ctx.traverseBST('search', val))}
                onTraverseBfs={async () => ctx.setOutput(await ctx.traverseBST('bfs'))}
                onTraverseDfs={async () => ctx.setOutput(await ctx.traverseBST('dfs'))}
                lastInsertPath={ctx.lastBstInsertPath}
                lastDeletedId={ctx.lastBstDeletedId}
                lastDeletedNode={ctx.lastBstDeletedNode}
            />
        ),
    })

    registerIfMissing('hash', {
        label: 'HASH',
        load: async (ctx) => ctx.loadHashState(),
        render: (ctx) => (
            <HashView
                rows={ctx.hashState || []}
                onInsert={ctx.insertHashItem}
                onDelete={ctx.deleteHashItem}
            />
        ),
    })

    registerIfMissing('tree', {
        label: 'TREE',
        load: async (ctx) => ctx.loadTreeState(),
        render: (ctx) => (
            <TreeView
                rows={ctx.treeState || []}
                output={ctx.output}
                onInsert={ctx.insertTreeNode}
                onTraverseBfs={async () => ctx.setOutput(await ctx.traverseTree('bfs'))}
                onTraverseDfs={async () => ctx.setOutput(await ctx.traverseTree('dfs'))}
            />
        ),
    })

    upcomingTreeAlgorithms.forEach((item) => {
        registerIfMissing(item.id, {
            label: item.label,
            load: async (ctx) => ctx.loadAdvancedTreeState(item.id),
            render: (ctx) => (
                <TreeVariantView
                    title={item.label}
                    treeType={item.id}
                    subtitle={item.subtitle}
                    state={ctx.advancedTreeStates?.[item.id] || null}
                    output={ctx.output}
                    debugMode={ctx.debugMode}
                    onInsert={async (value) => ctx.setOutput(await ctx.insertAdvancedTreeValue(item.id, value))}
                    onDelete={async (value) => ctx.setOutput(await ctx.deleteAdvancedTreeValue(item.id, value))}
                    onSearch={async (value) => ctx.setOutput(await ctx.searchAdvancedTreeValue(item.id, value))}
                    onTraverseBfs={async () => ctx.setOutput(await ctx.traverseAdvancedTree(item.id, 'bfs'))}
                    onTraverseDfs={async () => ctx.setOutput(await ctx.traverseAdvancedTree(item.id, 'dfs'))}
                    onReset={async () => ctx.setOutput(await ctx.resetAdvancedTree(item.id))}
                />
            ),
        })
    })

    registerIfMissing('recursion', {
        label: 'RECURSION',
        load: async (ctx) => ctx.loadRecursionState(),
        render: (ctx) => (
            <RecursionView
                rows={ctx.recursionState || []}
                onInsert={ctx.insertRecursionNode}
                bstState={ctx.bstState || []}
                treeState={ctx.treeState || []}
                advancedTreeStates={ctx.advancedTreeStates || {}}
            />
        ),
    })

    registerIfMissing('system', {
        label: 'SYSTEM',
        load: async () => { },
        render: (ctx) => (
            <SystemView
                output={ctx.output}
                debugMode={ctx.debugMode}
                onListDatabases={async () => ctx.setOutput(await ctx.listDatabases())}
                onRebuildDatabase={async () => ctx.setOutput(await ctx.recreateDatabase())}
                onClearDatabase={async () => ctx.setOutput(await ctx.clearDatabase())}
            />
        ),
    })
}

