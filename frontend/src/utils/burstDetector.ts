// 连拍组识别工具
// 根据照片拍摄时间间隔自动分组连拍照片

export interface Photo {
  file_path: string
  file_name: string
  capture_time: string | null
  is_raw: boolean
}

export interface BurstGroup {
  group_id: string
  photos: Photo[]
  photo_count: number
  start_time: string
  end_time: string
  time_span_seconds: number
  cover_photo?: Photo
}

/**
 * 将照片按时间间隔分组为连拍组
 * @param photos 照片列表，应按时间排序
 * @param thresholdSeconds 连拍阈值（秒），默认 3 秒
 * @returns 连拍组数组
 */
export function groupBurstPhotos(photos: Photo[], thresholdSeconds: number = 3): BurstGroup[] {
  if (photos.length === 0) return []

  // 按拍摄时间排序
  const sortedPhotos = [...photos].sort((a, b) => {
    if (!a.capture_time || !b.capture_time) return 0
    return new Date(a.capture_time).getTime() - new Date(b.capture_time).getTime()
  })

  const groups: BurstGroup[] = []
  let currentGroup: Photo[] = [sortedPhotos[0]]

  for (let i = 1; i < sortedPhotos.length; i++) {
    const prevPhoto = sortedPhotos[i - 1]
    const currPhoto = sortedPhotos[i]

    if (!prevPhoto.capture_time || !currPhoto.capture_time) {
      // 没有时间信息的照片单独成组
      groups.push(createGroup([...currentGroup]))
      currentGroup = []
      continue
    }

    const prevTime = new Date(prevPhoto.capture_time).getTime()
    const currTime = new Date(currPhoto.capture_time).getTime()
    const timeDiff = (currTime - prevTime) / 1000

    if (timeDiff <= thresholdSeconds) {
      // 时间间隔在阈值内，加入当前连拍组
      currentGroup.push(currPhoto)
    } else {
      // 时间间隔超出阈值，开始新组
      if (currentGroup.length > 0) {
        groups.push(createGroup(currentGroup))
      }
      currentGroup = [currPhoto]
    }
  }

  // 添加最后一组
  if (currentGroup.length > 0) {
    groups.push(createGroup(currentGroup))
  }

  return groups.filter(g => g.photo_count >= 1)
}

function createGroup(photos: Photo[]): BurstGroup {
  const startTime = photos[0].capture_time || new Date().toISOString()
  const endTime = photos[photos.length - 1].capture_time || new Date().toISOString()
  const _timeSpanSeconds = (new Date(endTime).getTime() - new Date(startTime).getTime()) / 1000

  return {
    group_id: `burst_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    photos,
    photo_count: photos.length,
    start_time: startTime,
    end_time: endTime,
    time_span_seconds: _timeSpanSeconds,
    cover_photo: photos[0],
  }
}

/**
 * 从连拍组中选择最佳照片
 * 简化版本：选择第一张作为封面
 * 可以扩展为基于清晰度、曝光等选择
 */
export function selectBestPhotoFromGroup(group: BurstGroup): Photo {
  // TODO: 实现更智能的最佳照片选择
  // 可以考虑：清晰度、曝光、对焦、是否有模糊等
  return group.cover_photo || group.photos[0]
}

/**
 * 获取非连拍的照片（单张照片）
 */
export function getSinglePhotos(photos: Photo[], burstGroups: BurstGroup[]): Photo[] {
  const burstPhotoPaths = new Set(
    burstGroups.flatMap(g => g.photos.map(p => p.file_path))
  )
  return photos.filter(p => !burstPhotoPaths.has(p.file_path))
}
