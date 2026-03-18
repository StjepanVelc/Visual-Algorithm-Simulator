import React, { useEffect, useState } from 'react'
import BSTCanvas from '../Canvas/BSTCanvas'
import PlaybackControls from '../Controls/PlaybackControls'
import { useTraversalMachine } from '../../hooks/useTraversalMachine'

const traversalFromOutput = (output) => (output && Array.isArray(output.steps) ? output.steps : [])

const BSTView = ({ rows, output, onInsert, onDelete, onTraverseBfs, onTraverseDfs, lastInsertPath, lastDeletedId, lastDeletedNode }) => {
    const [insertValue, setInsertValue] = useState('')
    const [deleteValue, setDeleteValue] = useState('')
    const steps = traversalFromOutput(output)
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
            <div className="control-grid">
                <input value={insertValue} onChange={(e) => setInsertValue(e.target.value)} placeholder="Value to insert" />
                <button onClick={async () => { if (insertValue) await onInsert(Number(insertValue)); setInsertValue('') }}>Insert</button>
                <input value={deleteValue} onChange={(e) => setDeleteValue(e.target.value)} placeholder="Leaf node id" />
                <button onClick={async () => { if (deleteValue) await onDelete(Number(deleteValue)); setDeleteValue('') }}>Delete Leaf</button>
                <button onClick={onTraverseBfs}>Traverse BFS</button>
                <button onClick={onTraverseDfs}>Traverse DFS</button>
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
