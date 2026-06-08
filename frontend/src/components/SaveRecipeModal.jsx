import React, { useState } from 'react'
import './SaveRecipeModal.css'

const CATEGORY_NAMES = {
  custom: '自定义',
  portrait: '人像',
  landscape: '风景',
  classic: '经典',
  vintage: '复古',
  cinematic: '电影'
}

function SaveRecipeModal({ onClose, onSave, categories }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('custom')
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!name.trim()) {
      setError('请输入配方名称')
      return
    }
    onSave(name.trim(), description.trim(), category)
  }

  const availableCategories = ['custom', ...categories.filter(c => c !== 'custom')]

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>保存胶片配方</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          <div className="form-group">
            <label>配方名称 *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="例如：我的复古风格"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>分类</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="form-input"
            >
              {availableCategories.map((cat) => (
                <option key={cat} value={cat}>
                  {CATEGORY_NAMES[cat] || cat}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>描述（可选）</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="简单描述这个配方的特点..."
              className="form-input form-textarea"
              rows={3}
            />
          </div>

          {error && <div className="form-error">{error}</div>}

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              取消
            </button>
            <button type="submit" className="btn btn-primary">
              保存
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default SaveRecipeModal
