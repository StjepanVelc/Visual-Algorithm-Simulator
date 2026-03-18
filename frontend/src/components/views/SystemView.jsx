import React from 'react'

const SystemView = ({ output, onListDatabases, onRebuildDatabase, onClearDatabase }) => {
    return (
        <section>
            <h2>System</h2>
            <div className="control-grid">
                <button onClick={onListDatabases}>List Databases</button>
                <button onClick={onRebuildDatabase}>Rebuild Database</button>
                <button onClick={onClearDatabase}>Clear Database</button>
            </div>

            {output && (
                <div className="output-block">
                    <h3>System Response</h3>
                    <pre>{JSON.stringify(output, null, 2)}</pre>
                </div>
            )}
        </section>
    )
}

export default SystemView
