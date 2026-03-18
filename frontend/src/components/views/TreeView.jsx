import React, { useState } from 'react'
import TreeCanvas from '../Canvas/TreeCanvas'
import PlaybackControls from '../Controls/PlaybackControls'
import { useTraversalMachine } from '../../hooks/useTraversalMachine'

const traversalFromOutput = (output) => (output && Array.isArray(output.steps) ? output.steps : [])

const TreeView = ({ rows, output, onInsert, onTraverseBfs, onTraverseDfs }) => {
    const [parentId, setParentId] = useState('-1')
    const [value, setValue] = useState('')
    const steps = traversalFromOutput(output)
    const machine = useTraversalMachine(steps)

    return (
        <section>
            <h2>General Tree Simulator</h2>
            <div className="control-grid">
                <input value={parentId} onChange={(e) => setParentId(e.target.value)} placeholder="Parent id (-1 root)" />
                <input value={value} onChange={(e) => setValue(e.target.value)} placeholder="Node value" />
                <button onClick={async () => { if (value) await onInsert(Number(parentId), Number(value)); setValue('') }}>Insert</button>
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

            <TreeCanvas rows={rows} traversalId={machine.activeStep} />
        </section>
    )
}

export default TreeView
