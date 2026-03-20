import React from 'react'
import DebugJsonPanel from '../DebugJsonPanel'

const SystemView = ({ output, onListDatabases, onRebuildDatabase, onClearDatabase, debugMode = false }) => {
    return (
        <section>
            <h2>System</h2>
            <div className="control-grid">
                <button onClick={onListDatabases}>List Databases</button>
                <button onClick={onRebuildDatabase}>Rebuild Database</button>
                <button onClick={onClearDatabase}>Clear Database</button>
            </div>

            {debugMode && <DebugJsonPanel title="System Response" data={output} />}
        </section>
    )
}

export default SystemView
