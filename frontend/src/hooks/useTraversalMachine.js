import { useEffect, useMemo, useRef, useState } from 'react'

const initialState = {
    mode: 'idle', // idle | running | paused
    currentStep: 0,
    traversalOrder: [],
}

export const useTraversalMachine = (order = []) => {
    const timerRef = useRef(null)
    const safeOrder = useMemo(() => (Array.isArray(order) ? order : []), [order])
    const [state, setState] = useState({ ...initialState, traversalOrder: safeOrder })

    useEffect(() => {
        setState({ mode: 'idle', currentStep: 0, traversalOrder: safeOrder })
    }, [safeOrder])

    useEffect(() => {
        if (state.mode !== 'running' || state.traversalOrder.length === 0) {
            return
        }

        timerRef.current = setInterval(() => {
            setState((prev) => {
                if (prev.currentStep >= prev.traversalOrder.length - 1) {
                    return { ...prev, mode: 'paused' }
                }
                return { ...prev, currentStep: prev.currentStep + 1 }
            })
        }, 650)

        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current)
            }
        }
    }, [state.mode, state.traversalOrder.length])

    const play = () => {
        setState((prev) => (prev.traversalOrder.length ? { ...prev, mode: 'running' } : prev))
    }

    const pause = () => {
        setState((prev) => ({ ...prev, mode: 'paused' }))
    }

    const step = () => {
        setState((prev) => {
            if (!prev.traversalOrder.length) {
                return prev
            }
            const next = Math.min(prev.currentStep + 1, prev.traversalOrder.length - 1)
            return { ...prev, mode: 'paused', currentStep: next }
        })
    }

    const reset = () => {
        setState((prev) => ({ ...prev, mode: 'idle', currentStep: 0 }))
    }

    const activeStep = state.traversalOrder[state.currentStep] ?? null

    return {
        state,
        activeStep,
        play,
        pause,
        step,
        reset,
    }
}
