const http = require('http');

const PORT = process.env.PORT || 3000;
const VERSION = process.env.APP_VERSION || '1.0.0';

const server = http.createServer((req, res) => {
    if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'UP', version: VERSION, timestamp: new Date().toISOString() }));
    } else if (req.url === '/info') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            app: 'docker-jenkins-demo',
            version: VERSION,
            environment: process.env.NODE_ENV || 'production',
            uptime: process.uptime()
        }));
    } else {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end(`DevOps Atolyesi - Dockerized App running on Jenkins CI/CD (v${VERSION})\n`);
    }
});

server.listen(PORT, () => {
    console.log(`Server listening on port ${PORT}, version ${VERSION}`);
});
