function multiply(a, b) {
    return a * b;
}

console.log("[TEST RUNNER] Node.js birim testleri koşturuluyor...");

if (multiply(3, 4) !== 12) {
    console.error("HATA: multiply(3, 4) sonucu 12 olmalı!");
    process.exit(1);
}

if (multiply(-2, 5) !== -10) {
    console.error("HATA: multiply(-2, 5) sonucu -10 olmalı!");
    process.exit(1);
}

console.log("[TEST PASSED] 2 birim test başarıyla geçti.");
process.exit(0);
