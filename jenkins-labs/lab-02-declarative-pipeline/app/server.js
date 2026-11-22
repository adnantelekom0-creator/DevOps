const http = require('http');
const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'UP', timestamp: new Date() }));
  } else {
    res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Jenkins Declarative Pipeline Demo Uygulaması Çalışıyor!\n');
  }
});

if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`Sunucu ${PORT} portunda aktif.`);
  });
}

module.exports = server;
