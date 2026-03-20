import React from 'react'

const DebugJsonPanel = ({ title, data }) => {
    if (!data) {
        return null
    }

    return (
        <div className="debug-panel">
            <div className="debug-panel-header">
                <h3>{title}</h3>
                <span className="debug-badge">DEV</span>
            </div>
            <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
    )
}

export default DebugJsonPanel
