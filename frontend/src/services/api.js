/**
 * API Service - HTTP client for backend communication
 */
const API_BASE = "/api";

export const api = {
    // ===== BST =====
    bst: {
        getState: async (dbId) => {
            const res = await fetch(`${API_BASE}/bst/state/${dbId}`);
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        },
        insert: async (dbId, value) => {
            const res = await fetch(`${API_BASE}/bst/insert/${dbId}?value=${value}`, {
                method: "POST"
            });
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        },
        delete: async (dbId, value) => {
            const res = await fetch(`${API_BASE}/bst/delete/${dbId}?value=${value}`, {
                method: "POST"
            });
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        },
        traverse: async (dbId, method) => {
            const res = await fetch(`${API_BASE}/bst/traverse/${dbId}/${method}`);
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        }
    },

    // ===== HASH =====
    hash: {
        getState: async (dbId) => {
            const res = await fetch(`${API_BASE}/hash/state/${dbId}`);
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        },
        insert: async (dbId, key, value) => {
            const res = await fetch(
                `${API_BASE}/hash/insert/${dbId}?key=${encodeURIComponent(key)}&value=${encodeURIComponent(value)}`,
                { method: "POST" }
            );
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        },
        delete: async (dbId, key) => {
            const res = await fetch(`${API_BASE}/hash/delete/${dbId}?key=${encodeURIComponent(key)}`, {
                method: "POST"
            });
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        }
    },

    // ===== TREE =====
    tree: {
        getState: async (dbId) => {
            const res = await fetch(`${API_BASE}/tree/state/${dbId}`);
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        },
        insert: async (dbId, parentId, value) => {
            const res = await fetch(
                `${API_BASE}/tree/insert/${dbId}/${parentId}?value=${value}`,
                { method: "POST" }
            );
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        },
        traverse: async (dbId, method) => {
            const res = await fetch(`${API_BASE}/tree/traverse/${dbId}/${method}`);
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        }
    },

    // ===== RECURSION =====
    recursion: {
        getState: async (dbId) => {
            const res = await fetch(`${API_BASE}/recursion/state/${dbId}`);
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        },
        insert: async (dbId, parentId = -1, value = 0) => {
            const res = await fetch(
                `${API_BASE}/recursion/insert/${dbId}?parent_id=${parentId}&value=${value}`,
                { method: "POST" }
            );
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        }
    },

    // ===== GENERAL =====
    listDatabases: async () => {
        const res = await fetch(`${API_BASE}/list-databases`);
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },
    createDatabase: async (adtType, dbName = "default") => {
        const res = await fetch(
            `${API_BASE}/create-database/${adtType}?db_name=${dbName}`,
            { method: "POST" }
        );
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },
    clearDatabase: async (dbId) => {
        const res = await fetch(`${API_BASE}/clear-database/${dbId}`, {
            method: "DELETE"
        });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    }
};
