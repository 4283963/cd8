import React, { useState, useRef } from 'react'
import './Preview.css'

function Preview({ originalImage, processedImage, compareMode, isProcessing, onReset, onDownload, onToggleCompare }) {
  const [sliderPosition, setSliderPosition] = useState(50)
  const [isDragging, setIsDragging] = useState(false)
  const containerRef = useRef(null)

  const handleMouseDown = (e) => {
    if (!compareMode) return
    setIsDragging(true)
    updateSliderPosition(e)
  }

  const handleMouseMove = (e) => {
    if (!isDragging || !compareMode) return
    updateSliderPosition(e)
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  const updateSliderPosition = (e) => {
    if (!containerRef.current) return
    const rect = containerRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const percent = Math.max(0, Math.min(100, (x / rect.width) * 100))
    setSliderPosition(percent)
  }

  const displayImage = processedImage || originalImage

  return (
    <div className="preview-container">
      <div className="preview-toolbar">
        <button className="toolbar-btn" onClick={onReset} title="重新上传">
          ↻ 重新上传
        </button>
        <button
          className={`toolbar-btn ${compareMode ? 'active' : ''}`}
          onClick={onToggleCompare}
          title="对比原图"
        >
          {compareMode ? '关闭对比' : '对比原图'}
        </button>
        <button className="toolbar-btn" onClick={onDownload} title="下载">
          ⬇ 下载
        </button>
      </div>

      <div
        className="preview-image-container"
        ref={containerRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {compareMode ? (
          <>
            <img src={originalImage} alt="original" className="preview-image base-image" />
            <div
              className="preview-image clipped-image"
              style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
            >
              <img src={displayImage} alt="processed" className="preview-image" />
            </div>
            <div
              className="compare-slider"
              style={{ left: `${sliderPosition}%` }}
            >
              <div className="compare-slider-line"></div>
              <div className="compare-slider-handle">⟷</div>
            </div>
            <div className="compare-labels">
              <span className="compare-label left">原图</span>
              <span className="compare-label right">效果</span>
            </div>
          </>
        ) : (
          <img src={displayImage} alt="preview" className="preview-image single-image" />
        )}

        {isProcessing && (
          <div className="processing-overlay">
            <div className="processing-spinner"></div>
            <span>处理中...</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default Preview
