# Yönetici Parolası Unutulduğunda

Bu Jenkins (LAB-JEN-01 B) kullanıcısını JCasC ile oluşturur: `jenkins.yaml`'daki `securityRealm` her açılışta yeniden uygulanır ve parolayı `JENKINS_ADMIN_PASSWORD` ortam değişkeninden alır. Bu yüzden parola, değişkeni değiştirip container'ı yeniden oluşturarak sıfırlanır. Job'lar ve build'ler `jenkins_home` volume'ünde olduğu için kaybolmaz.

```bash
cd ~/jenkins-labs/lab-01-jenkins-docker-setup/b-kod
```

`.env` yoksa örnekten oluşturun:

```bash
test -f .env || cp .env.example .env
```

Yeni parolayı yazın (`YeniParola2026!` yerine kendi parolanız):

```bash
sed -i "s|^JENKINS_ADMIN_PASSWORD=.*|JENKINS_ADMIN_PASSWORD=YeniParola2026!|" .env
```

`up -d` değişen ortam değişkeni nedeniyle container'ı yeniden oluşturur:

```bash
docker compose up -d
```

Jenkins açılınca (yaklaşık bir dakika) yeni parola geçerli, eski parola geçersizdir:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -u 'admin:YeniParola2026!' http://127.0.0.1:18080/api/json
```

`200` döner; eski parolayla `401`.

`config.xml`'de `<useSecurity>false</useSecurity>` yapmak bu Jenkins'te işe yaramaz: JCasC açılışta güvenlik ayarlarını yeniden uygular.
