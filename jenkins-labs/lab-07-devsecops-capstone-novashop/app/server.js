const http = require('http');

const PORT = process.env.PORT || 8080;
const APP_ENV = process.env.APP_ENV || 'development';
const APP_VERSION = process.env.APP_VERSION || '1.0.0';

let orders = [
    { id: 'ORD-1001', customer: 'Ahmet Yilmaz', item: 'DevOps Training Pack', amount: 1500, status: 'COMPLETED' },
    { id: 'ORD-1002', customer: 'Zeynep Kaya', item: 'Cloud Architecture Handbook', amount: 350, status: 'SHIPPED' },
    { id: 'ORD-1003', customer: 'Mehmet Demir', item: 'Kubernetes in Action', amount: 500, status: 'PROCESSING' }
];

let requestCount = 0;

const server = http.createServer((req, res) => {
    requestCount++;
    const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    const pathname = parsedUrl.pathname;

    if (pathname === '/health' || pathname === '/healthz') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            status: 'HEALTHY',
            service: 'novashop-order-service',
            env: APP_ENV,
            version: APP_VERSION,
            uptimeSeconds: Math.floor(process.uptime()),
            timestamp: new Date().toISOString()
        }));
    } else if (pathname === '/metrics') {
        res.writeHead(200, { 'Content-Type': 'text/plain; version=0.0.4' });
        res.end([
            '# HELP novashop_http_requests_total Total number of HTTP requests processed.',
            '# TYPE novashop_http_requests_total counter',
            `novashop_http_requests_total{service="novashop-order-service",env="${APP_ENV}"} ${requestCount}`,
            '# HELP novashop_orders_count Total number of active orders.',
            '# TYPE novashop_orders_count gauge',
            `novashop_orders_count{env="${APP_ENV}"} ${orders.length}`,
            '# HELP novashop_service_up Health status indicator.',
            '# TYPE novashop_service_up gauge',
            'novashop_service_up 1',
            ''
        ].join('\n'));
    } else if (pathname === '/api/v1/orders' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            success: true,
            count: orders.length,
            environment: APP_ENV,
            version: APP_VERSION,
            orders: orders
        }));
    } else if (pathname === '/api/v1/orders' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk; });
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                if (!data.customer || !data.item || !data.amount) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    return res.end(JSON.stringify({ error: 'Missing required fields: customer, item, amount' }));
                }
                const newOrder = {
                    id: `ORD-${1000 + orders.length + 1}`,
                    customer: data.customer,
                    item: data.item,
                    amount: Number(data.amount),
                    status: 'PENDING',
                    created_at: new Date().toISOString()
                };
                orders.push(newOrder);
                res.writeHead(201, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, order: newOrder }));
            } catch (err) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Invalid JSON payload' }));
            }
        });
    } else if (pathname === '/api/v1/info') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            service: 'novashop-order-service',
            maintained_by: 'DevOps Architecture Team',
            environment: APP_ENV,
            version: APP_VERSION
        }));
    } else {
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end(`
            <!DOCTYPE html>
            <html lang="tr">
            <head>
                <meta charset="utf-8">
                <title>NovaShop - Siparis Servisi</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }
                    .card { max-width: 700px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 32px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); border: 1px solid #334155; }
                    .badge { display: inline-block; padding: 4px 12px; border-radius: 9999px; font-size: 14px; font-weight: 600; }
                    .badge-env { background-color: #3b82f6; color: white; }
                    .badge-ver { background-color: #10b981; color: white; }
                    .status-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #10b981; margin-right: 6px; }
                    ul { text-align: left; background: #0f172a; padding: 16px 24px; border-radius: 8px; font-family: monospace; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h2><span class="status-dot"></span>NovaShop Siparis Servisi</h2>
                    <p>
                        Ortam: <span class="badge badge-env">${APP_ENV}</span> | 
                        Surum: <span class="badge badge-ver">${APP_VERSION}</span>
                    </p>
                    <p>Jenkins DevSecOps Pipeline ile sifir kesintiyle basariyla yayinlandi.</p>
                    <ul>
                        <li>GET /health : Servis saglik denetimi</li>
                        <li>GET /metrics : Prometheus metrikleri</li>
                        <li>GET /api/v1/orders : Siparis listesi</li>
                        <li>POST /api/v1/orders : Yeni siparis olusturma</li>
                    </ul>
                </div>
            </body>
            </html>
        `);
    }
});

server.listen(PORT, () => {
    console.log(`[NovaShop Order Service] Listening on port ${PORT} [env=${APP_ENV}, version=${APP_VERSION}]`);
});
