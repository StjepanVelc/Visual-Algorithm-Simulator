import React, { useEffect, useState } from 'react'
import { useStore } from './store'
import './App.css'
import { ensureDefaultAlgorithms } from './algorithms/defaults.jsx'
import { getRegisteredAlgorithms } from './algorithms/registry'

ensureDefaultAlgorithms()

const initialDebugMode = () => {
    if (typeof window === 'undefined') {
        return false
    }
    const saved = window.localStorage.getItem('vas:debug-mode')
    if (saved != null) {
        return saved === 'true'
    }
    return Boolean(import.meta.env.DEV)
}

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
        advancedTreeStates,
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
        loadAdvancedTreeState,
        insertAdvancedTreeValue,
        deleteAdvancedTreeValue,
        searchAdvancedTreeValue,
        traverseAdvancedTree,
        resetAdvancedTree,
        loadRecursionState,
        insertRecursionNode,
        listDatabases,
        recreateDatabase,
        clearDatabase
    } = useStore()

    const [backendConnected, setBackendConnected] = useState(false)
    const [output, setOutput] = useState(null)
    const [debugMode, setDebugMode] = useState(initialDebugMode)
    const algorithms = getRegisteredAlgorithms()

    const pluginContext = {
        output,
        setOutput,
        bstState,
        hashState,
        treeState,
        recursionState,
        advancedTreeStates,
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
        loadAdvancedTreeState,
        insertAdvancedTreeValue,
        deleteAdvancedTreeValue,
        searchAdvancedTreeValue,
        traverseAdvancedTree,
        resetAdvancedTree,
        loadRecursionState,
        insertRecursionNode,
        listDatabases,
        recreateDatabase,
        clearDatabase,
        lastBstInsertPath,
        lastBstDeletedId,
        lastBstDeletedNode,
        debugMode,
    }

    useEffect(() => {
        window.localStorage.setItem('vas:debug-mode', String(debugMode))
    }, [debugMode])

    useEffect(() => {
        const handleKey = (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'D') {
                e.preventDefault()
                setDebugMode((prev) => !prev)
            }
        }
        window.addEventListener('keydown', handleKey)
        return () => window.removeEventListener('keydown', handleKey)
    }, [])

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
                    {debugMode && (
                        <button
                            type="button"
                            className="debug-toggle active"
                            onClick={() => setDebugMode(false)}
                        >
                            Debug On
                        </button>
                    )}
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
