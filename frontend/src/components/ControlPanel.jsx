import React from 'react'
import './ControlPanel.css'

const SLIDER_GROUPS = [
  {
    title: '基础调整',
    sliders: [
      { key: 'brightness', label: '亮度', min: -100, max: 100, step: 1, default: 0 },
      { key: 'contrast', label: '对比度', min: 0.5, max: 2.0, step: 0.01, default: 1.0 },
      { key: 'saturation', label: '饱和度', min: 0, max: 2.0, step: 0.01, default: 1.0 },
    ]
  },
  {
    title: '色彩风格',
    sliders: [
      { key: 'temperature', label: '色温', min: -100, max: 100, step: 1, default: 0 },
      { key: 'fade', label: '褪色', min: 0, max: 100, step: 1, default: 0 },
    ]
  },
  {
    title: '胶片质感',
    sliders: [
      { key: 'grain_amount', label: '颗粒强度', min: 0, max: 100, step: 1, default: 0 },
      { key: 'grain_size', label: '颗粒大小', min: 0.5, max: 3.0, step: 0.1, default: 1.0 },
      { key: 'scratch_amount', label: '划痕灰尘', min: 0, max: 100, step: 1, default: 0 },
    ]
  },
  {
    title: '光影效果',
    sliders: [
      { key: 'vignette', label: '暗角', min: 0, max: 100, step: 1, default: 0 },
    ]
  }
]

function ControlPanel({ params, onChange, onReset, disabled }) {
  const displayValue = (value, slider) => {
    if (slider.step >= 1) {
      return Math.round(value)
    }
    return value.toFixed(2)
  }

  return (
    <div className={`control-panel ${disabled ? 'disabled' : ''}`}>
      {SLIDER_GROUPS.map((group) => (
        <div key={group.title} className="slider-group">
          <h3 className="group-title">{group.title}</h3>
          <div className="sliders">
            {group.sliders.map((slider) => (
              <div key={slider.key} className="slider-item">
                <div className="slider-header">
                  <span className="slider-label">{slider.label}</span>
                  <span className="slider-value">
                    {displayValue(params[slider.key] ?? slider.default, slider)}
                  </span>
                </div>
                <input
                  type="range"
                  min={slider.min}
                  max={slider.max}
                  step={slider.step}
                  value={params[slider.key] ?? slider.default}
                  onChange={(e) => onChange(slider.key, parseFloat(e.target.value))}
                  disabled={disabled}
                  className="slider-input"
                />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export default ControlPanel
