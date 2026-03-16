/**
 * 前端 API 客户端单元测试
 * 运行方式：npm test -- tests/api.test.js
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';

// 模拟 localStorage
const mockLocalStorage = {
  store: {},
  getItem(key) {
    return this.store[key] || null;
  },
  setItem(key, value) {
    this.store[key] = String(value);
  },
  removeItem(key) {
    delete this.store[key];
  },
  clear() {
    this.store = {};
  }
};

// 在模块加载前设置 localStorage mock
Object.defineProperty(global, 'localStorage', {
  value: mockLocalStorage,
  writable: true
});

// 模拟 fetch
global.fetch = vi.fn();

describe('API Client Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocalStorage.clear();
  });

  describe('checkLLMConfigured', () => {
    it('should return false when no config', async () => {
      const { checkLLMConfigured } = await import('../src/api/api.ts');
      const { configured, config } = checkLLMConfigured();
      expect(configured).toBe(false);
      expect(config).toBe(null);
    });

    it('should return true when config exists', async () => {
      // 先设置配置，再加载模块
      const testConfig = {
        provider: 'Anthropic',
        baseUrl: 'https://api.example.com',
        apiKey: 'test-key',
        model: 'claude-sonnet',
        timeout: 60
      };
      mockLocalStorage.setItem('llm_api_config', JSON.stringify(testConfig));

      // 重新加载模块以读取新的 localStorage
      vi.resetModules();
      const { checkLLMConfigured } = await import('../src/api/api.ts');
      const { configured, config } = checkLLMConfigured();
      expect(configured).toBe(true);
      expect(config).toEqual(testConfig);
    });
  });

  describe('scanApi', () => {
    it('should call scan endpoint with correct parameters', async () => {
      const { scanApi } = await import('../src/api/api.ts');

      const mockResponse = {
        ok: true,
        json: async () => ({ photos: [], total: 0 })
      };

      global.fetch.mockResolvedValue(mockResponse);

      const result = await scanApi.scan('/test/photos', true);

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/scan/scan',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            folder_path: '/test/photos',
            include_subfolders: true
          })
        })
      );

      expect(result.data).toEqual({ photos: [], total: 0 });
    });

    it('should get supported formats', async () => {
      const { scanApi } = await import('../src/api/api.ts');

      const mockFormats = {
        raw_formats: ['.cr2', '.nef'],
        image_formats: ['.jpg', '.png']
      };

      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockFormats
      });

      const result = await scanApi.getSupportedFormats();

      expect(result.data).toEqual(mockFormats);
    });
  });

  describe('birdsApi', () => {
    it('should call identify endpoint', async () => {
      const { birdsApi } = await import('../src/api/api.ts');

      const mockResponse = {
        ok: true,
        json: async () => ({
          total_photos: 1,
          photos_with_birds: 1,
          detections: []
        })
      };

      global.fetch.mockResolvedValue(mockResponse);

      const result = await birdsApi.identify(['/test/photo.jpg']);

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/birds/identify',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ photo_paths: ['/test/photo.jpg'] })
        })
      );
    });

    it('should get species list', async () => {
      const { birdsApi } = await import('../src/api/api.ts');

      const mockSpecies = [
        { species_cn: '麻雀', species_en: 'sparrow' },
        { species_cn: '鸽子', species_en: 'pigeon' }
      ];

      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockSpecies
      });

      const result = await birdsApi.getSpeciesList();

      expect(result.data).toEqual(mockSpecies);
    });
  });

  describe('scoringApi', () => {
    it('should get default criteria', async () => {
      const { scoringApi } = await import('../src/api/api.ts');

      const mockCriteria = {
        focus_weight: 0.4,
        clarity_weight: 0.35,
        composition_weight: 0.25
      };

      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockCriteria
      });

      const result = await scoringApi.get_default_criteria();

      expect(result.data).toEqual(mockCriteria);
    });

    it('should call batch score with LLM config', async () => {
      // 先设置 LLM 配置
      mockLocalStorage.setItem('llm_api_config', JSON.stringify({
        baseUrl: 'https://api.example.com',
        apiKey: 'test-key',
        model: 'test-model',
        timeout: 60
      }));

      // 重新加载模块以读取新的 localStorage
      vi.resetModules();
      const { scoringApi } = await import('../src/api/api.ts');

      const mockResponse = {
        ok: true,
        json: async () => ({ results: [] })
      };

      global.fetch.mockResolvedValue(mockResponse);

      const result = await scoringApi.batch_score(['/test/photo.jpg']);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/scoring/batch-score'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
      );
    });
  });

  describe('summaryApi', () => {
    it('should get sessions list', async () => {
      const { summaryApi } = await import('../src/api/api.ts');

      const mockSessions = [
        { id: 1, folder_path: '/test', total_photos: 10 }
      ];

      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockSessions
      });

      const result = await summaryApi.get_sessions(10, 0);

      expect(result.data).toEqual(mockSessions);
    });

    it('should get calendar data', async () => {
      const { summaryApi } = await import('../src/api/api.ts');

      const mockCalendar = {
        year: 2024,
        month: 3,
        days: []
      };

      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockCalendar
      });

      const result = await summaryApi.get_calendar(2024, 3);

      expect(result.data).toEqual(mockCalendar);
    });
  });

  describe('checkBackend', () => {
    it('should check backend connection', async () => {
      // 这个函数依赖 electronAPI，在 web 环境下会 fallback
      // 这里主要测试函数存在性
      const { checkBackend } = await import('../src/api/api.ts');
      expect(typeof checkBackend).toBe('function');
    });
  });
});
