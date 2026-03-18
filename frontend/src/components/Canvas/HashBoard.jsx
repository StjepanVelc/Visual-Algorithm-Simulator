import React from 'react'

const HashBoard = ({ rows = [] }) => {
    const buckets = new Map()
        ; (Array.isArray(rows) ? rows : []).forEach((row) => {
            const bucket = Number(row.bucket)
            if (!buckets.has(bucket)) {
                buckets.set(bucket, [])
            }
            if (row.cvor_id != null) {
                buckets.get(bucket).push(row)
            }
        })

    const keys = [...buckets.keys()].sort((a, b) => a - b)

    return (
        <div className="bucket-grid">
            {keys.map((bucket) => {
                const chain = buckets.get(bucket) || []
                return (
                    <section key={bucket} className="bucket-card">
                        <h3>Bucket {bucket}</h3>
                        {chain.length === 0 ? (
                            <p className="empty-state">Empty</p>
                        ) : (
                            <div className="chain-row">
                                {chain.map((node, idx) => (
                                    <React.Fragment key={node.cvor_id}>
                                        <article className="node-card hash-node">
                                            <header>#{node.cvor_id}</header>
                                            <strong>{node.kljuc}</strong>
                                            <span>{node.vrijednost}</span>
                                        </article>
                                        {idx < chain.length - 1 && <span className="chain-arrow">-&gt;</span>}
                                    </React.Fragment>
                                ))}
                            </div>
                        )}
                    </section>
                )
            })}
        </div>
    )
}

export default HashBoard
