import create from 'zustand'
import { api } from './services/api'

export const useStore = create((set, get) => ({
    // State
    currentView: 'bst',
    dbId: 1,
    bstState: null,
    hashState: null,
    treeState: null,
    recursionState: null,
    lastBstInsertPath: [],
    lastBstDeletedId: null,
    lastBstDeletedNode: null,
    loading: false,
    error: null,

    // Actions
    setView: (view) => set({ currentView: view }),
    setDbId: (id) => set({ dbId: id }),
    setError: (error) => set({ error }),
    clearError: () => set({ error: null }),

    // BST Operations
    loadBSTState: async () => {
        set({ loading: true, error: null })
        try {
            const result = await api.bst.getState(get().dbId)
            set({ bstState: result.data, lastBstInsertPath: [], lastBstDeletedId: null, lastBstDeletedNode: null })
        } catch (err) {
            set({ error: err.message })
        } finally {
            set({ loading: false })
        }
    },

    insertBSTNode: async (value) => {
        set({ loading: true, error: null })
        try {
            const result = await api.bst.insert(get().dbId, value)
            set({
                bstState: result.data,
                lastBstInsertPath: result?.insert?.path || [],
                lastBstDeletedId: null,
                lastBstDeletedNode: null,
            })
            return result
        } catch (err) {
            set({ error: err.message })
            return null
        } finally {
            set({ loading: false })
        }
    },

    deleteBSTNode: async (value) => {
        set({ loading: true, error: null })
        try {
            const previousRows = get().bstState || []
            const deletedNode = previousRows.find((node) => Number(node.id) === Number(value)) || null
            const result = await api.bst.delete(get().dbId, value)
            set({
                bstState: result.data,
                lastBstDeletedId: value,
                lastBstDeletedNode: deletedNode,
            })
            return result
        } catch (err) {
            set({ error: err.message })
            return null
        } finally {
            set({ loading: false })
        }
    },

    traverseBST: async (method) => {
        set({ loading: true, error: null })
        try {
            return await api.bst.traverse(get().dbId, method)
        } catch (err) {
            set({ error: err.message })
            return null
        } finally {
            set({ loading: false })
        }
    },

    // Hash Operations
    loadHashState: async () => {
        set({ loading: true, error: null })
        try {
            const result = await api.hash.getState(get().dbId)
            set({ hashState: result.data })
        } catch (err) {
            set({ error: err.message })
        } finally {
            set({ loading: false })
        }
    },

    insertHashItem: async (key, value) => {
        set({ loading: true, error: null })
        try {
            const result = await api.hash.insert(get().dbId, key, value)
            set({ hashState: result.data })
            return result
        } catch (err) {
            set({ error: err.message })
            return null
        } finally {
            set({ loading: false })
        }
    },

    deleteHashItem: async (key) => {
        set({ loading: true, error: null })
        try {
            const result = await api.hash.delete(get().dbId, key)
            set({ hashState: result.data })
            return result
        } catch (err) {
            set({ error: err.message })
            return null
        } finally {
            set({ loading: false })
        }
    },

    // Tree Operations
    loadTreeState: async () => {
        set({ loading: true, error: null })
        try {
            const result = await api.tree.getState(get().dbId)
            set({ treeState: result.data })
        } catch (err) {
            set({ error: err.message })
        } finally {
            set({ loading: false })
        }
    },

    insertTreeNode: async (parentId, value) => {
        set({ loading: true, error: null })
        try {
            const result = await api.tree.insert(get().dbId, parentId, value)
            set({ treeState: result.data })
            return result
        } catch (err) {
            set({ error: err.message })
            return null
        } finally {
            set({ loading: false })
        }
    },

    traverseTree: async (method) => {
        set({ loading: true, error: null })
        try {
            return await api.tree.traverse(get().dbId, method)
        } catch (err) {
            set({ error: err.message })
            return null
        } finally {
            set({ loading: false })
        }
    },

    loadRecursionState: async () => {
        set({ loading: true, error: null })
        try {
            const result = await api.recursion.getState(get().dbId)
            set({ recursionState: result.data })
        } catch (err) {
            set({ error: err.message })
        } finally {
            set({ loading: false })
        }
    },

    insertRecursionNode: async (parentId = -1, value = 0) => {
        set({ loading: true, error: null })
        try {
            const result = await api.recursion.insert(get().dbId, parentId, value)
            set({ recursionState: result.data })
            return result
        } catch (err) {
            set({ error: err.message })
            return null
        } finally {
            set({ loading: false })
        }
    },

    listDatabases: async () => {
        set({ loading: true, error: null })
        try {
            return await api.listDatabases()
        } catch (err) {
            set({ error: err.message })
            return null
        } finally {
            set({ loading: false })
        }
    },

    recreateDatabase: async () => {
        set({ loading: true, error: null })
        try {
            return await api.createDatabase('all', 'default')
        } catch (err) {
            set({ error: err.message })
            return null
        } finally {
            set({ loading: false })
        }
    },

    clearDatabase: async () => {
        set({ loading: true, error: null })
        try {
            return await api.clearDatabase(get().dbId)
        } catch (err) {
            set({ error: err.message })
            return null
        } finally {
            set({ loading: false })
        }
    }
}))
