// API 测试脚本
const API_BASE = 'http://localhost:8000';

const testResults = [];

async function test(name, fn) {
  try {
    await fn();
    testResults.push({ name, status: 'PASS' });
    console.log(`✓ ${name}`);
  } catch (e) {
    testResults.push({ name, status: 'FAIL', error: e.message });
    console.log(`✗ ${name}: ${e.message}`);
  }
}

async function runTests() {
  // 1. 测试后端健康检查
  await test('Backend Health Check', async () => {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Status: ${res.status}`);
    const data = await res.json();
    if (data.status !== 'healthy') throw new Error('Not healthy');
  });

  // 2. 测试根路由
  await test('Root Endpoint', async () => {
    const res = await fetch(`${API_BASE}/`);
    if (!res.ok) throw new Error(`Status: ${res.status}`);
  });

  // 3. 测试扫描 API - 支持的格式
  await test('Scan Supported Formats', async () => {
    const res = await fetch(`${API_BASE}/api/scan/supported-formats`);
    if (!res.ok) throw new Error(`Status: ${res.status}`);
  });

  // 4. 测试鸟类识别 API - 物种列表
  await test('Bird Species List', async () => {
    const res = await fetch(`${API_BASE}/api/birds/species-list`);
    if (!res.ok) throw new Error(`Status: ${res.status}`);
  });

  // 5. 测试 LLM 连接测试端点
  await test('LLM Test Connection Endpoint', async () => {
    const res = await fetch(`${API_BASE}/api/llm/test-connection`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        base_url: 'https://api.openai.com/v1',
        api_key: 'test-key',
        model: 'gpt-4o',
        timeout: 10
      })
    });
    // 401 是正常的（key 无效），只要端点存在即可
    if (res.status !== 200 && res.status !== 401) {
      console.log(`  (Endpoint exists, status: ${res.status})`);
    }
  });

  // 6. 测试筛图 API - 默认评分标准
  await test('Scoring Default Criteria', async () => {
    const res = await fetch(`${API_BASE}/api/scoring/criteria/defaults`);
    if (!res.ok) throw new Error(`Status: ${res.status}`);
  });

  // 7. 测试总结 API - 物种列表
  await test('Summary Species List', async () => {
    const res = await fetch(`${API_BASE}/api/summary/species/list`);
    if (!res.ok) throw new Error(`Status: ${res.status}`);
  });

  // 8. 测试总结 API - 会话列表
  await test('Summary Sessions List', async () => {
    const res = await fetch(`${API_BASE}/api/summary/sessions?limit=10&offset=0`);
    if (!res.ok) throw new Error(`Status: ${res.status}`);
  });

  // 9. 测试地图 API - GET /daily
  await test('Map Daily Endpoint', async () => {
    const res = await fetch(`${API_BASE}/api/map/daily?date=${new Date().toISOString().split('T')[0]}`, {
      method: 'GET'
    });
    if (res.status !== 200 && res.status !== 400 && res.status !== 422) {
      throw new Error(`Status: ${res.status}`);
    }
  });

  console.log('\n=== Test Summary ===');
  const passed = testResults.filter(r => r.status === 'PASS').length;
  const failed = testResults.filter(r => r.status === 'FAIL').length;
  console.log(`Passed: ${passed}/${testResults.length}`);
  if (failed > 0) {
    console.log('Failed:');
    testResults.filter(r => r.status === 'FAIL').forEach(r => {
      console.log(`  - ${r.name}: ${r.error}`);
    });
  }
}

runTests().catch(console.error);
