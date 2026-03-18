import React, { useState } from 'react'
import HashBoard from '../Canvas/HashBoard'

const HashView = ({ rows, onInsert, onDelete }) => {
    const [key, setKey] = useState('')
    const [value, setValue] = useState('')
    const [deleteKey, setDeleteKey] = useState('')

    return (
        <section>
            <h2>Hash Table Simulator</h2>
            <div className="control-grid">
                <input value={key} onChange={(e) => setKey(e.target.value)} placeholder="Key" />
                <input value={value} onChange={(e) => setValue(e.target.value)} placeholder="Value" />
                <button onClick={async () => { if (key) await onInsert(key, value); setKey(''); setValue('') }}>Insert</button>
                <input value={deleteKey} onChange={(e) => setDeleteKey(e.target.value)} placeholder="Key to delete" />
                <button onClick={async () => { if (deleteKey) await onDelete(deleteKey); setDeleteKey('') }}>Delete</button>
            </div>

            <HashBoard rows={rows} />
        </section>
    )
}

export default HashView
