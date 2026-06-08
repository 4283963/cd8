import React, { useState } from 'react'
import './RecipeSelector.css'

const CATEGORY_NAMES = {
  portrait: '人像',
  landscape: '风景',
  classic: '经典',
  bw: '黑白',
  vintage: '复古',
  cinematic: '电影',
  slide: '反转片',
  toy: '玩具相机',
  custom: '自定义'
}

function RecipeSelector({ recipes, categories, selectedRecipeId, onSelect, onSaveClick }) {
  const [activeCategory, setActiveCategory] = useState('all')
  const [showAll, setShowAll] = useState(false)

  const filteredRecipes = activeCategory === 'all'
    ? recipes
    : recipes.filter(r => r.category === activeCategory)

  const displayRecipes = showAll ? filteredRecipes : filteredRecipes.slice(0, 6)

  return (
    <div className="recipe-selector">
      <div className="selector-header">
        <h3 className="selector-title">🎞️ 胶片配方</h3>
        <button className="save-btn" onClick={onSaveClick}>
          + 保存当前
        </button>
      </div>

      <div className="category-tabs">
        <button
          className={`category-tab ${activeCategory === 'all' ? 'active' : ''}`}
          onClick={() => setActiveCategory('all')}
        >
          全部
        </button>
        {categories.slice(0, 4).map((cat) => (
          <button
            key={cat}
            className={`category-tab ${activeCategory === cat ? 'active' : ''}`}
            onClick={() => setActiveCategory(cat)}
          >
            {CATEGORY_NAMES[cat] || cat}
          </button>
        ))}
      </div>

      <div className="recipe-grid">
        <button
          className={`recipe-card ${selectedRecipeId === null ? 'selected' : ''}`}
          onClick={() => onSelect(null)}
        >
          <div className="recipe-icon">⬜</div>
          <div className="recipe-info">
            <span className="recipe-name">原图</span>
            <span className="recipe-cat">无效果</span>
          </div>
        </button>

        {displayRecipes.map((recipe) => (
          <button
            key={recipe.id}
            className={`recipe-card ${selectedRecipeId === recipe.id ? 'selected' : ''}`}
            onClick={() => onSelect(recipe)}
          >
            <div className="recipe-icon">
              {recipe.category === 'bw' ? '⬛' :
               recipe.category === 'vintage' ? '📜' :
               recipe.category === 'cinematic' ? '🎬' :
               recipe.category === 'landscape' ? '🏔️' :
               recipe.category === 'portrait' ? '👤' :
               recipe.category === 'slide' ? '🌈' :
               recipe.category === 'toy' ? '📷' : '🎞️'}
            </div>
            <div className="recipe-info">
              <span className="recipe-name">{recipe.name}</span>
              <span className="recipe-cat">
                {recipe.is_builtin ? '内置' : '自定义'}
              </span>
            </div>
          </button>
        ))}
      </div>

      {filteredRecipes.length > 6 && (
        <button
          className="show-more-btn"
          onClick={() => setShowAll(!showAll)}
        >
          {showAll ? '收起' : `展开全部 (${filteredRecipes.length})`}
        </button>
      )}
    </div>
  )
}

export default RecipeSelector
