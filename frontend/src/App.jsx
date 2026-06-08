import React, { useState, useEffect, useRef, useCallback } from 'react'
import ImageUploader from './components/ImageUploader.jsx'
import ControlPanel from './components/ControlPanel.jsx'
import Preview from './components/Preview.jsx'
import RecipeSelector from './components/RecipeSelector.jsx'
import SaveRecipeModal from './components/SaveRecipeModal.jsx'
import './App.css'

const DEFAULT_PARAMS = {
  saturation: 1.0,
  contrast: 1.0,
  brightness: 0,
  temperature: 0,
  grain_amount: 0,
  grain_size: 1.0,
  vignette: 0,
  scratch_amount: 0,
  fade: 0
}

function App() {
  const [originalImage, setOriginalImage] = useState(null)
  const [processedImage, setProcessedImage] = useState(null)
  const [params, setParams] = useState(DEFAULT_PARAMS)
  const [recipes, setRecipes] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedRecipeId, setSelectedRecipeId] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [showSaveModal, setShowSaveModal] = useState(false)
  const [compareMode, setCompareMode] = useState(false)
  const debounceRef = useRef(null)
  const imageFileRef = useRef(null)
  const abortControllerRef = useRef(null)
  const requestVersionRef = useRef(0)
  const processedImageUrlRef = useRef(null)

  useEffect(() => {
    fetchRecipes()
    fetchCategories()
  }, [])

  const fetchRecipes = async () => {
    try {
      const res = await fetch('/api/recipes')
      const data = await res.json()
      setRecipes(data.recipes || [])
    } catch (e) {
      console.error('Failed to fetch recipes:', e)
    }
  }

  const fetchCategories = async () => {
    try {
      const res = await fetch('/api/categories')
      const data = await res.json()
      setCategories(data.categories || [])
    } catch (e) {
      console.error('Failed to fetch categories:', e)
    }
  }

  const processImage = useCallback(async (imageData, currentParams) => {
    if (!imageData) return

    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    const abortController = new AbortController()
    abortControllerRef.current = abortController

    const myVersion = ++requestVersionRef.current

    setIsProcessing(true)

    try {
      const formData = new FormData()
      formData.append('image', imageData)
      formData.append('params', JSON.stringify(currentParams))

      const res = await fetch('/api/process', {
        method: 'POST',
        body: formData,
        signal: abortController.signal
      })

      if (myVersion !== requestVersionRef.current) {
        return
      }

      if (res.ok) {
        const blob = await res.blob()

        if (myVersion !== requestVersionRef.current) {
          return
        }

        const url = URL.createObjectURL(blob)

        if (processedImageUrlRef.current) {
          URL.revokeObjectURL(processedImageUrlRef.current)
        }
        processedImageUrlRef.current = url

        setProcessedImage(url)
      }
    } catch (e) {
      if (e.name === 'AbortError') {
        return
      }
      console.error('Processing failed:', e)
    } finally {
      if (myVersion === requestVersionRef.current) {
        setIsProcessing(false)
      }
      if (abortControllerRef.current === abortController) {
        abortControllerRef.current = null
      }
    }
  }, [])

  const debouncedProcess = useCallback((imageData, currentParams) => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }
    debounceRef.current = setTimeout(() => {
      processImage(imageData, currentParams)
    }, 300)
  }, [processImage])

  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      if (processedImageUrlRef.current) {
        URL.revokeObjectURL(processedImageUrlRef.current)
      }
    }
  }, [])

  const handleImageUpload = (file, dataUrl) => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
      debounceRef.current = null
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    requestVersionRef.current = 0

    imageFileRef.current = file
    setOriginalImage(dataUrl)
    setProcessedImage(null)
    setSelectedRecipeId(null)

    if (processedImageUrlRef.current) {
      URL.revokeObjectURL(processedImageUrlRef.current)
      processedImageUrlRef.current = null
    }

    processImage(file, params)
  }

  const handleParamChange = (key, value) => {
    const newParams = { ...params, [key]: value }
    setParams(newParams)
    setSelectedRecipeId(null)

    if (imageFileRef.current) {
      debouncedProcess(imageFileRef.current, newParams)
    }
  }

  const handleRecipeSelect = async (recipe) => {
    if (!recipe) {
      setParams(DEFAULT_PARAMS)
      setSelectedRecipeId(null)
      if (imageFileRef.current) {
        debouncedProcess(imageFileRef.current, DEFAULT_PARAMS)
      }
      return
    }

    setSelectedRecipeId(recipe.id)

    const recipeParams = {}
    Object.keys(DEFAULT_PARAMS).forEach(key => {
      if (recipe[key] !== undefined && recipe[key] !== null) {
        recipeParams[key] = recipe[key]
      }
    })

    setParams(recipeParams)

    if (imageFileRef.current) {
      debouncedProcess(imageFileRef.current, recipeParams)
    }
  }

  const handleReset = () => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
      debounceRef.current = null
    }
    setParams(DEFAULT_PARAMS)
    setSelectedRecipeId(null)
    if (imageFileRef.current) {
      processImage(imageFileRef.current, DEFAULT_PARAMS)
    }
  }

  const handleSaveRecipe = async (name, description, category) => {
    try {
      const res = await fetch('/api/recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          description,
          category,
          params
        })
      })

      if (res.ok) {
        await fetchRecipes()
        setShowSaveModal(false)
      }
    } catch (e) {
      console.error('Failed to save recipe:', e)
    }
  }

  const handleDownload = () => {
    if (!processedImage) return
    const link = document.createElement('a')
    link.href = processedImage
    link.download = 'film-simulated.jpg'
    link.click()
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🎞️ 复古胶片色彩模拟器</h1>
          <p>让数码照片拥有传统胶片的质感</p>
        </div>
      </header>

      <main className="app-main">
        <div className="main-content">
          <div className="preview-section">
            {!originalImage ? (
              <ImageUploader onUpload={handleImageUpload} />
            ) : (
              <Preview
                originalImage={originalImage}
                processedImage={processedImage}
                compareMode={compareMode}
                isProcessing={isProcessing}
                onReset={() => {
                  setOriginalImage(null)
                  setProcessedImage(null)
                  imageFileRef.current = null
                }}
                onDownload={handleDownload}
                onToggleCompare={() => setCompareMode(!compareMode)}
              />
            )}
          </div>

          <div className="control-section">
            <RecipeSelector
              recipes={recipes}
              categories={categories}
              selectedRecipeId={selectedRecipeId}
              onSelect={handleRecipeSelect}
              onSaveClick={() => setShowSaveModal(true)}
            />

            <ControlPanel
              params={params}
              onChange={handleParamChange}
              onReset={handleReset}
              disabled={!originalImage}
            />

            {originalImage && (
              <div className="action-buttons">
                <button className="btn btn-secondary" onClick={handleReset}>
                  重置参数
                </button>
                <button
                  className="btn btn-primary"
                  onClick={handleDownload}
                  disabled={!processedImage || isProcessing}
                >
                  下载图片
                </button>
              </div>
            )}
          </div>
        </div>
      </main>

      {showSaveModal && (
        <SaveRecipeModal
          onClose={() => setShowSaveModal(false)}
          onSave={handleSaveRecipe}
          categories={categories}
        />
      )}
    </div>
  )
}

export default App
