const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const path = require('path')
const fs = require('fs')

let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  })

  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5174')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
    title: '选择照片文件夹',
  })

  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0]
  }
  return null
})

ipcMain.handle('select-files', async (event, options = {}) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: options.filters || [
      { name: '图片文件', extensions: ['jpg', 'jpeg', 'png', 'cr2', 'cr3', 'nef', 'arw', 'raf', 'dng'] },
      { name: '所有文件', extensions: ['*'] },
    ],
    title: options.title || '选择照片',
  })

  if (!result.canceled) {
    return result.filePaths
  }
  return []
})

ipcMain.handle('scan-folder', async (event, { folderPath, includeSubfolders = true }) => {
  try {
    if (!fs.existsSync(folderPath)) {
      return { success: false, error: '文件夹不存在' }
    }

    const supportedRawFormats = ['.cr2', '.cr3', '.nef', '.arw', '.raf', '.orf', '.pef', '.srw', '.dng', '.rw2']
    const supportedImageFormats = ['.jpg', '.jpeg', '.png', '.tiff', '.heic']
    const allSupportedFormats = [...supportedRawFormats, ...supportedImageFormats]

    const photos = []

    function scanDirectory(dirPath) {
      if (!fs.existsSync(dirPath)) return

      const entries = fs.readdirSync(dirPath, { withFileTypes: true })

      for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name)

        if (entry.isDirectory()) {
          if (includeSubfolders) {
            scanDirectory(fullPath)
          }
        } else if (entry.isFile()) {
          const ext = path.extname(entry.name).toLowerCase()
          if (allSupportedFormats.includes(ext)) {
            const stats = fs.statSync(fullPath)
            const isRaw = supportedRawFormats.includes(ext)

            let captureTime = null
            let gpsLat = null
            let gpsLon = null

            try {
              const exifData = readExifData(fullPath)
              if (exifData) {
                captureTime = exifData.captureTime
                gpsLat = exifData.gpsLat
                gpsLon = exifData.gpsLon
              }
            } catch (e) {
              // ignore
            }

            photos.push({
              file_path: fullPath,
              file_name: entry.name,
              file_size: stats.size,
              capture_time: captureTime,
              gps_lat: gpsLat,
              gps_lon: gpsLon,
              is_raw: isRaw,
            })
          }
        }
      }
    }

    scanDirectory(folderPath)

    photos.sort((a, b) => {
      if (a.capture_time && b.capture_time) {
        return new Date(a.capture_time) - new Date(b.capture_time)
      }
      return a.file_name.localeCompare(b.file_name)
    })

    const rawPhotos = photos.filter(p => p.is_raw)
    const jpegPhotos = photos.filter(p => !p.is_raw)
    const photosWithGps = photos.filter(p => p.gps_lat !== null && p.gps_lon !== null)

    return {
      success: true,
      data: {
        total_photos: photos.length,
        raw_photos: rawPhotos.length,
        jpeg_photos: jpegPhotos.length,
        photos_with_gps: photosWithGps.length,
        photos: photos,
      },
    }
  } catch (error) {
    return { success: false, error: error.message }
  }
})

function readExifData(filePath) {
  try {
    const buffer = fs.readFileSync(filePath)
    const ext = path.extname(filePath).toLowerCase()

    if (ext === '.jpg' || ext === '.jpeg') {
      const dateTimeMatch = buffer.toString('latin1').match(/(\d{4}):(\d{2}):(\d{2}) (\d{2}):(\d{2}):(\d{2})/)
      if (dateTimeMatch) {
        const [, year, month, day, hour, min, sec] = dateTimeMatch
        return {
          captureTime: `${year}-${month}-${day}T${hour}:${min}:${sec}`,
          gpsLat: null,
          gpsLon: null,
        }
      }
    }

    const stats = fs.statSync(filePath)
    return {
      captureTime: stats.mtime.toISOString(),
      gpsLat: null,
      gpsLon: null,
    }
  } catch (e) {
    return null
  }
}

ipcMain.handle('identify-birds', async (event, photoPaths) => {
  try {
    return {
      success: true,
      data: {
        total_photos: photoPaths.length,
        photos_with_birds: 0,
        detections: [],
        burst_groups: [],
      },
    }
  } catch (error) {
    return { success: false, error: error.message }
  }
})

ipcMain.handle('get-species-list', async () => {
  try {
    return { success: true, data: [] }
  } catch (error) {
    return { success: false, error: error.message }
  }
})

ipcMain.handle('get-daily-map', async (event, mapDate, photoLocations) => {
  try {
    return {
      success: true,
      data: {
        total_photos: 0,
        total_locations: 0,
        bird_species_count: 0,
        species_summary: {},
        points: [],
        map_html: null,
      },
    }
  } catch (error) {
    return { success: false, error: error.message }
  }
})

ipcMain.handle('test-llm-connection', async (event, config) => {
  const http = require('http')
  const https = require('https')
  const { URL } = require('url')

  return new Promise((resolve) => {
    try {
      const baseUrl = config.baseUrl.replace(/\/$/, '')
      const parsedUrl = new URL(baseUrl)
      const isHttps = parsedUrl.protocol === 'https:'

      // 直接使用 POST /chat/completions 测试连接
      const options = {
        hostname: parsedUrl.hostname,
        port: parsedUrl.port || (isHttps ? 443 : 80),
        path: '/chat/completions',
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${config.apiKey}`,
          'Content-Type': 'application/json',
        },
        timeout: (config.timeout || 30) * 1000,
      }

      const lib = isHttps ? https : http

      const req = lib.request(options, (res) => {
        let data = ''

        res.on('data', (chunk) => {
          data += chunk
        })

        res.on('end', () => {
          // 200 表示成功，4xx 表示认证失败或其他客户端错误，5xx 表示服务器错误
          if (res.statusCode === 200) {
            resolve({ success: true, message: '连接成功' })
          } else if (res.statusCode === 401) {
            resolve({ success: false, message: 'API Key 无效' })
          } else if (res.statusCode === 400) {
            // 可能是模型不支持，但连接是通的
            resolve({ success: true, message: '连接成功（模型可能不支持）' })
          } else {
            resolve({ success: false, message: `连接失败：${res.statusCode} ${res.statusMessage}` })
          }
        })
      })

      req.on('error', (e) => {
        resolve({ success: false, message: `连接失败：${e.message}` })
      })

      req.on('timeout', () => {
        req.destroy()
        resolve({ success: false, message: '请求超时' })
      })

      // 发送一个简单的测试请求
      req.write(JSON.stringify({
        model: config.model,
        messages: [{ role: 'user', content: 'Hello' }],
        max_tokens: 10,
      }))
      req.end()
    } catch (error) {
      resolve({ success: false, message: `连接失败：${error.message}` })
    }
  })
})

ipcMain.handle('check-backend', async () => {
  try {
    const http = require('http')
    return new Promise((resolve) => {
      const req = http.get('http://localhost:8000', (res) => {
        if (res.statusCode === 200) {
          resolve({ success: true })
        } else {
          resolve({ success: false, error: '后端服务未响应' })
        }
      })

      req.on('error', () => {
        resolve({ success: false, error: '无法连接到后端服务' })
      })

      req.setTimeout(3000, () => {
        req.destroy()
        resolve({ success: false, error: '连接超时' })
      })
    })
  } catch (error) {
    return { success: false, error: error.message }
  }
})

ipcMain.handle('get-app-path', (event, name) => {
  return app.getPath(name)
})

ipcMain.handle('open-external', (event, url) => {
  require('electron').shell.openExternal(url)
})
