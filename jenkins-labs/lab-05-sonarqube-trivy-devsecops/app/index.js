const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Ornek guvenlik ve kod kokusu senaryosu:
// Statik analiz (SAST) tarafindan incelenecek endpoint'ler
app.get('/', (req, res) => {
    res.json({ message: 'DevSecOps Demo Service', status: 'active' });
});

app.get('/health', (req, res) => {
    res.status(200).json({ status: 'healthy', uptime: process.uptime() });
});

// Ornek zayiflik simülasyonu (Hardcoded credential uyarisi testi)
// SonarQube bunu security hotspot / code smell olarak tespit eder
const API_TOKEN_EXAMPLE = "SAMPLE_TOKEN_NOT_FOR_PRODUCTION_USAGE_12345";

app.get('/api/data', (req, res) => {
    res.json({ data: "Secured payload", token_type: "Bearer" });
});

if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`DevSecOps app listening on port ${PORT}`);
    });
}

module.exports = app;
