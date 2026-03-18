import { BSTView, HashView, RecursionView, SystemView, TreeView } from '../components/views'
import { hasAlgorithm, registerAlgorithm } from './registry'

export const ensureDefaultAlgorithms = () => {
    if (!hasAlgorithm('bst')) {
        registerAlgorithm('bst', {
            label: 'BST',
            load: async (ctx) => ctx.loadBSTState(),
            render: (ctx) => (
                <BSTView
                    rows={ctx.bstState || []}
                    output={ctx.output}
                    onInsert={ctx.insertBSTNode}
                    onDelete={ctx.deleteBSTNode}
                    onTraverseBfs={async () => ctx.setOutput(await ctx.traverseBST('bfs'))}
                    onTraverseDfs={async () => ctx.setOutput(await ctx.traverseBST('dfs'))}
                    lastInsertPath={ctx.lastBstInsertPath}
                    lastDeletedId={ctx.lastBstDeletedId}
                    lastDeletedNode={ctx.lastBstDeletedNode}
                />
            ),
        })
    }

    if (!hasAlgorithm('hash')) {
        registerAlgorithm('hash', {
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
    }

    if (!hasAlgorithm('tree')) {
        registerAlgorithm('tree', {
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
    }

    if (!hasAlgorithm('recursion')) {
        registerAlgorithm('recursion', {
            label: 'RECURSION',
            load: async (ctx) => ctx.loadRecursionState(),
            render: (ctx) => <RecursionView rows={ctx.recursionState || []} onInsert={ctx.insertRecursionNode} />,
        })
    }

    if (!hasAlgorithm('system')) {
        registerAlgorithm('system', {
            label: 'SYSTEM',
            load: async () => { },
            render: (ctx) => (
                <SystemView
                    output={ctx.output}
                    onListDatabases={async () => ctx.setOutput(await ctx.listDatabases())}
                    onRebuildDatabase={async () => ctx.setOutput(await ctx.recreateDatabase())}
                    onClearDatabase={async () => ctx.setOutput(await ctx.clearDatabase())}
                />
            ),
        })
    }
}
