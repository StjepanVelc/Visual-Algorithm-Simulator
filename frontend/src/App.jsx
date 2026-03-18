import React, { useEffect, useState } from 'react'
import { useStore } from './store'
import './App.css'
import { ensureDefaultAlgorithms } from './algorithms/defaults'
import { getRegisteredAlgorithms } from './algorithms/registry'

ensureDefaultAlgorithms()

const App = () => {
    const {
        currentView,
        setView,
        error,
        clearError,
        loading,
        bstState,
        lastBstInsertPath,
        lastBstDeletedId,
        lastBstDeletedNode,
        hashState,
        treeState,
        recursionState,
        loadBSTState,
        insertBSTNode,
        deleteBSTNode,
        traverseBST,
        loadHashState,
        insertHashItem,
        deleteHashItem,
        loadTreeState,
        insertTreeNode,
        traverseTree,
        loadRecursionState,
        insertRecursionNode,
        listDatabases,
        recreateDatabase,
        clearDatabase
    } = useStore()

    const [backendConnected, setBackendConnected] = useState(false)
    const [output, setOutput] = useState(null)
    const algorithms = getRegisteredAlgorithms()

    const pluginContext = {
        output,
        setOutput,
        bstState,
        hashState,
        treeState,
        recursionState,
        loadBSTState,
        insertBSTNode,
        deleteBSTNode,
        traverseBST,
        loadHashState,
        insertHashItem,
        deleteHashItem,
        loadTreeState,
        insertTreeNode,
        traverseTree,
        loadRecursionState,
        insertRecursionNode,
        listDatabases,
        recreateDatabase,
        clearDatabase,
        lastBstInsertPath,
        lastBstDeletedId,
        lastBstDeletedNode,
    }

    useEffect(() => {
        const checkBackend = async () => {
            try {
                const res = await fetch('/api/health')
                setBackendConnected(res.ok)
            } catch {
                setBackendConnected(false)
            }
        }
        checkBackend()
        const interval = setInterval(checkBackend, 5000)
        return () => clearInterval(interval)
    }, [])

    useEffect(() => {
        if (!backendConnected) {
            return
        }

        const load = async () => {
            const plugin = algorithms.find((item) => item.id === currentView)
            if (plugin?.load) {
                await plugin.load(pluginContext)
            }
        }

        load()
    }, [currentView, backendConnected, loadBSTState, loadHashState, loadTreeState, loadRecursionState])

    const renderView = () => {
        const plugin = algorithms.find((item) => item.id === currentView)
        if (!plugin?.render) {
            return <p className="empty-state">No plugin registered for this algorithm.</p>
        }
        return plugin.render(pluginContext)
    }

    return (
        <div className="app">
            <header className="app-header">
                <h1>Algorithm Simulator Web</h1>
                <div className="header-right">
                    <span className={`backend-status ${backendConnected ? 'connected' : 'disconnected'}`}>
                        {backendConnected ? 'Backend Connected' : 'Backend Unavailable'}
                    </span>
                </div>
            </header>

            {error && (
                <div className="error-banner">
                    <p>{error}</p>
                    <button onClick={clearError}>✕</button>
                </div>
            )}

            <nav className="view-tabs">
                {algorithms.map((view) => (
                    <button
                        key={view.id}
                        className={`tab ${currentView === view.id ? 'active' : ''}`}
                        onClick={() => setView(view.id)}
                    >
                        {view.label}
                    </button>
                ))}
            </nav>

            <main className="content">
                {!backendConnected ? (
                    <div className="no-backend">
                        <h2>Backend Not Connected</h2>
                        <p>Make sure FastAPI server is running on http://localhost:8000</p>
                        <p>Run: <code>cd backend ; python main.py</code></p>
                    </div>
                ) : (
                    <div className="view-container">
                        {loading && <p className="loading">Loading...</p>}
                        {renderView()}
                    </div>
                )}
            </main>
        </div>
    )
}

export default App
