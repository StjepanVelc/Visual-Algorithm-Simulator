import React from 'react'

const PlaybackControls = ({ machine, onPlay, onPause, onStep, onReset }) => {
    const total = machine?.traversalOrder?.length || 0
    const current = machine?.currentStep || 0
    const isPlaying = machine?.mode === 'running'

    return (
        <div className="playback-bar">
            <button onClick={onPlay} disabled={isPlaying || total === 0}>Play</button>
            <button onClick={onPause} disabled={!isPlaying}>Pause</button>
            <button onClick={onStep} disabled={total === 0}>Step</button>
            <button onClick={onReset} disabled={total === 0}>Reset</button>
            <span className="playback-meta">Mode: {machine?.mode || 'idle'}</span>
            <span className="playback-meta">Step {total === 0 ? 0 : current + 1} / {Math.max(total, 0)}</span>
        </div>
    )
}

export default PlaybackControls
