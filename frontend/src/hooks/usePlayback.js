import { useEffect, useRef, useState } from 'react'

export const usePlayback = (steps = []) => {
    const [isPlaying, setIsPlaying] = useState(false)
    const [stepIndex, setStepIndex] = useState(0)
    const timerRef = useRef(null)

    const safeSteps = Array.isArray(steps) ? steps : []
    const maxIndex = Math.max(0, safeSteps.length - 1)

    useEffect(() => {
        setStepIndex(0)
        setIsPlaying(false)
    }, [safeSteps.length])

    useEffect(() => {
        if (!isPlaying || safeSteps.length === 0) {
            return
        }

        timerRef.current = setInterval(() => {
            setStepIndex((prev) => {
                if (prev >= maxIndex) {
                    setIsPlaying(false)
                    return prev
                }
                return prev + 1
            })
        }, 650)

        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current)
            }
        }
    }, [isPlaying, maxIndex, safeSteps.length])

    const play = () => {
        if (safeSteps.length > 0) {
            setIsPlaying(true)
        }
    }

    const pause = () => setIsPlaying(false)

    const reset = () => {
        setIsPlaying(false)
        setStepIndex(0)
    }

    const step = () => {
        setStepIndex((prev) => Math.min(maxIndex, prev + 1))
    }

    const activeStep = safeSteps[stepIndex] ?? null

    return {
        isPlaying,
        stepIndex,
        activeStep,
        maxIndex,
        play,
        pause,
        reset,
        step,
    }
}
