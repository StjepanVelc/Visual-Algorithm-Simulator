const registry = new Map()

export const registerAlgorithm = (id, config) => {
    if (!id || typeof id !== 'string') {
        throw new Error('Algorithm id must be a non-empty string')
    }
    registry.set(id, { id, ...config })
}

export const getRegisteredAlgorithms = () => [...registry.values()]

export const hasAlgorithm = (id) => registry.has(id)
