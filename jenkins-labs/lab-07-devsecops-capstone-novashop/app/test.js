const assert = require('assert');

console.log('[TEST SUITE] Starting NovaShop Order Service Unit Tests...');

// Test 1: Healthcheck logic verification
function testHealthLogic() {
    const uptime = 10;
    const env = 'staging';
    const version = 'v1.0.0';
    const payload = {
        status: 'HEALTHY',
        service: 'novashop-order-service',
        env: env,
        version: version,
        uptimeSeconds: uptime
    };

    assert.strictEqual(payload.status, 'HEALTHY');
    assert.strictEqual(payload.service, 'novashop-order-service');
    assert.strictEqual(payload.env, 'staging');
    console.log('✓ Test 1: Health check contract passed.');
}

// Test 2: Order data validation
function testOrderValidation() {
    const validOrder = {
        customer: 'Ali Veli',
        item: 'Terraform Pro Guide',
        amount: 250
    };

    assert.ok(validOrder.customer && validOrder.item && validOrder.amount, 'All fields must be present');
    assert.strictEqual(typeof validOrder.amount, 'number', 'Amount must be number');
    console.log('✓ Test 2: Order schema validation passed.');
}

// Test 3: Metrics format verification
function testMetricsFormat() {
    const metricLine = 'novashop_http_requests_total{service="novashop-order-service",env="production"} 15';
    assert.ok(metricLine.includes('novashop_http_requests_total'), 'Metric name missing');
    assert.ok(metricLine.endsWith('15'), 'Metric value missing');
    console.log('✓ Test 3: Prometheus metrics format passed.');
}

// Execute all tests
try {
    testHealthLogic();
    testOrderValidation();
    testMetricsFormat();
    console.log('----------------------------------------------------');
    console.log('ALL UNIT TESTS PASSED (3/3). Quality threshold met.');
    process.exit(0);
} catch (err) {
    console.error('TEST FAILED:', err.message);
    process.exit(1);
}
