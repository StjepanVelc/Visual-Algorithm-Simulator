import React, { useMemo, useState } from 'react'
import RecursionBoard from '../Canvas/RecursionBoard'
import PlaybackControls from '../Controls/PlaybackControls'
import { useTraversalMachine } from '../../hooks/useTraversalMachine'
import { buildRecursionRowsFromSource } from '../../utils/recursionFromTrees'

const sources = [
    { id: 'bst', label: 'BST' },
    { id: 'tree', label: 'General Tree' },
    { id: 'avl', label: 'AVL Tree' },
    { id: 'btree', label: 'B-Tree' },
    { id: 'bplustree', label: 'B+ Tree' },
    { id: 'rbtree', label: 'RB Tree' },
]

const RecursionView = ({ rows, onInsert, bstState, treeState, advancedTreeStates }) => {
    const [parentId, setParentId] = useState('-1')
    const [value, setValue] = useState('0')
    const [sourceId, setSourceId] = useState('bst')
    const [derivedRows, setDerivedRows] = useState([])

    const activeRows = derivedRows.length > 0 ? derivedRows : (rows || [])
    const steps = useMemo(() => activeRows.map((item) => item.id), [activeRows])
    const machine = useTraversalMachine(steps)

    const loadFromSource = () => {
        setDerivedRows(buildRecursionRowsFromSource({ sourceId, bstState, treeState, advancedTreeStates }))
    }

    return (
        <section>
            <h2>Recursion Stack Simulator</h2>
            <div className="control-grid control-grid-bst">
                <input value={parentId} onChange={(e) => setParentId(e.target.value)} placeholder="Parent id (-1 root)" />
                <input value={value} onChange={(e) => setValue(e.target.value)} placeholder="Argument" />
                <button onClick={async () => await onInsert(Number(parentId), Number(value))}>Insert Call</button>
                <select value={sourceId} onChange={(e) => setSourceId(e.target.value)}>
                    {sources.map((source) => (
                        <option key={source.id} value={source.id}>{source.label}</option>
                    ))}
                </select>
                <button onClick={loadFromSource}>Load From Tree</button>
                <button onClick={() => setDerivedRows([])}>Use Manual Recursion</button>
            </div>

            <PlaybackControls
                machine={machine.state}
                onPlay={machine.play}
                onPause={machine.pause}
                onStep={machine.step}
                onReset={machine.reset}
            />

            <RecursionBoard rows={activeRows} activeId={machine.activeStep} sourceId={sourceId} />
        </section>
    )
}

export default RecursionView
