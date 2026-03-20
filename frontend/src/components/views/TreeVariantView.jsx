import React, { useMemo, useState } from 'react'
import PlaybackControls from '../Controls/PlaybackControls'
import AdvancedTreeCanvas from '../Canvas/AdvancedTreeCanvas'
import DebugJsonPanel from '../DebugJsonPanel'
import { useTraversalMachine } from '../../hooks/useTraversalMachine'

const traversalFromOutput = (output) => (output && Array.isArray(output.steps) ? output.steps : [])

const TreeVariantView = ({
    title,
    treeType,
    subtitle,
    state,
    output,
    debugMode = false,
    onInsert,
    onDelete,
    onSearch,
    onTraverseBfs,
    onTraverseDfs,
    onReset,
}) => {
    const [insertValue, setInsertValue] = useState('')
    const [deleteValue, setDeleteValue] = useState('')
    const [searchValue, setSearchValue] = useState('')
    const steps = useMemo(() => traversalFromOutput(output), [output])
    const machine = useTraversalMachine(steps)

    const keys = state?.keys || []
    const levels = state?.levels || []
    const nodes = state?.nodes || []
    const activeValue = machine.activeStep

    return (
        <section>
            <h2>{title}</h2>
            <div className="control-stack">
                <div className="control-grid control-grid-bst">
                    <input value={insertValue} onChange={(e) => setInsertValue(e.target.value)} placeholder="Value to insert" />
                    <button onClick={async () => { if (insertValue) await onInsert(Number(insertValue)); setInsertValue('') }}>Insert</button>
                    <input value={deleteValue} onChange={(e) => setDeleteValue(e.target.value)} placeholder="Value to delete" />
                    <button onClick={async () => { if (deleteValue) await onDelete(Number(deleteValue)); setDeleteValue('') }}>Delete</button>
                </div>

                <div className="control-grid control-grid-bst-search">
                    <input value={searchValue} onChange={(e) => setSearchValue(e.target.value)} placeholder="Search value" />
                    <button onClick={async () => { if (searchValue) await onSearch(Number(searchValue)); setSearchValue('') }}>Search</button>
                    <button onClick={onTraverseBfs}>Traverse BFS</button>
                    <button onClick={onTraverseDfs}>Traverse DFS</button>
                    <button onClick={onReset}>Reset</button>
                </div>
            </div>

            <PlaybackControls
                machine={machine.state}
                onPlay={machine.play}
                onPause={machine.pause}
                onStep={machine.step}
                onReset={machine.reset}
            />

            <div className="variant-card">
                <p>{subtitle}</p>
                <p>
                    Aktivni element: <strong>{activeValue ?? '-'}</strong>
                </p>
                <p>Ukupno kljuceva: <strong>{state?.size || 0}</strong></p>
            </div>

            <AdvancedTreeCanvas treeType={treeType} state={state} activeValue={activeValue} />

            <div className="variant-card">
                <h3>Keys</h3>
                <div className="chip-row">
                    {keys.map((value) => (
                        <span className={`step-chip ${Number(value) === Number(activeValue) ? 'step-chip-active' : ''}`} key={`k-${value}`}>
                            {value}
                        </span>
                    ))}
                    {keys.length === 0 && <span>No keys yet.</span>}
                </div>
            </div>

            {levels.length > 0 && treeType !== 'avl' && treeType !== 'rbtree' && (
                <div className="variant-card">
                    <h3>Levels</h3>
                    <div className="level-board">
                        {levels.map((level, levelIndex) => (
                            <div className="level-row" key={`lvl-${levelIndex}`}>
                                <div className="level-label">L{levelIndex}</div>
                                <div className="node-lane">
                                    {level.map((nodeKeys, idx) => (
                                        <div className="node-card tree-card" key={`node-${levelIndex}-${idx}`}>
                                            {nodeKeys.join(' | ')}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {nodes.length > 0 && (treeType === 'avl' || treeType === 'rbtree') && (
                <div className="variant-card">
                    <h3>Binary Nodes</h3>
                    <div className="node-lane">
                        {nodes.map((node) => (
                            <div className="node-card bst-card" key={`bin-${node.id}`}>
                                <header>id: {node.id}</header>
                                <strong>{node.vrijednost}</strong>
                                <div className="node-meta">
                                    <span>L: {node.lijevi_id ?? '-'}</span>
                                    <span>R: {node.desni_id ?? '-'}</span>
                                    <span>C: {node.color || '-'}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {debugMode && <DebugJsonPanel title="Last Operation Output" data={output} />}
        </section >
    )
}

export default TreeVariantView




