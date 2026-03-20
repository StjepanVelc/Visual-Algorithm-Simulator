/**
 * API Service - HTTP client for backend communication
 */
const API_BASE = "/api";

async function throwApiError(res) {
    const text = await res.text();
    let msg = text;
    try {
        const json = JSON.parse(text);
        if (json.detail) msg = json.detail;
    } catch {
        // keep raw text
    }
    throw new Error(msg);
}

export const api = {
    // ===== BST =====
    bst: {
        getState: async (dbId) => {
            const res = await fetch(`${API_BASE}/bst/state/${dbId}`);
            if (!res.ok) await throwApiError(res);
            return res.json();
        },
        insert: async (dbId, value) => {
            const res = await fetch(`${API_BASE}/bst/insert/${dbId}?value=${value}`, {
                method: "POST"
            });
            if (!res.ok) await throwApiError(res);
            return res.json();
        },
        delete: async (dbId, value) => {
            const res = await fetch(`${API_BASE}/bst/delete/${dbId}?value=${value}`, {
                method: "POST"
            });
            if (!res.ok) await throwApiError(res);
            return res.json();
        },
        traverse: async (dbId, method, searchValue = null) => {
            const url = searchValue
                ? `${API_BASE}/bst/traverse/${dbId}/${method}?search_value=${encodeURIComponent(searchValue)}`
                : `${API_BASE}/bst/traverse/${dbId}/${method}`
            const res = await fetch(url);
            if (!res.ok) await throwApiError(res);
            return res.json();
        }
    },

    // ===== HASH =====
    hash: {
        getState: async (dbId) => {
            const res = await fetch(`${API_BASE}/hash/state/${dbId}`);
            if (!res.ok) await throwApiError(res);
            return res.json();
        },
        insert: async (dbId, key, value) => {
            const res = await fetch(
                `${API_BASE}/hash/insert/${dbId}?key=${encodeURIComponent(key)}&value=${encodeURIComponent(value)}`,
                { method: "POST" }
            );
            if (!res.ok) await throwApiError(res);
            return res.json();
        },
        delete: async (dbId, key) => {
            const res = await fetch(`${API_BASE}/hash/delete/${dbId}?key=${encodeURIComponent(key)}`, {
                method: "POST"
            });
            if (!res.ok) await throwApiError(res);
            return res.json();
        }
    },

    // ===== TREE =====
    tree: {
        getState: async (dbId) => {
            const res = await fetch(`${API_BASE}/tree/state/${dbId}`);
            if (!res.ok) await throwApiError(res);
            return res.json();
        },
        insert: async (dbId, parentId, value) => {
            const res = await fetch(
                `${API_BASE}/tree/insert/${dbId}/${parentId}?value=${value}`,
                { method: "POST" }
            );
            if (!res.ok) await throwApiError(res);
            return res.json();
        },
        traverse: async (dbId, method) => {
            const res = await fetch(`${API_BASE}/tree/traverse/${dbId}/${method}`);
            if (!res.ok) await throwApiError(res);
            return res.json();
        }
    },

    advanced: {
        getState: async (treeType, dbId) => {
            const res = await fetch(`${API_BASE}/advanced/${treeType}/state/${dbId}`)
            if (!res.ok) await throwApiError(res)
            return res.json()
        },
        insert: async (treeType, dbId, value) => {
            const res = await fetch(`${API_BASE}/advanced/${treeType}/insert/${dbId}?value=${value}`, {
                method: 'POST',
            })
            if (!res.ok) await throwApiError(res)
            return res.json()
        },
        delete: async (treeType, dbId, value) => {
            const res = await fetch(`${API_BASE}/advanced/${treeType}/delete/${dbId}?value=${value}`, {
                method: 'POST',
            })
            if (!res.ok) await throwApiError(res)
            return res.json()
        },
        search: async (treeType, dbId, value) => {
            const res = await fetch(`${API_BASE}/advanced/${treeType}/search/${dbId}?value=${value}`)
            if (!res.ok) await throwApiError(res)
            return res.json()
        },
        traverse: async (treeType, dbId, method) => {
            const res = await fetch(`${API_BASE}/advanced/${treeType}/traverse/${dbId}/${method}`)
            if (!res.ok) await throwApiError(res)
            return res.json()
        },
        reset: async (treeType, dbId) => {
            const res = await fetch(`${API_BASE}/advanced/${treeType}/reset/${dbId}`, {
                method: 'DELETE',
            })
            if (!res.ok) await throwApiError(res)
            return res.json()
        },
    },

    // ===== RECURSION =====
    recursion: {
        getState: async (dbId) => {
            const res = await fetch(`${API_BASE}/recursion/state/${dbId}`);
            if (!res.ok) await throwApiError(res);
            return res.json();
        },
        insert: async (dbId, parentId = -1, value = 0) => {
            const res = await fetch(
                `${API_BASE}/recursion/insert/${dbId}?parent_id=${parentId}&value=${value}`,
                { method: "POST" }
            );
            if (!res.ok) await throwApiError(res);
            return res.json();
        }
    },

    // ===== GENERAL =====
    listDatabases: async () => {
        const res = await fetch(`${API_BASE}/list-databases`);
        if (!res.ok) await throwApiError(res);
        return res.json();
    },
    createDatabase: async (adtType, dbName = "default") => {
        const res = await fetch(
            `${API_BASE}/create-database/${adtType}?db_name=${dbName}`,
            { method: "POST" }
        );
        if (!res.ok) await throwApiError(res);
        return res.json();
    },
    clearDatabase: async (dbId) => {
        const res = await fetch(`${API_BASE}/clear-database/${dbId}`, {
            method: "DELETE"
        });
        if (!res.ok) await throwApiError(res);
        return res.json();
    }
};
