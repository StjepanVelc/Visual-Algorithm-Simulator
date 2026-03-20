import React, { useEffect, useMemo, useState } from 'react'
import BSTCanvas from '../Canvas/BSTCanvas'
import PlaybackControls from '../Controls/PlaybackControls'
import { useTraversalMachine } from '../../hooks/useTraversalMachine'

const traversalFromOutput = (output) => (output && Array.isArray(output.steps) ? output.steps : [])

const BSTView = ({ rows, output, onInsert, onDelete, onTraverseBfs, onTraverseDfs, onSearch, lastInsertPath, lastDeletedId, lastDeletedNode }) => {
    const [insertValue, setInsertValue] = useState('')
    const [deleteValue, setDeleteValue] = useState('')
    const [searchValue, setSearchValue] = useState('')
    // Stabilise reference — only recompute when output actually changes,
    // not on every timer-triggered re-render.
    const steps = useMemo(() => traversalFromOutput(output), [output])
    const machine = useTraversalMachine(steps)
    const [deleteGhost, setDeleteGhost] = useState(null)

    useEffect(() => {
        if (!lastDeletedId || !lastDeletedNode) {
            return
        }
        setDeleteGhost({ id: lastDeletedId, value: lastDeletedNode.vrijednost })
        const timer = setTimeout(() => setDeleteGhost(null), 1200)
        return () => clearTimeout(timer)
    }, [lastDeletedId, lastDeletedNode])

    return (
        <section>
            <h2>BST Simulator</h2>
            <div className="control-stack">
                <div className="control-grid control-grid-bst">
                    <input value={insertValue} onChange={(e) => setInsertValue(e.target.value)} placeholder="Value to insert" />
                    <button onClick={async () => { if (insertValue) await onInsert(Number(insertValue)); setInsertValue('') }}>Insert</button>
                    <input value={deleteValue} onChange={(e) => setDeleteValue(e.target.value)} placeholder="Leaf node id" />
                    <button onClick={async () => { if (deleteValue) await onDelete(Number(deleteValue)); setDeleteValue('') }}>Delete Leaf</button>
                </div>

                <div className="control-grid control-grid-bst-search">
                    <input value={searchValue} onChange={(e) => setSearchValue(e.target.value)} placeholder="BST value" />
                    <button onClick={async () => { if (searchValue && onSearch) await onSearch(searchValue); setSearchValue('') }}>BST Search</button>
                    <button onClick={onTraverseBfs}>Traverse BFS</button>
                    <button onClick={onTraverseDfs}>Traverse DFS</button>
                </div>
            </div>

            <PlaybackControls
                machine={machine.state}
                onPlay={machine.play}
                onPause={machine.pause}
                onStep={machine.step}
                onReset={machine.reset}
            />

            <BSTCanvas
                rows={rows}
                traversalId={machine.activeStep}
                insertPath={lastInsertPath}
                deleteGhost={deleteGhost}
            />
        </section>
    )
}

export default BSTView
