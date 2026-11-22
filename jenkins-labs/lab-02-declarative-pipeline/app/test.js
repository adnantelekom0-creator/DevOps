const assert = require('assert');
const server = require('./server');

console.log('--- Birim Test Başlatılıyor ---');
assert.ok(server !== undefined, 'Sunucu objesi tanımlı olmalıdır');
console.log('Test Başarılı: Sunucu objesi geçerli.');
console.log('--- Tüm Testler Geçti ---');
