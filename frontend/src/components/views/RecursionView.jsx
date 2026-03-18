import React, { useState } from 'react'
import RecursionBoard from '../Canvas/RecursionBoard'

const RecursionView = ({ rows, onInsert }) => {
    const [parentId, setParentId] = useState('-1')
    const [value, setValue] = useState('0')

    return (
        <section>
            <h2>Recursion Stack Simulator</h2>
            <div className="control-grid">
                <input value={parentId} onChange={(e) => setParentId(e.target.value)} placeholder="Parent id (-1 root)" />
                <input value={value} onChange={(e) => setValue(e.target.value)} placeholder="Argument" />
                <button onClick={async () => await onInsert(Number(parentId), Number(value))}>Insert Call</button>
            </div>

            <RecursionBoard rows={rows} />
        </section>
    )
}

export default RecursionView
