import React, { useCallback } from 'react'
import './ImageUploader.css'

function ImageUploader({ onUpload }) {
  const handleDrop = useCallback((e) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      handleFile(file)
    }
  }, [onUpload])

  const handleFileInput = (e) => {
    const file = e.target.files[0]
    if (file) {
      handleFile(file)
    }
  }

  const handleFile = (file) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      onUpload(file, e.target.result)
    }
    reader.readAsDataURL(file)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  return (
    <div
      className="uploader"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <div className="uploader-content">
        <div className="uploader-icon">📷</div>
        <h2>上传照片</h2>
        <p>拖拽图片到此处，或点击选择文件</p>
        <p className="uploader-hint">支持 JPG、PNG 格式</p>
        <label className="upload-btn">
          <input
            type="file"
            accept="image/jpeg,image/png,image/jpg"
            onChange={handleFileInput}
            style={{ display: 'none' }}
          />
          选择图片
        </label>
      </div>
    </div>
  )
}

export default ImageUploader
