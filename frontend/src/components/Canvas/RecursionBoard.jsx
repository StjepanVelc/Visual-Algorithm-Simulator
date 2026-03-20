import React from 'react'

const RecursionBoard = ({ rows = [], activeId = null, sourceId = 'bst' }) => {
    const items = Array.isArray(rows) ? rows : []
    const byId = new Map(items.map((n) => [n.id, n]))

    const depthOf = (node) => {
        if (!node || node.parent_id == null) {
            return 0
        }
        return 1 + depthOf(byId.get(node.parent_id))
    }

    return (
        <div className="call-flow">
            <div className="variant-card recursion-source-card">
                <p>Recursion source: <strong>{sourceId.toUpperCase()}</strong></p>
                <p>Aktivni call: <strong>{activeId ?? '-'}</strong></p>
            </div>
            {items.map((call) => {
                const depth = depthOf(call)
                const active = Number(call.id) === Number(activeId)
                return (
                    <article key={call.id} className={`call-card ${active ? 'call-card-active' : ''}`} style={{ marginLeft: `${depth * 24}px` }}>
                        <div className="call-head">
                            <strong>{call.oznaka}</strong>
                            <span>#{call.id}</span>
                        </div>
                        <div className="call-body">
                            <span>fn: {call.funkcija}</span>
                            <span>arg: {call.argument}</span>
                            <span>ret: {call.povrat ?? 'pending'}</span>
                            <span>parent: {call.parent_id ?? 'root'}</span>
                        </div>
                    </article>
                )
            })}
        </div>
    )
}

export default RecursionBoard
