"""Lab README'leri için işaretli Jenkins ekran görüntüleri.

Kullanım (yerelde):
    JK_BASE=https://student103-jenkins.devopsatolyesi.com JK_SSH=student@<sunucu> \
        python3 scripts/screenshots/jenkins_shots.py lab01-wizard lab01-ui

Tıklanacak yerler kırmızı kutu + ok + README'deki adım numarasıyla işaretlenir.
Kutu, Playwright'ın bulduğu öğenin ölçülen yerine çizilir.
Çıktı: <lab-dizini>/images/<ad>.png (genişlik 1600 px).
"""
import math
import os
import secrets
import subprocess
import sys
import time

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

BASE = os.environ.get("JK_BASE", "http://127.0.0.1:18080").rstrip("/")
SSH = os.environ.get("JK_SSH", "")
USER = os.environ.get("JK_USER", "admin")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCALE = 1.5
OUT_W = 1600
RED = (220, 38, 38)
LAB_DIRS = {"lab01": "lab-01-jenkins-docker-setup", "lab02": "lab-02-declarative-pipeline", "lab02a": "lab-02a-python-dockerhub-kind", "lab03": "lab-03-parameters-approval-resilience", "lab04": "lab-04-credentials-docker-harbor-push", "lab06": "lab-06-kubernetes-kind-rolling-update", "lab05": "lab-05-sonarqube-trivy-devsecops", "lab07": "lab-07-devsecops-capstone-novashop", "b01": "bonus-labs/01-groovy-script-loops-conditions", "b02": "bonus-labs/02-build-managers-npm-python", "b03": "bonus-labs/03-parallel-execution-replay", "b04": "bonus-labs/04-multibranch-pipeline-gitflow", "b05": "bonus-labs/05-gitlab-webhook-event-driven", "b07": "bonus-labs/07-shared-libraries-jcasc-ops", "b06": "bonus-labs/06-argocd-gitops-sync"}


def remote(cmd):
    return subprocess.run(["ssh", SSH, cmd], capture_output=True, text=True, check=True).stdout.strip()


def admin_password():
    """Sunucuda ~/jenkins-admin-sifre.txt (600) içinde tutulur; yoksa üretilir. Ekrana yazılmaz."""
    pw = remote("cat ~/jenkins-admin-sifre.txt 2>/dev/null || true")
    if not pw:
        pw = secrets.token_urlsafe(12)
        subprocess.run(["ssh", SSH, "umask 077; cat > ~/jenkins-admin-sifre.txt"], input=pw, text=True, check=True)
    return pw


def settle(page, extra=1.5):
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass
    time.sleep(extra)


def box_of(scope, target, page=None):
    if target[0] == "page":             # frame kapsamındayken sayfadaki bir öğe
        return box_of(page, target[1])
    if target[0] == "union":
        bs = [box_of(scope, t) for t in target[1:]]
        x0 = min(b["x"] for b in bs); y0 = min(b["y"] for b in bs)
        x1 = max(b["x"] + b["width"] for b in bs); y1 = max(b["y"] + b["height"] for b in bs)
        return {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}
    b = loc(scope, target).bounding_box(timeout=10000)
    if not b:
        raise RuntimeError(f"öğe bulunamadı: {target}")
    return b


def loc(scope, target):
    kind = target[0]
    if kind == "xpath_parent":   # gizli input'un görünen üst öğesi (React select)
        return scope.locator(target[1]).locator("xpath=ancestor::*[contains(@class,'select') or @role='combobox' or contains(@class,'css-')][1]").first
    if kind == "text":
        return scope.get_by_text(target[1], exact=target[2] if len(target) > 2 else False).first
    if kind == "role":
        return scope.get_by_role(target[1], name=target[2], exact=target[3] if len(target) > 3 else False).first
    return scope.locator(target[1]).first


def draw(path, marks):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 34)
    except OSError:
        font = ImageFont.load_default()
    pad = 6 * SCALE
    for b, no, arrow in marks:
        x0, y0 = b["x"] * SCALE - pad, b["y"] * SCALE - pad
        x1, y1 = (b["x"] + b["width"]) * SCALE + pad, (b["y"] + b["height"]) * SCALE + pad
        d.rounded_rectangle((x0, y0, x1, y1), radius=8, outline=RED, width=5)
        cy, cx = (y0 + y1) / 2, (x0 + x1) / 2
        L = 110
        tip = tail = None
        if arrow == "left":
            tip, tail = (x0 - 4, cy), (x0 - L, cy)
        elif arrow == "right":
            tip, tail = (x1 + 4, cy), (x1 + L, cy)
        elif arrow == "up":
            tip, tail = (cx, y0 - 4), (cx, y0 - L)
        elif arrow == "down":
            tip, tail = (cx, y1 + 4), (cx, y1 + L)
        if tip:
            d.line((tail, tip), fill=RED, width=7)
            ang = math.atan2(tip[1] - tail[1], tip[0] - tail[0])
            h = 26
            p1 = (tip[0] - h * math.cos(ang - 0.45), tip[1] - h * math.sin(ang - 0.45))
            p2 = (tip[0] - h * math.cos(ang + 0.45), tip[1] - h * math.sin(ang + 0.45))
            d.polygon([tip, p1, p2], fill=RED)
            nx, ny = tail
        else:
            nx, ny = x0, y0
        if no is None:
            continue
        r = 24
        d.ellipse((nx - r - 3, ny - r - 3, nx + r + 3, ny + r + 3), fill=(255, 255, 255))
        d.ellipse((nx - r, ny - r, nx + r, ny + r), fill=RED)
        t = str(no)
        tw, th = d.textbbox((0, 0), t, font=font)[2:]
        d.text((nx - tw / 2, ny - th / 2 - 3), t, fill=(255, 255, 255), font=font)
    if im.width > OUT_W:
        im = im.resize((OUT_W, int(im.height * OUT_W / im.width)), Image.LANCZOS)
    im.save(path, optimize=True)


def shoot(page, lab, name, marks_spec, scope=None, offset=None, full=False):
    """scope: öğelerin arandığı frame (varsayılan sayfa); offset: frame'in sayfadaki konumu."""
    scope = scope or page
    out_dir = os.path.join(ROOT, LAB_DIRS[lab], "images")
    os.makedirs(out_dir, exist_ok=True)
    if marks_spec and marks_spec[0][0][0] != "union":
        try:
            loc(scope, marks_spec[0][0]).scroll_into_view_if_needed(timeout=5000)
            time.sleep(0.6)
        except Exception:
            pass
    marks = []
    for target, no, arrow in marks_spec:
        b = dict(box_of(scope, target, page))
        if offset:
            b["x"] += offset["x"]; b["y"] += offset["y"]
        marks.append((b, no, arrow))
    path = os.path.join(out_dir, name + ".png")
    page.screenshot(path=path, full_page=full)
    draw(path, marks)
    print("ok", os.path.relpath(path, ROOT))


def login(page, pw):
    page.goto(BASE + "/login", wait_until="domcontentloaded"); settle(page)
    if page.locator("#j_username").count():
        page.fill("#j_username", USER)
        page.fill("#j_password", pw)
        page.locator('button[name="Submit"], input[name="Submit"]').first.click()
        settle(page)


def set_pipeline_script(page, script):
    page.evaluate(
        """(s) => {
            const ed = document.querySelector('.ace_editor');
            if (ed && ed.env && ed.env.editor) { ed.env.editor.setValue(s, 1); return; }
            const ta = document.querySelector('textarea[name="_.script"]');
            ta.value = s; ta.dispatchEvent(new Event('change'));
        }""",
        script,
    )


# ------------------------------------------------------------------ lab-01
A_PIPELINE = """pipeline {
    agent any
    stages {
        stage('Merhaba') {
            steps {
                echo 'Jenkins arayüzünden ilk pipeline'
                sh 'hostname && whoami'
            }
        }
    }
}
"""


def lab01a_wizard(page):
    """A: düz image, Install suggested plugins."""
    lab = "lab01"
    initial = remote("docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword")
    pw = admin_password()
    page.goto(BASE + "/", wait_until="domcontentloaded"); settle(page, 3)
    page.fill("#security-token", initial)
    shoot(page, lab, "a01-unlock", [
        (("css", "#security-token"), 1, "left"),
        (("css", "input.set-security-key"), 2, "up"),
    ])
    page.locator("input.set-security-key").first.click(); settle(page, 4)
    shoot(page, lab, "a02-suggested", [
        (("css", "a.install-recommended"), 3, "down"),
    ])
    page.locator("a.install-recommended").first.click(); time.sleep(12)
    shoot(page, lab, "a03-installing", [])
    frame_el = page.locator("iframe").first
    frame_el.wait_for(timeout=900000)
    fr = frame_el.element_handle().content_frame()
    fr.locator('input[name="username"]').wait_for(timeout=120000)
    fr.fill('input[name="username"]', USER)
    fr.fill('input[name="password1"]', pw)
    fr.fill('input[name="password2"]', pw)
    fr.fill('input[name="fullname"]', "Jenkins Admin")
    fr.fill('input[name="email"]', "admin@example.com")
    shoot(page, lab, "a04-first-admin", [
        (("union", ("css", 'input[name="username"]'), ("css", 'input[name="email"]')), 4, "left"),
        (("page", ("css", "button.save-first-user")), 5, "up"),
    ], scope=fr)
    page.locator("button.save-first-user").first.click(); settle(page, 4)
    frame_el = page.locator("iframe").first
    frame_el.wait_for(timeout=60000)
    fr = frame_el.element_handle().content_frame()
    fr.locator('input[name="rootUrl"]').wait_for(timeout=60000)
    shoot(page, lab, "a05-instance-url", [
        (("css", 'input[name="rootUrl"]'), 6, "down"),
        (("page", ("css", "button.save-configure-instance")), 7, "up"),
    ], scope=fr)
    page.locator("button.save-configure-instance").first.click(); settle(page, 3)
    shoot(page, lab, "a06-ready", [
        (("css", "button.install-done"), 8, "down"),
    ])
    page.locator("button.install-done").first.click(); settle(page, 4)


def dismiss_monitors(page):
    for _ in range(5):
        btn = page.locator("button.app-adminmonitor-dismiss-button:visible")
        if not btn.count():
            break
        try:
            btn.first.click(timeout=3000); time.sleep(1.5)
        except Exception:
            break


def lab01a_tour(page):
    lab = "lab01"
    login(page, admin_password())
    page.goto(BASE + "/", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "a07-dashboard", [
        (("css", 'a.task-link[href$="/newJob"]'), 1, "right"),
        (("css", 'a.task-link[href$="/builds"]'), 2, "right"),
        (("css", 'a[href="/computer/"]'), 3, "right"),
        (("css", 'a.jenkins-button[href="/manage"]'), 4, "down"),
        (("css", 'a.jenkins-button[href^="/user/"]'), 5, "down"),
    ])
    page.goto(BASE + "/manage", wait_until="domcontentloaded"); settle(page, 2)
    dismiss_monitors(page)
    page.goto(BASE + "/manage", wait_until="domcontentloaded"); settle(page, 2)
    page.set_viewport_size({"width": 1400, "height": 1100})
    shoot(page, lab, "a08-manage", [
        (("css", 'a[href="configure"]'), 1, None),
        (("css", 'a[href="configureTools"]'), 2, None),
        (("css", 'a[href="pluginManager"]'), 3, None),
        (("css", 'a[href="computer"]'), 4, None),
        (("css", 'a[href="configureSecurity"]'), 5, None),
        (("css", 'a[href="credentials"]'), 6, None),
        (("css", 'a[href="securityRealm/"]'), 7, None),
    ])
    page.set_viewport_size({"width": 1400, "height": 860})


def lab01a_plugin_install(page):
    lab = "lab01"
    login(page, admin_password())
    page.goto(BASE + "/manage/pluginManager/available", wait_until="domcontentloaded"); settle(page, 2)
    page.locator("input.jenkins-search__input:visible").fill("Rebuilder")
    row = page.locator('tr[data-plugin-id="rebuild"]')
    row.wait_for(timeout=30000); time.sleep(1)
    row.locator('input[type="checkbox"]').check(force=True); time.sleep(0.5)
    shoot(page, lab, "a09-plugin-available", [
        (("css", 'a.task-link[href$="/available"]'), 1, None),
        (("css", "input.jenkins-search__input:visible"), 2, "down"),
        (("css", 'tr[data-plugin-id="rebuild"] .jenkins-checkbox'), 3, "down"),
        (("role", "button", "Install", True), 4, "down"),
    ])
    page.get_by_role("button", name="Install", exact=True).first.click(); settle(page, 3)
    for _ in range(60):
        if page.get_by_text("Success").count() >= 2:
            break
        time.sleep(2)
    shoot(page, lab, "a10-plugin-success", [
        (("css", 'a.task-link[href$="/updates/"]'), None, None),
        (("text", "Rebuilder", True), None, None),
    ])


def lab01a_plugin_uninstall(page):
    lab = "lab01"
    login(page, admin_password())
    page.goto(BASE + "/manage/pluginManager/installed", wait_until="domcontentloaded"); settle(page, 2)
    page.locator("input.jenkins-search__input:visible").fill("Rebuilder"); time.sleep(2)
    btn = 'tr[data-plugin-id="rebuild"] button[data-action="uninstall"]'
    shoot(page, lab, "a11-plugin-uninstall", [
        (("css", 'a.task-link[href$="/installed"]'), 1, None),
        (("css", "input.jenkins-search__input:visible"), 2, "down"),
        (("css", btn), 3, "down"),
    ])
    page.locator(btn).click(); time.sleep(1.5)
    shoot(page, lab, "a12-uninstall-confirm", [
        (("css", "dialog button.jenkins-button--primary, .jenkins-dialog button.jenkins-button--primary"), 4, "down"),
    ])
    page.locator("dialog button.jenkins-button--primary, .jenkins-dialog button.jenkins-button--primary").first.click()
    settle(page, 3)
    lab01a_restart(page)


def lab01a_restart(page):
    """Kaldırma, Jenkins yeniden başlayınca tamamlanır: <adres>/safeRestart -> Yes."""
    lab = "lab01"
    login(page, admin_password())
    page.goto(BASE + "/safeRestart", wait_until="domcontentloaded"); settle(page, 2)
    yes = "form button.jenkins-button--primary, form button[name='Submit']"
    shoot(page, lab, "a13-safe-restart", [
        (("css", yes), 5, "down"),
    ])
    page.locator(yes).first.click(); time.sleep(8)
    for _ in range(60):
        try:
            page.goto(BASE + "/login", wait_until="domcontentloaded", timeout=10000)
            if page.locator("#j_username").count():
                break
        except Exception:
            pass
        time.sleep(3)


def api_password():
    """A bölümünde sihirbazda verilen parola, B'de .env/varsayılan parola."""
    if os.environ.get("JK_PART", "b") == "a":
        return admin_password()
    return env_password()


def api(script):
    """Sunucuda Jenkins REST çağrısı; parola stdin ile gider, komut satırında görünmez."""
    pw = api_password().replace("'", "'\\''")
    full = f"P='{pw}'; J=http://127.0.0.1:18080\n" + script
    return subprocess.run(["ssh", SSH, "bash -s"], input=full, text=True, capture_output=True, check=True).stdout


def delete_job(name):
    """Betik tekrar çalıştırılabilsin diye önceki denemenin job'u silinir."""
    api('CK=$(mktemp); '
        'c=$(curl -s -c $CK -u "admin:$P" "$J/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\\":\\",//crumb)"); '
        f'curl -s -o /dev/null -b $CK -u "admin:$P" -H "$c" -X POST $J/job/{name}/doDelete; rm -f $CK\n')


def wait_build(name, no):
    for _ in range(150):
        st = api(f'curl -s -u "admin:$P" "$J/job/{name}/{no}/api/json?tree=result" || true\n')
        if any(x in st for x in ('"SUCCESS"', '"FAILURE"', '"UNSTABLE"', '"ABORTED"')):
            return
        time.sleep(2)


def lab01a_pipeline(page):
    lab = "lab01"
    job = "ilk-pipeline"
    delete_job(job)
    login(page, admin_password())
    page.goto(BASE + "/view/all/newJob", wait_until="domcontentloaded"); settle(page)
    page.fill("#name", job)
    page.locator("div.org_jenkinsci_plugins_workflow_job_WorkflowJob").first.click(); time.sleep(0.5)
    shoot(page, lab, "a14-new-item", [
        (("css", "#name"), 1, "left"),
        (("css", "div.org_jenkinsci_plugins_workflow_job_WorkflowJob"), 2, "left"),
        (("css", "#ok-button"), 3, "up"),
    ])
    page.locator("#ok-button").click(); settle(page, 3)
    page.locator("div.ace_editor").first.wait_for(timeout=30000)
    set_pipeline_script(page, A_PIPELINE); time.sleep(1)
    shoot(page, lab, "a15-pipeline-script", [
        (("css", "div.ace_editor"), 4, "left"),
        (("css", 'button[name="Submit"]'), 5, "up"),
    ])
    page.locator('button[name="Submit"]').first.click(); settle(page, 2)
    shoot(page, lab, "a16-build-now", [
        (("css", 'a[href$="/build?delay=0sec"], a:has-text("Build Now")'), 6, "right"),
    ])
    page.locator('a[href$="/build?delay=0sec"], a:has-text("Build Now")').first.click()
    wait_build(job, 1)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 3)
    shoot(page, lab, "a17-job-page", [
        (("css", 'a.task-link[href$="/configure"]'), 7, "right"),
        (("css", "a.task-link[href$=\"/multi-pipeline-graph\"]"), 8, "right"),
        (("css", f'a[href$="/job/{job}/1/"]'), 9, "right"),
    ])
    page.goto(BASE + f"/job/{job}/1/console", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "a18-console", [
        (("text", "Jenkins arayüzünden ilk pipeline", True), 10, "left"),
    ])


def lab01a_rebuild_link(page):
    """Rebuilder kuruluyken build sayfasında Rebuild bağlantısı."""
    lab = "lab01"
    login(page, admin_password())
    page.goto(BASE + "/job/ilk-pipeline/1/", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "a10b-rebuild-link", [
        (("css", 'a.task-link:has-text("Rebuild")'), None, "right"),
    ])


def lab01a_console(page):
    lab = "lab01"
    login(page, admin_password())
    page.goto(BASE + "/job/ilk-pipeline/1/console", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "a18-console", [
        (("text", "Jenkins arayüzünden ilk pipeline", True), 10, "left"),
    ])


def env_password():
    """B bölümü: yönetici parolası lab-01/.env dosyasındadır."""
    pw = remote("grep '^JENKINS_ADMIN_PASSWORD=' ~/jenkins-labs/lab-01-jenkins-docker-setup/b-kod/.env 2>/dev/null | cut -d= -f2- || true")
    return pw or "DevOps2026!"   # .env yoksa compose varsayılanı


def lab01b(page):
    lab = "lab01"
    pw = env_password()
    page.goto(BASE + "/login", wait_until="domcontentloaded"); settle(page, 2)
    page.fill("#j_username", USER); page.fill("#j_password", pw)
    shoot(page, lab, "b01-login", [
        (("union", ("css", "#j_username"), ("css", "#j_password")), 1, "left"),
        (("css", 'button[name="Submit"]'), 2, "left"),
    ])
    page.locator('button[name="Submit"]').first.click(); settle(page, 3)
    shoot(page, lab, "b02-dashboard", [
        (("text", "jenkins-as-code/jenkins.yaml"), 3, "down"),
        (("css", "#projectstatus"), 4, "left"),
    ])
    page.goto(BASE + "/manage/configuration-as-code/", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "b03-casc", [
        (("text", "/var/jenkins_config/jenkins.yaml"), 5, "down"),
        (("css", 'form[action="reload"] button'), 6, "down"),
    ])


def login_b(page):
    page.goto(BASE + "/login", wait_until="domcontentloaded"); settle(page, 1)
    if page.locator("#j_username").count():
        page.fill("#j_username", USER); page.fill("#j_password", env_password())
        page.locator('button[name="Submit"]').first.click(); settle(page, 2)


def select_by_label(page, select_css, label):
    page.locator(select_css).select_option(label=label); time.sleep(1.5)


def lab02(page):
    lab = "lab02"
    job = "declarative-pipeline-demo"
    delete_job(job)
    login_b(page)
    page.goto(BASE + "/view/all/newJob", wait_until="domcontentloaded"); settle(page)
    page.fill("#name", job)
    page.locator("div.org_jenkinsci_plugins_workflow_job_WorkflowJob").first.click(); time.sleep(0.5)
    page.locator("#ok-button").click(); settle(page, 3)
    defsel = 'xpath=(//select[contains(@class,"dropdownList")][option[normalize-space(.)="Pipeline script from SCM"]])[1]'
    page.locator(defsel).select_option(label="Pipeline script from SCM"); time.sleep(2)
    scmsel = 'xpath=(//select[contains(@class,"dropdownList")][option[normalize-space(.)="Git"]])[1]'
    page.locator(scmsel).select_option(label="Git"); time.sleep(2)
    page.locator('input[name="_.url"]:visible').first.fill("https://gitlab.com/devops-practitioner-labs/jenkins-labs.git")
    page.locator('input[name="_.name"]:visible').first.fill("*/main")
    page.locator('input[name="_.scriptPath"]:visible').first.fill("lab-02-declarative-pipeline/Jenkinsfile")
    page.locator('input[name="_.url"]:visible').first.press("Tab"); time.sleep(2)
    page.locator(defsel).scroll_into_view_if_needed(); page.mouse.wheel(0, 120); time.sleep(1)
    shoot(page, lab, "01-pipeline-from-scm", [
        (("css", defsel), 1, "left"),
        (("css", scmsel), 2, "left"),
        (("css", 'input[name="_.url"]:visible'), 3, "left"),
    ])
    page.locator('input[name="_.scriptPath"]:visible').first.scroll_into_view_if_needed(); time.sleep(1)
    shoot(page, lab, "02-branch-script-path", [
        (("css", 'input[name="_.name"]:visible'), 4, "left"),
        (("css", 'input[name="_.scriptPath"]:visible'), 5, "left"),
        (("css", 'button[name="Submit"]'), 6, "up"),
    ])
    page.locator('button[name="Submit"]').first.click(); settle(page, 2)
    page.locator('a[href$="/build?delay=0sec"], a:has-text("Build Now")').first.click()
    wait_build(job, 1)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "03-stage-view-artifacts", [
        (("css", "table.jobsTable, #pipeline-box, .stage-view, div.table-box"), 7, None),
        (("text", "Last Successful Artifacts"), 8, "left"),
    ])
    # Snippet Generator
    page.goto(BASE + f"/job/{job}/pipeline-syntax/", wait_until="domcontentloaded"); settle(page, 2)
    page.locator('input[name="_.artifacts"]').first.fill("output/*.txt")
    page.locator("#generatePipelineScript").click(); time.sleep(2)
    shoot(page, lab, "04-snippet-generator", [
        (("css", "select.dropdownList"), 1, "left"),
        (("css", 'input[name="_.artifacts"]'), 2, "left"),
        (("css", "#generatePipelineScript"), 3, "left"),
        (("css", "#prototypeText"), 4, "left"),
    ])
    # Directive Generator
    page.goto(BASE + f"/job/{job}/directive-generator/", wait_until="domcontentloaded"); settle(page, 2)
    page.locator('button[id^="prototypeButton"]').first.click(); time.sleep(2)
    shoot(page, lab, "05-directive-generator", [
        (("css", "select.dropdownList"), 1, "left"),
        (("css", 'button[id^="prototypeButton"]'), 2, "left"),
        (("css", 'textarea[id^="prototypeText"]'), 3, "left"),
    ])
    # Parametreli snippet: ilk build sonrası Build with Parameters
    page.goto(BASE + "/job/snip-05/", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "06-build-with-parameters", [
        (("css", 'a.task-link[href$="/build?delay=0sec"]'), None, "right"),
    ])


def lab02a_credential(page):
    """Secret file credential formu. Görüntü için yerelde aynı adlı boş bir dosya seçilir ve form
    kaydedilmeden kapatılır; gerçek kubeconfig credential'ı sunucuda REST ile eklenir."""
    lab = "lab02a"
    dummy = os.environ["JK_DUMMY_FILE"]
    login_b(page)
    page.goto(BASE + "/manage/credentials/", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "01-add-credentials", [
        (("role", "button", "Add Credentials"), 1, "down"),
    ])
    page.get_by_role("button", name="Add Credentials").click(); time.sleep(2)
    page.get_by_text("Secret file", exact=True).click(); time.sleep(0.5)
    shoot(page, lab, "02-kind-secret-file", [
        (("text", "Secret file", True), 2, "left"),
        (("role", "button", "Next"), 3, "down"),
    ])
    page.get_by_role("button", name="Next").click(); time.sleep(2)
    page.locator('input[name="file"]').set_input_files(dummy)
    page.locator('input[name="_.id"]').fill("kubeconfig-student-kind")
    page.locator('input[name="_.description"]').fill("KinD cluster kubeconfig")
    time.sleep(1)
    shoot(page, lab, "03-secret-file-form", [
        (("css", 'input[name="file"]'), 4, "left"),
        (("css", 'input[name="_.id"]'), 5, "left"),
        (("role", "button", "Create"), 6, "down"),
    ])
    page.get_by_role("button", name="Close").first.click(); time.sleep(1)


def lab02a_build(page):
    lab = "lab02a"
    job = "python-dockerhub-kind"
    login_b(page)
    # Docker Hub credential formu (görüntü için sahte token; form kaydedilmez)
    add_userpass_credential_shot(page, lab, "07-dockerhub-credential", "hbayraktar", "dckr_pat_ornek_token", "dockerhub-creds", 1)
    nxt = int(api(f'curl -s -u "admin:$P" "$J/job/{job}/api/json?tree=nextBuildNumber" | python3 -c "import sys,json;print(json.load(sys.stdin)[\'nextBuildNumber\'])"\n').strip())
    page.goto(BASE + f"/job/{job}/build?delay=0sec", wait_until="domcontentloaded"); settle(page, 2)
    page.locator('input.jenkins-input[name="value"]').first.fill("103")
    shoot(page, lab, "04-build-with-parameters", [
        (("css", 'input.jenkins-input[name="value"]'), 7, "left"),
        (("css", '.jenkins-checkbox:has(input[name="value"])'), 8, "left"),
        (("css", "button.jenkins-button--primary"), 9, "up"),
    ])
    page.locator("button.jenkins-button--primary").first.click(); time.sleep(3)
    wait_build(job, nxt)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "05-stage-view", [
        (("text", "Stage View", True), 10, "left"),
    ])
    page.goto(os.environ.get("JK_APP_URL", "https://student103-app1.devopsatolyesi.com/"), wait_until="domcontentloaded"); settle(page, 1)
    shoot(page, lab, "06-app", [])


def lab03(page):
    """#3 production build'i onay bekliyorken çalıştırılır."""
    lab = "lab03"
    job = "parametric-pipeline-demo"
    login_b(page)
    page.goto(BASE + f"/job/{job}/3/console", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "02-input-console", [
        (("css", 'a.post-hyperlink-note-button:has-text("Dağıtımı Başlat")'), 6, "left"),
        (("css", 'a.post-hyperlink-note-button:has-text("Abort")'), 7, "right"),
    ])
    page.locator('a.post-hyperlink-note-button:has-text("Dağıtımı Başlat")').first.click(); time.sleep(3)
    wait_build(job, 3)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "03-stage-view-approved", [
        (("text", "Stage View", True), None, "left"),
    ])
    # Build with Parameters: production
    page.goto(BASE + f"/job/{job}/build?delay=0sec", wait_until="domcontentloaded"); settle(page, 2)
    sels = page.locator('select[name="value"]')
    sels.nth(0).select_option("production")
    page.locator('input.jenkins-input[name="value"]').first.fill("2.1.0")
    sels.nth(1).select_option("5")
    shoot(page, lab, "01-build-with-parameters", [
        (("css", 'select[name="value"]'), 1, "left"),
        (("css", 'input.jenkins-input[name="value"]'), 2, "left"),
        (("css", '.jenkins-checkbox:has(input[name="value"])'), 3, "left"),
        (("css", 'xpath=(//select[@name="value"])[2]'), 4, "left"),
        (("css", "button.jenkins-button--primary"), 5, "up"),
    ])
    page.locator("button.jenkins-button--primary").first.click(); time.sleep(5)
    for _ in range(60):
        if '"id"' in api(f'curl -s -u "admin:$P" "$J/job/{job}/4/wfapi/pendingInputActions" || true\n'):
            break
        time.sleep(2)
    page.goto(BASE + f"/job/{job}/4/input/", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "04-input-page-abort", [
        (("css", 'button[name="abort"]'), 8, "down"),
    ])
    page.locator('button[name="abort"]').first.click(); time.sleep(3)
    wait_build(job, 4)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "05-stage-view-aborted", [
        (("text", "Stage View", True), None, "left"),
    ])


HARBOR = os.environ.get("JK_HARBOR", "https://student103-harbor.devopsatolyesi.com")


def harbor_login(page):
    page.goto(HARBOR + "/", wait_until="domcontentloaded"); settle(page, 3)
    if page.locator("#login_username").count():
        page.fill("#login_username", "admin"); page.fill("#login_password", "Harbor12345")
        page.locator("#log_in").click(); settle(page, 4)
    for btn in page.locator("button.close:visible").all():   # üstteki bilgi bandı
        try:
            btn.click(timeout=1000)
        except Exception:
            pass
    light = page.locator('a.nav-link:has-text("LIGHT")')
    if light.count():
        light.first.click(); time.sleep(1)


def add_userpass_credential_shot(page, lab, name, user, secret, cred_id, first_no):
    page.goto(BASE + "/manage/credentials/", wait_until="domcontentloaded"); settle(page, 2)
    page.get_by_role("button", name="Add Credentials").click(); time.sleep(2)
    page.get_by_text("Username with password", exact=True).click(); time.sleep(0.5)
    page.get_by_role("button", name="Next").click(); time.sleep(2)
    page.locator('input[name="_.username"]').fill(user)
    page.locator('input[name="_.password"]').fill(secret)
    page.locator('input[name="_.id"]').fill(cred_id)
    time.sleep(1)
    shoot(page, lab, name, [
        (("css", 'input[name="_.username"]'), first_no, "left"),
        (("css", 'input[name="_.password"]'), first_no + 1, "left"),
        (("css", 'input[name="_.id"]'), first_no + 2, "left"),
        (("role", "button", "Create"), first_no + 3, "down"),
    ])
    page.get_by_role("button", name="Close").first.click(); time.sleep(1)


def lab04(page):
    lab = "lab04"
    harbor_login(page)
    page.goto(HARBOR + "/harbor/projects", wait_until="domcontentloaded"); settle(page, 3)
    page.get_by_role("button", name="NEW PROJECT").click(); time.sleep(2)
    page.fill("#create_project_name", "devops")
    page.locator('clr-checkbox-wrapper:has(#create_project_public) label').first.click(); time.sleep(0.5)
    shoot(page, lab, "01-harbor-new-project", [
        (("css", "#create_project_name"), 1, "left"),
        (("css", 'clr-checkbox-wrapper:has(#create_project_public)'), 2, "left"),
        (("css", "#new-project-ok"), 3, "up"),
    ])
    page.locator("#new-project-ok").click(); time.sleep(2)
    login_b(page)
    add_userpass_credential_shot(page, lab, "02-jenkins-credential", "admin", "Harbor12345", "harbor-creds", 4)
    page.goto(BASE + "/job/docker-harbor-pipeline/", wait_until="domcontentloaded"); settle(page, 2)
    nxt = int(api('curl -s -u "admin:$P" "$J/job/docker-harbor-pipeline/api/json?tree=nextBuildNumber" | python3 -c "import sys,json;print(json.load(sys.stdin)[\'nextBuildNumber\'])"\n').strip())
    page.locator('a[href$="/build?delay=0sec"]').first.click(); time.sleep(3)
    wait_build("docker-harbor-pipeline", nxt)
    page.goto(BASE + "/job/docker-harbor-pipeline/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "03-stage-view", [
        (("text", "Stage View", True), 8, "left"),
    ])
    harbor_login(page)
    page.goto(HARBOR + "/harbor/projects", wait_until="domcontentloaded"); settle(page, 3)
    page.get_by_role("link", name="devops", exact=True).click(); settle(page, 3)
    page.get_by_role("link", name="devops/demo-app").first.click(); settle(page, 3)
    shoot(page, lab, "04-harbor-artifacts", [
        (("css", "clr-dg-row"), 9, "down"),
    ])


def lab04_results(page):
    lab = "lab04"
    login_b(page)
    page.goto(BASE + "/job/docker-harbor-pipeline/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "03-stage-view", [
        (("text", "Stage View", True), 8, "left"),
    ])
    harbor_login(page)
    page.goto(HARBOR + "/harbor/projects", wait_until="domcontentloaded"); settle(page, 3)
    page.get_by_role("link", name="devops", exact=True).click(); settle(page, 3)
    page.get_by_role("link", name="devops/demo-app").first.click(); settle(page, 3)
    shoot(page, lab, "04-harbor-artifacts", [
        (("css", "clr-dg-row"), 9, "down"),
    ])


def lab06(page):
    lab = "lab06"
    job = "k8s-cd-deploy-pipeline"
    login_b(page)
    page.goto(BASE + f"/job/{job}/build?delay=0sec", wait_until="domcontentloaded"); settle(page, 2)
    page.locator('input.jenkins-input[name="value"]').nth(1).fill("nginx:non-existent-tag-9999")
    shoot(page, lab, "01-build-with-parameters", [
        (("css", 'xpath=(//input[contains(@class,"jenkins-input") and @name="value"])[2]'), 1, "left"),
        (("css", '.jenkins-checkbox:has(input[name="value"])'), 2, "left"),
        (("css", "button.jenkins-button--primary"), 3, "up"),
    ])
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "02-stage-view", [
        (("text", "Stage View", True), 4, "left"),
    ])
    page.goto(BASE + f"/job/{job}/2/console", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "03-console-rollback", [
        (("text", "timed out waiting for the condition"), 5, "left"),
        (("text", "rolled back"), 6, "left"),
    ])


SONAR = os.environ.get("JK_SONAR", "https://student103-sonar.devopsatolyesi.com")
SONAR_PASS = os.environ.get("JK_SONAR_PASS", "DevOps2026!Sonar")


def lab05(page):
    lab = "lab05"
    job = "devsecops-quality-pipeline"
    page.goto(SONAR + "/sessions/new", wait_until="domcontentloaded"); settle(page, 3)
    page.fill("#login-input", "admin"); page.fill("#password-input", SONAR_PASS); page.keyboard.press("Enter"); settle(page, 4)
    for t in ("Dismiss",):
        for b in page.get_by_role("button", name=t).all():
            try:
                b.click(timeout=1000)
            except Exception:
                pass
    page.goto(SONAR + "/account/security", wait_until="domcontentloaded"); settle(page, 3)
    page.fill("#token-name", "jenkins-scanner-token")
    shoot(page, lab, "01-sonar-token", [
        (("css", "#token-name"), 1, "left"),
        (("css", "#token-select-type"), 2, "down"),
        (("css", "#token-select-expiration"), 3, "down"),
        (("role", "button", "Generate", True), 4, "down"),
    ])
    page.goto(SONAR + "/admin/settings?category=security", wait_until="domcontentloaded"); settle(page, 3)
    shoot(page, lab, "02-sonar-validate-webhooks", [
        (("css", '[id="input-settings[sonar.validateWebhooks]"]'), 5, "left"),
    ])
    page.goto(SONAR + "/admin/webhooks", wait_until="domcontentloaded"); settle(page, 3)
    page.get_by_role("button", name="Create").first.click(); time.sleep(2)
    page.fill("#webhook-name", "Jenkins-Webhook")
    page.fill("#webhook-url", "http://jenkins:8080/sonarqube-webhook/")
    shoot(page, lab, "03-sonar-webhook", [
        (("css", "#webhook-name"), 6, "left"),
        (("css", "#webhook-url"), 7, "left"),
        (("css", '[role=dialog] button:has-text("Create")'), 8, "down"),
    ])
    page.locator('[role=dialog] button:has-text("Cancel")').first.click(); time.sleep(1)
    page.goto(SONAR + "/dashboard?id=devops-jenkins-app", wait_until="domcontentloaded"); settle(page, 5)
    shoot(page, lab, "08-sonar-dashboard", [
        (("text", "Passed", True), None, "right"),
    ])
    # Jenkins
    login_b(page)
    page.goto(BASE + "/manage/credentials/", wait_until="domcontentloaded"); settle(page, 2)
    page.get_by_role("button", name="Add Credentials").click(); time.sleep(2)
    page.get_by_text("Secret text", exact=True).click(); time.sleep(0.5)
    page.get_by_role("button", name="Next").click(); time.sleep(2)
    page.locator('input[name="_.secret"], textarea[name="_.secret"]').first.fill("squ_ornek_token")
    page.locator('input[name="_.id"]').fill("sonar-token")
    time.sleep(1)
    shoot(page, lab, "04-jenkins-secret-text", [
        (("css", 'input[name="_.secret"], textarea[name="_.secret"]'), 1, "left"),
        (("css", 'input[name="_.id"]'), 2, "left"),
        (("role", "button", "Create"), 3, "down"),
    ])
    page.get_by_role("button", name="Close").first.click(); time.sleep(1)
    page.goto(BASE + "/manage/configure", wait_until="domcontentloaded"); settle(page, 3)
    page.locator('input[name="sonar.name"]').scroll_into_view_if_needed(); page.mouse.wheel(0, 150); time.sleep(1)
    shoot(page, lab, "05-jenkins-sonar-server", [
        (("css", 'input[name="sonar.name"]'), 4, "left"),
        (("css", 'input[name="sonar.serverUrl"]'), 5, "left"),
        (("css", 'xpath=(//input[@name="sonar.serverUrl"]/following::select[@name="_.credentialsId"])[1]'), 6, "left"),
    ])
    page.goto(BASE + f"/job/{job}/build?delay=0sec", wait_until="domcontentloaded"); settle(page, 2)
    cbs = page.locator('.jenkins-checkbox:has(input[name="value"])')
    shoot(page, lab, "06-build-with-parameters", [
        (("css", 'xpath=(//*[contains(@class,"jenkins-checkbox")][.//input[@name="value"]])[1]'), 1, "left"),
        (("css", 'select[name="value"]'), 2, "left"),
        (("css", 'xpath=(//*[contains(@class,"jenkins-checkbox")][.//input[@name="value"]])[2]'), 3, "left"),
        (("css", "button.jenkins-button--primary"), 4, "up"),
    ])
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "07-stage-view", [
        (("text", "Stage View", True), 5, "left"),
    ])


def lab05_jenkins_tail(page):
    lab = "lab05"
    job = "devsecops-quality-pipeline"
    login_b(page)
    page.goto(BASE + f"/job/{job}/build?delay=0sec", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "06-build-with-parameters", [
        (("css", 'xpath=(//*[contains(@class,"jenkins-checkbox")][.//input[@name="value"]])[1]'), 1, "left"),
        (("css", 'select[name="value"]'), 2, "left"),
        (("css", 'xpath=(//*[contains(@class,"jenkins-checkbox")][.//input[@name="value"]])[2]'), 3, "left"),
        (("css", "button.jenkins-button--primary"), 4, "up"),
    ])
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "07-stage-view", [
        (("text", "Stage View", True), 5, "left"),
    ])


def lab05_token(page):
    lab = "lab05"
    page.goto(SONAR + "/sessions/new", wait_until="domcontentloaded"); settle(page, 3)
    page.fill("#login-input", "admin"); page.fill("#password-input", SONAR_PASS); page.keyboard.press("Enter"); settle(page, 4)
    page.goto(SONAR + "/account/security", wait_until="domcontentloaded"); settle(page, 3)
    page.fill("#token-name", "jenkins-scanner-token")
    page.get_by_text("Select Token Type", exact=True).click(); time.sleep(1)
    page.get_by_role("option", name="User Token").first.click(); time.sleep(1)
    shoot(page, lab, "01-sonar-token", [
        (("css", "#token-name"), 1, "down"),
        (("xpath_parent", "#token-select-type"), 2, "down"),
        (("xpath_parent", "#token-select-expiration"), 3, "down"),
        (("role", "button", "Generate", True), 4, "down"),
    ])


def lab07(page):
    lab = "lab07"
    job = "novashop-devsecops-capstone"
    login_b(page)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "01-stage-view-waiting", [
        (("text", "Stage View", True), 1, "left"),
    ])
    page.goto(BASE + f"/job/{job}/1/input/", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "02-approve", [
        (("css", 'button[name="proceed"]'), 2, "down"),
    ])
    page.locator('button[name="proceed"]').first.click(); time.sleep(3)
    wait_build(job, 1)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "03-stage-view-success", [
        (("text", "Stage View", True), 3, "left"),
    ])
    harbor_login(page)
    page.goto(HARBOR + "/harbor/projects", wait_until="domcontentloaded"); settle(page, 3)
    page.get_by_role("link", name="devops", exact=True).click(); settle(page, 3)
    page.get_by_role("link", name="devops/novashop-order-service").first.click(); settle(page, 3)
    shoot(page, lab, "04-harbor-artifact", [
        (("css", "clr-dg-row"), 4, "down"),
    ])
    page.goto(SONAR + "/sessions/new", wait_until="domcontentloaded"); settle(page, 3)
    if page.locator("#login-input").count():
        page.fill("#login-input", "admin"); page.fill("#password-input", SONAR_PASS); page.keyboard.press("Enter"); settle(page, 4)
    page.goto(SONAR + "/dashboard?id=novashop-order-service", wait_until="domcontentloaded"); settle(page, 5)
    shoot(page, lab, "05-sonar-dashboard", [
        (("text", "Passed", True), 5, "right"),
    ])


# ------------------------------------------------------------- arayüz yardımcıları
# Bütün adımlar tarayıcıda README'deki gibi yapılır; REST yalnızca sonucu okumak içindir.
def next_build(job):
    out = api(f'curl -s -u "admin:$P" "$J/job/{job}/api/json?tree=nextBuildNumber" || true\n')
    import json as _j
    return _j.loads(out)["nextBuildNumber"]


def console_text(job, no):
    return api(f'curl -s -u "admin:$P" "$J/job/{job}/{no}/consoleText"\n')


def build_result(job, no):
    import json as _j
    return _j.loads(api(f'curl -s -u "admin:$P" "$J/job/{job}/{no}/api/json?tree=result"\n')).get("result")


def ui_build_now(page, job, wait=True):
    n = next_build(job)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 2)
    page.locator('a.task-link[href$="/build?delay=0sec"]').first.click(); time.sleep(3)
    # Job'da parametre varsa (Build with Parameters) form açılır; README'deki gibi Build'e basılır
    if "/build" in page.url and page.locator("button.jenkins-button--primary").count():
        page.locator("button.jenkins-button--primary").first.click(); time.sleep(3)
    if wait:
        wait_build(job, n)
    return n


def param_input(page, name):
    return page.locator(f'xpath=//input[@name="name" and @value="{name}"]/following::*[@name="value"][1]').first


def ui_build_with_params(page, job, values, shot=None, wait=True):
    """values: {PARAM: değer | True/False}. shot: (lab, ad, marks) Build'e basmadan önce."""
    n = next_build(job)
    page.goto(BASE + f"/job/{job}/build?delay=0sec", wait_until="domcontentloaded"); settle(page, 2)
    for k, v in values.items():
        el = param_input(page, k)
        tag = el.evaluate("e => e.tagName + ':' + (e.type || '')")
        if tag.startswith("SELECT"):
            el.select_option(str(v))
        elif "checkbox" in tag:
            if bool(v) != el.is_checked():
                el.locator("xpath=following-sibling::label[1]").click()
        else:
            el.fill(str(v))
    time.sleep(0.5)
    if shot:
        shoot(page, shot[0], shot[1], shot[2])
    page.locator("button.jenkins-button--primary").first.click(); time.sleep(3)
    if wait:
        wait_build(job, n)
    return n


def ui_new_pipeline_scm(page, job, script_path, shots=None):
    """New Item -> Pipeline -> Pipeline script from SCM (jenkins-labs repo)."""
    page.goto(BASE + "/view/all/newJob", wait_until="domcontentloaded"); settle(page)
    page.fill("#name", job)
    page.locator("div.org_jenkinsci_plugins_workflow_job_WorkflowJob").first.click(); time.sleep(0.5)
    page.locator("#ok-button").click(); settle(page, 3)
    defsel = 'xpath=(//select[contains(@class,"dropdownList")][option[normalize-space(.)="Pipeline script from SCM"]])[1]'
    page.locator(defsel).select_option(label="Pipeline script from SCM"); time.sleep(2)
    scmsel = 'xpath=(//select[contains(@class,"dropdownList")][option[normalize-space(.)="Git"]])[1]'
    page.locator(scmsel).select_option(label="Git"); time.sleep(2)
    page.locator('input[name="_.url"]:visible').first.fill("https://gitlab.com/devops-practitioner-labs/jenkins-labs.git")
    page.locator('input[name="_.name"]:visible').first.fill("*/main")
    page.locator('input[name="_.scriptPath"]:visible').first.fill(script_path)
    page.locator('input[name="_.url"]:visible').first.press("Tab"); time.sleep(2)
    if shots:
        shots(page, defsel, scmsel)
    page.locator('button[name="Submit"]').first.click(); settle(page, 2)


def ui_new_pipeline_inline(page, job):
    page.goto(BASE + "/view/all/newJob", wait_until="domcontentloaded"); settle(page)
    page.fill("#name", job)
    page.locator("div.org_jenkinsci_plugins_workflow_job_WorkflowJob").first.click(); time.sleep(0.5)
    page.locator("#ok-button").click(); settle(page, 3)
    page.locator('button[name="Submit"]').first.click(); settle(page, 2)


def ui_set_script(page, job, script):
    page.goto(BASE + f"/job/{job}/configure", wait_until="domcontentloaded"); settle(page, 2)
    page.locator("div.ace_editor").first.wait_for(timeout=30000)
    set_pipeline_script(page, script); time.sleep(1)
    page.locator('button[name="Submit"]').first.click(); settle(page, 2)


def ui_credential(page, kind, fields, shot=None):
    """kind: 'Username with password' | 'Secret file' | 'Secret text'. fields: {css: değer | ('file', yol)}."""
    page.goto(BASE + "/manage/credentials/", wait_until="domcontentloaded"); settle(page, 2)
    page.get_by_role("button", name="Add Credentials").click(); time.sleep(2)
    page.get_by_text(kind, exact=True).click(); time.sleep(0.5)
    page.get_by_role("button", name="Next").click(); time.sleep(2)
    for css, v in fields.items():
        if isinstance(v, tuple) and v[0] == "file":
            page.locator(css).set_input_files(v[1])
        else:
            page.locator(css).first.fill(v)
    time.sleep(1)
    if shot:
        shoot(page, shot[0], shot[1], shot[2])
    page.get_by_role("button", name="Create").click(); settle(page, 2)


def ui_approve(page, job, no, shot=None, abort=False):
    for _ in range(90):
        if '"id"' in api(f'curl -s -u "admin:$P" "$J/job/{job}/{no}/wfapi/pendingInputActions" || true\n'):
            break
        time.sleep(2)
    page.goto(BASE + f"/job/{job}/{no}/input/", wait_until="domcontentloaded"); settle(page, 2)
    btn = 'button[name="abort"]' if abort else 'button[name="proceed"]'
    if shot:
        shoot(page, shot[0], shot[1], shot[2])
    page.locator(btn).first.click(); time.sleep(3)
    wait_build(job, no)


def lab01b_jobs(page):
    """B4: üç JCasC job'u arayüzden çalıştırılır."""
    lab = "lab01"
    login_b(page)
    n1 = ui_build_now(page, "01-hello-jcasc")
    n2 = ui_build_with_params(page, "02-parameters-jcasc", {}, shot=(lab, "b04-build-with-parameters", [
        (("union", ("css", 'input.jenkins-input[name="value"]'), ("css", 'select[name="value"]')), 7, "left"),
        (("css", "button.jenkins-button--primary"), 8, "up"),
    ]))
    n3 = ui_build_now(page, "03-environment-jcasc")
    for j, n, want in (("01-hello-jcasc", n1, "Merhaba! Job: 01-hello-jcasc"), ("02-parameters-jcasc", n2, "Merhaba DevOps Mühendisi; ortam: development"),
                       ("03-environment-jcasc", n3, "Koşul sağlandı: test ortamı adımı çalıştı.")):
        print("kontrol", j, n, build_result(j, n), want in console_text(j, n))


def lab02_run(page):
    """README sırası: 1) progressive-learning + 6 snippet, 2) üreteçler, 3) SCM job."""
    lab = "lab02"
    d = os.path.join(ROOT, "lab-02-declarative-pipeline", "snippets")
    login_b(page)
    for j in ("progressive-learning", "declarative-pipeline-demo"):   # önceki deneme kaldıysa
        delete_job(j)
    ui_new_pipeline_inline(page, "progressive-learning")
    for f in sorted(os.listdir(d)):
        ui_set_script(page, "progressive-learning", open(os.path.join(d, f), encoding="utf-8").read())
        n = ui_build_now(page, "progressive-learning")
        print("kontrol", f, n, build_result("progressive-learning", n))
        if f.startswith("05"):
            page.goto(BASE + "/job/progressive-learning/", wait_until="domcontentloaded"); settle(page, 2)
            shoot(page, lab, "06-build-with-parameters", [
                (("css", 'a.task-link[href$="/build?delay=0sec"]'), None, "right"),
            ])
            n = ui_build_with_params(page, "progressive-learning", {"APP_VERSION": "2.0.0", "DEPLOY_ENV": "qa", "RUN_TESTS": False})
            t = console_text("progressive-learning", n)
            print("kontrol 05-params", n, build_result("progressive-learning", n), "Surum           : 2.0.0" in t, "Test Kosulsun mu: false" in t)
    # 2. Üreteçler
    page.goto(BASE + "/job/progressive-learning/pipeline-syntax/", wait_until="domcontentloaded"); settle(page, 2)
    page.locator('input[name="_.artifacts"]').first.fill("output/*.txt")
    page.locator("#generatePipelineScript").click(); time.sleep(2)
    shoot(page, lab, "04-snippet-generator", [
        (("css", "select.dropdownList"), 1, "left"),
        (("css", 'input[name="_.artifacts"]'), 2, "left"),
        (("css", "#generatePipelineScript"), 3, "left"),
        (("css", "#prototypeText"), 4, "left"),
    ])
    page.goto(BASE + "/job/progressive-learning/directive-generator/", wait_until="domcontentloaded"); settle(page, 2)
    page.locator('button[id^="prototypeButton"]').first.click(); time.sleep(2)
    shoot(page, lab, "05-directive-generator", [
        (("css", "select.dropdownList"), 1, "left"),
        (("css", 'button[id^="prototypeButton"]'), 2, "left"),
        (("css", 'textarea[id^="prototypeText"]'), 3, "left"),
    ])
    # 3. SCM job
    def shots(page, defsel, scmsel):
        page.locator(defsel).scroll_into_view_if_needed(); page.mouse.wheel(0, 120); time.sleep(1)
        shoot(page, lab, "01-pipeline-from-scm", [
            (("css", defsel), 1, "left"), (("css", scmsel), 2, "left"),
            (("css", 'input[name="_.url"]:visible'), 3, "left"),
        ])
        page.locator('input[name="_.scriptPath"]:visible').first.scroll_into_view_if_needed(); time.sleep(1)
        shoot(page, lab, "02-branch-script-path", [
            (("css", 'input[name="_.name"]:visible'), 4, "left"),
            (("css", 'input[name="_.scriptPath"]:visible'), 5, "left"),
            (("css", 'button[name="Submit"]'), 6, "up"),
        ])
    ui_new_pipeline_scm(page, "declarative-pipeline-demo", "lab-02-declarative-pipeline/Jenkinsfile", shots)
    n = ui_build_now(page, "declarative-pipeline-demo")
    t = console_text("declarative-pipeline-demo", n)
    print("kontrol scm", n, build_result("declarative-pipeline-demo", n), "--- Tüm Testler Geçti ---" in t)
    page.goto(BASE + "/job/declarative-pipeline-demo/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "03-stage-view-artifacts", [
        (("css", "table.jobsTable, #pipeline-box, .stage-view, div.table-box"), 7, None),
        (("text", "Last Successful Artifacts"), 8, "left"),
    ])


def lab02a_run(page):
    """README 2-5: kubeconfig ve Docker Hub credential'ları, job, build'ler (gerçek)."""
    lab = "lab02a"
    job = "python-dockerhub-kind"
    login_b(page)
    page.goto(BASE + "/manage/credentials/", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "01-add-credentials", [(("role", "button", "Add Credentials"), 1, "down")])
    page.get_by_role("button", name="Add Credentials").click(); time.sleep(2)
    page.get_by_text("Secret file", exact=True).click(); time.sleep(0.5)
    shoot(page, lab, "02-kind-secret-file", [
        (("text", "Secret file", True), 2, "left"), (("role", "button", "Next"), 3, "down")])
    page.keyboard.press("Escape"); time.sleep(1)
    ui_credential(page, "Secret file", {'input[name="file"]': ("file", os.environ["JK_KUBECONFIG"]),
                                        'input[name="_.id"]': "kubeconfig-student-kind",
                                        'input[name="_.description"]': "KinD cluster kubeconfig"},
                  shot=(lab, "03-secret-file-form", [
                      (("css", 'input[name="file"]'), 4, "left"), (("css", 'input[name="_.id"]'), 5, "left"),
                      (("role", "button", "Create"), 6, "down")]))
    ui_credential(page, "Username with password", {'input[name="_.username"]': "hbayraktar",
                                                   'input[name="_.password"]': os.environ["JK_DH_TOKEN"],
                                                   'input[name="_.id"]': "dockerhub-creds"},
                  shot=(lab, "07-dockerhub-credential", [
                      (("css", 'input[name="_.username"]'), 1, "left"), (("css", 'input[name="_.password"]'), 2, "left"),
                      (("css", 'input[name="_.id"]'), 3, "left"), (("role", "button", "Create"), 4, "down")]))
    ui_new_pipeline_scm(page, job, "lab-02a-python-dockerhub-kind/Jenkinsfile")
    n1 = ui_build_now(page, job)
    print("kontrol build1", n1, build_result(job, n1))
    n2 = ui_build_with_params(page, job, {"STUDENT_NO": "103", "PUSH_TO_DOCKERHUB": True}, shot=(lab, "04-build-with-parameters", [
        (("css", 'input.jenkins-input[name="value"]'), 7, "left"),
        (("css", '.jenkins-checkbox:has(input[name="value"])'), 8, "left"),
        (("css", "button.jenkins-button--primary"), 9, "up")]))
    t = console_text(job, n2)
    print("kontrol build2", n2, build_result(job, n2), "Login Succeeded" in t, "successfully rolled out" in t)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "05-stage-view", [(("text", "Stage View", True), 10, "left")])
    page.goto("https://student103-app1.devopsatolyesi.com/", wait_until="domcontentloaded"); settle(page, 1)
    shoot(page, lab, "06-app", [])


def lab03_run(page):
    lab = "lab03"
    job = "parametric-pipeline-demo"
    login_b(page)
    ui_new_pipeline_scm(page, job, "lab-03-parameters-approval-resilience/Jenkinsfile")
    n = ui_build_now(page, job); print("kontrol ilk", n, build_result(job, n))
    n = ui_build_with_params(page, job, {"DEPLOY_ENV": "development", "RELEASE_VERSION": "1.2.1", "RUN_INTEGRATION_TESTS": True, "REPLICA_COUNT": "1"})
    t = console_text(job, n); print("kontrol dev", n, build_result(job, n), 'skipped due to when conditional' in t)
    shot = (lab, "01-build-with-parameters", [
        (("css", 'select[name="value"]'), 1, "left"), (("css", 'input.jenkins-input[name="value"]'), 2, "left"),
        (("css", '.jenkins-checkbox:has(input[name="value"])'), 3, "left"),
        (("css", 'xpath=(//select[@name="value"])[2]'), 4, "left"), (("css", "button.jenkins-button--primary"), 5, "up")])
    n = ui_build_with_params(page, job, {"DEPLOY_ENV": "production", "RELEASE_VERSION": "2.0.0", "RUN_INTEGRATION_TESTS": True, "REPLICA_COUNT": "5"}, shot=shot, wait=False)
    for _ in range(60):
        if '"id"' in api(f'curl -s -u "admin:$P" "$J/job/{job}/{n}/wfapi/pendingInputActions" || true\n'):
            break
        time.sleep(2)
    page.goto(BASE + f"/job/{job}/{n}/console", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "02-input-console", [
        (("css", 'a.post-hyperlink-note-button:has-text("Dağıtımı Başlat")'), 6, "left"),
        (("css", 'a.post-hyperlink-note-button:has-text("Abort")'), 7, "right")])
    page.locator('a.post-hyperlink-note-button:has-text("Dağıtımı Başlat")').first.click(); time.sleep(3)
    wait_build(job, n)
    t = console_text(job, n); print("kontrol onay", n, build_result(job, n), "Approved by" in t)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "03-stage-view-approved", [(("text", "Stage View", True), None, "left")])
    n = ui_build_with_params(page, job, {"DEPLOY_ENV": "production", "RELEASE_VERSION": "2.1.0"}, wait=False)
    ui_approve(page, job, n, abort=True, shot=(lab, "04-input-page-abort", [(("css", 'button[name="abort"]'), 8, "down")]))
    t = console_text(job, n); print("kontrol ret", n, build_result(job, n), "Rejected by" in t)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "05-stage-view-aborted", [(("text", "Stage View", True), None, "left")])
    n = ui_build_with_params(page, job, {"DEPLOY_ENV": "production", "RELEASE_VERSION": "2.2.0"}, wait=False)
    time.sleep(310)
    wait_build(job, n)
    t = console_text(job, n); print("kontrol zaman asimi", n, build_result(job, n), "Timeout has been exceeded" in t)


def lab04_run(page):
    lab = "lab04"
    job = "docker-harbor-pipeline"
    harbor_login(page)
    page.goto(HARBOR + "/harbor/projects", wait_until="domcontentloaded"); settle(page, 3)
    page.get_by_role("button", name="NEW PROJECT").click(); time.sleep(2)
    page.fill("#create_project_name", "devops-public")
    page.locator('clr-checkbox-wrapper:has(#create_project_public) label').first.click(); time.sleep(0.5)
    shoot(page, lab, "01-harbor-new-project", [
        (("css", "#create_project_name"), 1, "left"),
        (("css", 'clr-checkbox-wrapper:has(#create_project_public)'), 2, "left"),
        (("css", "#new-project-ok"), 3, "up")])
    page.locator("#new-project-ok").click(); time.sleep(2)
    login_b(page)
    ui_credential(page, "Username with password", {'input[name="_.username"]': "admin", 'input[name="_.password"]': "Harbor12345",
                                                   'input[name="_.id"]': "harbor-creds"},
                  shot=(lab, "02-jenkins-credential", [
                      (("css", 'input[name="_.username"]'), 4, "left"), (("css", 'input[name="_.password"]'), 5, "left"),
                      (("css", 'input[name="_.id"]'), 6, "left"), (("role", "button", "Create"), 7, "down")]))
    ui_new_pipeline_scm(page, job, "lab-04-credentials-docker-harbor-push/Jenkinsfile")
    n = ui_build_now(page, job)
    t = console_text(job, n); print("kontrol", n, build_result(job, n), "Login Succeeded" in t)
    print("\n".join(l for l in t.splitlines() if "digest:" in l or "başarıyla yüklendi" in l or "Unit tests" in l))
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "03-stage-view", [(("text", "Stage View", True), 8, "left")])
    harbor_login(page)
    page.goto(HARBOR + "/harbor/projects", wait_until="domcontentloaded"); settle(page, 3)
    page.get_by_role("link", name="devops-public", exact=True).click(); settle(page, 3)
    page.get_by_role("link", name="devops-public/demo-app").first.click(); settle(page, 3)
    shoot(page, lab, "04-harbor-artifacts", [(("css", "clr-dg-row"), 9, "down")])


def sonar_first_login(page, lab):
    """İlk giriş admin/admin -> zorunlu parola değişikliği."""
    page.goto(SONAR + "/sessions/new", wait_until="domcontentloaded"); settle(page, 3)
    page.fill("#login-input", "admin"); page.fill("#password-input", "admin"); page.keyboard.press("Enter"); settle(page, 5)
    pw = page.locator('input[type="password"]:visible')
    if pw.count() >= 3:
        pw.nth(0).fill("admin"); pw.nth(1).fill(SONAR_PASS); pw.nth(2).fill(SONAR_PASS); time.sleep(0.5)
        shoot(page, lab, "00-sonar-change-password", [
            (("union", ("css", 'xpath=(//input[@type="password"])[1]'), ("css", 'xpath=(//input[@type="password"])[3]')), None, "left"),
            (("role", "button", "Update"), None, "down")])
        page.get_by_role("button", name="Update").first.click(); settle(page, 4)
    for b in page.get_by_role("button", name="Dismiss").all():
        try:
            b.click(timeout=1000)
        except Exception:
            pass


def lab05_run(page):
    import re as _re
    lab = "lab05"
    job = "devsecops-quality-pipeline"
    sonar_first_login(page, lab)
    page.goto(SONAR + "/account/security", wait_until="domcontentloaded"); settle(page, 3)
    page.fill("#token-name", "jenkins-scanner-token")
    page.get_by_text("Select Token Type", exact=True).click(); time.sleep(1)
    page.get_by_role("option", name="User Token").first.click(); time.sleep(1)
    shoot(page, lab, "01-sonar-token", [
        (("css", "#token-name"), 1, "down"), (("xpath_parent", "#token-select-type"), 2, "down"),
        (("xpath_parent", "#token-select-expiration"), 3, "down"), (("role", "button", "Generate", True), 4, "down")])
    page.get_by_role("button", name="Generate", exact=True).click(); time.sleep(3)
    m = _re.search(r"squ_[0-9a-f]{40}", page.content())
    token = m.group(0)
    print("kontrol token uretildi", len(token))
    page.goto(SONAR + "/admin/settings?category=security", wait_until="domcontentloaded"); settle(page, 3)
    tog = page.locator('[id="input-settings[sonar.validateWebhooks]"]')
    if tog.get_attribute("aria-checked") == "true":
        tog.click(); time.sleep(1)
        sv = page.get_by_role("button", name="Save")
        if sv.count():
            sv.first.click(); time.sleep(2)
    shoot(page, lab, "02-sonar-validate-webhooks", [(("css", '[id="input-settings[sonar.validateWebhooks]"]'), 5, "left")])
    print("kontrol validateWebhooks", tog.get_attribute("aria-checked"))
    page.goto(SONAR + "/admin/webhooks", wait_until="domcontentloaded"); settle(page, 3)
    page.get_by_role("button", name="Create").first.click(); time.sleep(2)
    page.fill("#webhook-name", "Jenkins-Webhook")
    page.fill("#webhook-url", "http://jenkins:8080/sonarqube-webhook/")
    shoot(page, lab, "03-sonar-webhook", [
        (("css", "#webhook-name"), 6, "left"), (("css", "#webhook-url"), 7, "left"),
        (("css", '[role=dialog] button:has-text("Create")'), 8, "down")])
    page.locator('[role=dialog] button:has-text("Create")').first.click(); time.sleep(3)
    print("kontrol webhook", page.get_by_text("http://jenkins:8080/sonarqube-webhook/").count() > 0)
    # Jenkins
    login_b(page)
    ui_credential(page, "Secret text", {'input[name="_.secret"], textarea[name="_.secret"]': token, 'input[name="_.id"]': "sonar-token"},
                  shot=(lab, "04-jenkins-secret-text", [
                      (("css", 'input[name="_.secret"], textarea[name="_.secret"]'), 1, "left"),
                      (("css", 'input[name="_.id"]'), 2, "left"), (("role", "button", "Create"), 3, "down")]))
    page.goto(BASE + "/manage/configure", wait_until="domcontentloaded"); settle(page, 3)
    page.get_by_role("button", name="Add SonarQube").first.click(); time.sleep(2)
    page.locator('input[name="sonar.name"]').first.fill("sonarqube-local")
    page.locator('input[name="sonar.serverUrl"]').first.fill("http://172.17.0.1:19000")
    cred = page.locator('xpath=(//input[@name="sonar.serverUrl"]/following::select[@name="_.credentialsId"])[1]')
    cred.select_option("sonar-token"); time.sleep(1)
    page.locator('input[name="sonar.name"]').scroll_into_view_if_needed(); page.mouse.wheel(0, 150); time.sleep(1)
    shoot(page, lab, "05-jenkins-sonar-server", [
        (("css", 'input[name="sonar.name"]'), 4, "left"), (("css", 'input[name="sonar.serverUrl"]'), 5, "left"),
        (("css", 'xpath=(//input[@name="sonar.serverUrl"]/following::select[@name="_.credentialsId"])[1]'), 6, "left")])
    page.locator('button[name="Submit"]').first.click(); settle(page, 2)
    ui_new_pipeline_scm(page, job, "lab-05-sonarqube-trivy-devsecops/Jenkinsfile")
    n = ui_build_now(page, job); print("kontrol ilk", n, build_result(job, n))
    shot = (lab, "06-build-with-parameters", [
        (("css", 'xpath=(//*[contains(@class,"jenkins-checkbox")][.//input[@name="value"]])[1]'), 1, "left"),
        (("css", 'select[name="value"]'), 2, "left"),
        (("css", 'xpath=(//*[contains(@class,"jenkins-checkbox")][.//input[@name="value"]])[2]'), 3, "left"),
        (("css", "button.jenkins-button--primary"), 4, "up")])
    n = ui_build_with_params(page, job, {"ENABLE_QUALITY_GATE": True, "TRIVY_SEVERITY": "HIGH,CRITICAL", "FAIL_ON_VULNERABILITY": False}, shot=shot)
    t = console_text(job, n)
    print("kontrol senaryo1", n, build_result(job, n), "[QUALITY-GATE] Durum: OK" in t)
    print("\n".join(l for l in t.splitlines() if l.startswith("Total:") or "QUALITY" in l or "TRIVY" in l or "ANALYSIS SUCCESSFUL" in l))
    n = ui_build_with_params(page, job, {"ENABLE_QUALITY_GATE": True, "TRIVY_SEVERITY": "HIGH,CRITICAL", "FAIL_ON_VULNERABILITY": True})
    t = console_text(job, n)
    print("kontrol senaryo2", n, build_result(job, n))
    print("\n".join(l for l in t.splitlines() if l.startswith("Total:") or "TRIVY-IMAGE" in l))
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "07-stage-view", [(("text", "Stage View", True), 5, "left")])
    page.goto(SONAR + "/dashboard?id=devops-jenkins-app", wait_until="domcontentloaded"); settle(page, 5)
    shoot(page, lab, "08-sonar-dashboard", [(("text", "Passed", True), None, "right")])


def lab06_run(page):
    lab = "lab06"
    job = "k8s-cd-deploy-pipeline"
    login_b(page)
    ui_new_pipeline_scm(page, job, "lab-06-kubernetes-kind-rolling-update/Jenkinsfile")
    n = ui_build_now(page, job); t = console_text(job, n)
    print("kontrol basarili", n, build_result(job, n), "successfully rolled out" in t)
    shot = (lab, "01-build-with-parameters", [
        (("css", 'xpath=//input[@name="name" and @value="APP_IMAGE"]/following::*[@name="value"][1]'), 1, "left"),
        (("css", '.jenkins-checkbox:has(input[name="value"])'), 2, "left"),
        (("css", "button.jenkins-button--primary"), 3, "up")])
    n = ui_build_with_params(page, job, {"APP_IMAGE": "nginx:non-existent-tag-9999", "AUTO_ROLLBACK": True}, shot=shot)
    t = console_text(job, n)
    print("kontrol rollback", n, build_result(job, n), "rolled back" in t)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "02-stage-view", [(("text", "Stage View", True), 4, "left")])
    page.goto(BASE + f"/job/{job}/{n}/console", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "03-console-rollback", [
        (("text", "timed out waiting for the condition"), 5, "left"), (("text", "rolled back"), 6, "left")])


def lab07_run(page):
    lab = "lab07"
    job = "novashop-devsecops-capstone"
    login_b(page)
    ui_new_pipeline_scm(page, job, "lab-07-devsecops-capstone-novashop/Jenkinsfile")
    n = ui_build_now(page, job, wait=False)
    for _ in range(300):
        if '"id"' in api(f'curl -s -u "admin:$P" "$J/job/{job}/{n}/wfapi/pendingInputActions" || true\n'):
            break
        r = build_result(job, n)
        if r:
            print("kontrol erken bitti", r); break
        time.sleep(3)
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "01-stage-view-waiting", [(("text", "Stage View", True), 1, "left")])
    time.sleep(int(os.environ.get("JK_PAUSE_BEFORE_APPROVE", "0")))   # README'deki staging kontrolleri için
    ui_approve(page, job, n, shot=(lab, "02-approve", [(("css", 'button[name="proceed"]'), 2, "down")]))
    t = console_text(job, n)
    print("kontrol", n, build_result(job, n), "Approved by" in t)
    print("\n".join(l for l in t.splitlines() if any(k in l for k in ("PASSED", "EXECUTION SUCCESS", "Login Succeeded", "digest:", "successfully rolled out", "SUCCESS]"))))
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "03-stage-view-success", [(("text", "Stage View", True), 3, "left")])
    harbor_login(page)
    page.goto(HARBOR + "/harbor/projects", wait_until="domcontentloaded"); settle(page, 3)
    page.get_by_role("link", name="devops-public", exact=True).click(); settle(page, 3)
    page.get_by_role("link", name="devops-public/novashop-order-service").first.click(); settle(page, 3)
    shoot(page, lab, "04-harbor-artifact", [(("css", "clr-dg-row"), 4, "down")])
    page.goto(SONAR + "/sessions/new", wait_until="domcontentloaded"); settle(page, 3)
    if page.locator("#login-input").count():
        page.fill("#login-input", "admin"); page.fill("#password-input", SONAR_PASS); page.keyboard.press("Enter"); settle(page, 4)
    page.goto(SONAR + "/dashboard?id=novashop-order-service", wait_until="domcontentloaded"); settle(page, 5)
    shoot(page, lab, "05-sonar-dashboard", [(("text", "Passed", True), 5, "right")])


def b01_run(page):
    lab = "b01"
    d = os.path.join(ROOT, LAB_DIRS[lab])
    login_b(page)
    delete_job("groovy-snippets"); delete_job("groovy-script-loops-demo")
    ui_new_pipeline_inline(page, "groovy-snippets")
    for f in sorted(os.listdir(os.path.join(d, "snippets"))):
        ui_set_script(page, "groovy-snippets", open(os.path.join(d, "snippets", f), encoding="utf-8").read())
        n = ui_build_now(page, "groovy-snippets")
        t = console_text("groovy-snippets", n)
        print("kontrol", f, n, build_result("groovy-snippets", n))
        print("\n".join(l for l in t.splitlines() if not l.startswith("[Pipeline]") and "Started by" not in l and "Running on" not in l)[:900])
    ui_new_pipeline_inline(page, "groovy-script-loops-demo")
    ui_set_script(page, "groovy-script-loops-demo", open(os.path.join(d, "Jenkinsfile"), encoding="utf-8").read())
    n = ui_build_now(page, "groovy-script-loops-demo")
    t = console_text("groovy-script-loops-demo", n)
    print("kontrol jenkinsfile", n, build_result("groovy-script-loops-demo", n))
    import re as _re
    print("\n".join(_re.sub(r"^\[[0-9TZ:.-]+\] ", "", l) for l in t.splitlines() if any(k in l for k in ("GROOVY-LOG", "Toplam", "--- Servis", "GATEKEEPER", "FAST-TRACK", "SUCCESS]"))))
    page.goto(BASE + f"/job/groovy-script-loops-demo/{n}/console", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "01-console-loops", [
        (("text", "Toplam 4 Mikroservis"), 1, "left"),
    ])


def b01_prod(page):
    login_b(page)
    n = ui_build_with_params(page, "groovy-snippets", {"TARGET_ENV": "prod"})
    t = console_text("groovy-snippets", n)
    print("kontrol prod", n, build_result("groovy-snippets", n), [l for l in t.splitlines() if "DIKKAT" in l or "BILGI" in l])


def b02_run(page):
    import re as _re
    lab = "b02"; job = "build-managers-test-pipeline"
    login_b(page)
    delete_job(job)
    ui_new_pipeline_scm(page, job, "bonus-labs/02-build-managers-npm-python/Jenkinsfile")
    n = ui_build_now(page, job); print("kontrol ilk", n, build_result(job, n))
    n = ui_build_with_params(page, job, {"TARGET_STACK": "all", "RUN_LINTER": True}, shot=(lab, "01-build-with-parameters", [
        (("css", 'select[name="value"]'), 1, "left"), (("css", '.jenkins-checkbox:has(input[name="value"])'), 2, "left"),
        (("css", "button.jenkins-button--primary"), 3, "up")]))
    t = console_text(job, n)
    print("kontrol all", n, build_result(job, n))
    print("\n".join(_re.sub(r"^\[[0-9TZ:.-]+\] ", "", l) for l in t.splitlines() if any(k in l for k in ("PASSED", "passed", "TEST", "SUCCESS]", "ERROR", "flake8", "E501", "F401"))))
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "02-stage-view", [(("text", "Stage View", True), 4, "left")])


def b02_node(page):
    login_b(page)
    n = ui_build_with_params(page, "build-managers-test-pipeline", {"TARGET_STACK": "node"})
    t = console_text("build-managers-test-pipeline", n)
    print("kontrol node", n, build_result("build-managers-test-pipeline", n), [l.split("] ",1)[-1] for l in t.splitlines() if "skipped due to when" in l])


def b03_run(page):
    lab = "b03"; d = os.path.join(ROOT, LAB_DIRS[lab])
    up, down = "parallel-execution-demo", "downstream-deploy-worker"
    login_b(page)
    delete_job(up); delete_job(down)
    ui_new_pipeline_inline(page, down)
    ui_set_script(page, down, open(os.path.join(d, "downstream-job", "Jenkinsfile"), encoding="utf-8").read())
    n = ui_build_now(page, down); print("kontrol downstream ilk", n, build_result(down, n))
    ui_new_pipeline_inline(page, up)
    ui_set_script(page, up, open(os.path.join(d, "Jenkinsfile"), encoding="utf-8").read())
    n = ui_build_now(page, up); print("kontrol upstream ilk", n, build_result(up, n))
    time.sleep(8)
    dn = next_build(down)
    n = ui_build_with_params(page, up, {"APP_VERSION": "1.5.0", "TRIGGER_DOWNSTREAM": True})
    t = console_text(up, n); print("kontrol upstream", n, build_result(up, n), "[DOWNSTREAM]" in t)
    wait_build(down, dn)
    td = console_text(down, dn); print("kontrol downstream", dn, build_result(down, dn), "gelen sürüm: 1.5.0" in td)
    page.goto(BASE + f"/job/{up}/", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "01-stage-view-parallel", [(("text", "Stage View", True), 1, "left")])
    page.goto(BASE + f"/job/{down}/", wait_until="domcontentloaded"); settle(page, 3)
    shoot(page, lab, "02-downstream-builds", [(("css", f'a[href$="/job/{down}/{dn}/"]'), 2, "right")])
    # Replay
    page.goto(BASE + f"/job/{up}/{n}/replay", wait_until="domcontentloaded"); settle(page, 3)
    page.locator("div.ace_editor").first.wait_for(timeout=30000)
    page.evaluate("""() => { const ed = document.querySelector('.ace_editor').env.editor;
        ed.setValue(ed.getValue().replace('echo "Sürüm: ${params.APP_VERSION}"', 'echo "Sürüm (Replay ile değişti): ${params.APP_VERSION}"'), 1); }""")
    time.sleep(1)
    rn = next_build(up)
    shoot(page, lab, "03-replay", [(("css", "div.ace_editor"), 3, "left"), (("css", 'button[name="Submit"]'), 4, "up")])
    page.locator('button[name="Submit"]').first.click(); time.sleep(3)
    wait_build(up, rn)
    t = console_text(up, rn); print("kontrol replay", rn, build_result(up, rn), "Replay ile değişti" in t, "Replayed #" in t)
    # Restart from Stage
    page.goto(BASE + f"/job/{up}/{rn}/restart", wait_until="domcontentloaded"); settle(page, 3)
    sel = page.locator("select").first
    sel.select_option(label="Sonuçların Birleştirilmesi ve Paketleme"); time.sleep(0.5)
    sn = next_build(up)
    shoot(page, lab, "04-restart-from-stage", [(("css", "select"), 5, "left"), (("css", 'button[name="Submit"]'), 6, "up")])
    page.locator('button[name="Submit"]').first.click(); time.sleep(3)
    wait_build(up, sn)
    t = console_text(up, sn)
    print("kontrol restart", sn, build_result(up, sn))
    print("\n".join(l.split("] ", 1)[-1] for l in t.splitlines() if "Restarted" in l or "skipped" in l.lower() or "Version:" in l)[:800])


def b04_run(page):
    lab = "b04"; job = "multibranch-demo"
    login_b(page)
    delete_job(job)
    page.goto(BASE + "/view/all/newJob", wait_until="domcontentloaded"); settle(page)
    page.fill("#name", job)
    page.locator("div.org_jenkinsci_plugins_workflow_multibranch_WorkflowMultiBranchProject").click(); time.sleep(0.5)
    shoot(page, lab, "01-new-multibranch", [(("css", "#name"), 1, "left"),
        (("css", "div.org_jenkinsci_plugins_workflow_multibranch_WorkflowMultiBranchProject"), 2, "left"), (("css", "#ok-button"), 3, "up")])
    page.locator("#ok-button").click(); settle(page, 4)
    page.get_by_role("button", name="Add source").first.click(); time.sleep(1.5)
    page.locator(".jenkins-dropdown__item", has_text="Git").first.click(); time.sleep(2)
    page.locator('input[name="_.remote"]').first.fill("file:///var/jenkins_home/sample-multibranch-repo.git")
    page.locator('input[name="_.remote"]').first.press("Tab"); time.sleep(1)
    page.locator('input[name="_.remote"]').first.scroll_into_view_if_needed(); time.sleep(0.5)
    shoot(page, lab, "02-git-source", [(("role", "button", "Add source"), 4, "left"), (("css", 'input[name="_.remote"]'), 5, "left")])
    cb = page.locator('input[name="com-cloudbees-hudson-plugins-folder-computed-PeriodicFolderTrigger"]')
    cb.locator("xpath=following-sibling::label[1]").click(); time.sleep(1)
    interval = page.locator('xpath=//input[@name="com-cloudbees-hudson-plugins-folder-computed-PeriodicFolderTrigger"]/following::select[1]')
    interval.select_option(label="1 minute"); time.sleep(0.5)
    page.locator('input[name="_.daysToKeepStr"]').first.fill("1")
    page.locator('input[name="_.numToKeepStr"]').first.fill("5")
    cb.scroll_into_view_if_needed(); time.sleep(0.5)
    shoot(page, lab, "03-scan-orphaned", [
        (("css", '.jenkins-checkbox:has(input[name="com-cloudbees-hudson-plugins-folder-computed-PeriodicFolderTrigger"])'), 6, "left"),
        (("css", 'xpath=//input[@name="com-cloudbees-hudson-plugins-folder-computed-PeriodicFolderTrigger"]/following::select[1]'), 7, "left"),
        (("union", ("css", 'input[name="_.daysToKeepStr"]'), ("css", 'input[name="_.numToKeepStr"]')), 8, "left")])
    page.locator('button[name="Submit"]').first.click(); settle(page, 6)
    shoot(page, lab, "04-scan-log", [])
    for br, path in (("main", "main"), ("develop", "develop"), ("feature/login", "feature%252Flogin")):
        jp = f"{job}/job/{path}"
        for _ in range(60):
            r = api(f'curl -s -u "admin:$P" "$J/job/{jp}/1/api/json?tree=result" || true\n')
            if '"result":"' in r:
                break
            time.sleep(3)
        t = console_text(jp, 1)
        print("kontrol", br, build_result(jp, 1), [l.split("] ", 1)[-1] for l in t.splitlines() if any(k in l for k in ("[STAGING]", "[PRODUCTION]", "[FEATURE-BRANCH]", "SUCCESS]", "skipped due to when")) ])
    page.goto(BASE + f"/job/{job}/", wait_until="domcontentloaded"); settle(page, 3)
    shoot(page, lab, "05-branches", [(("css", "#projectstatus"), 9, "left")])


def b05_plugin(page):
    lab = "b05"
    login_b(page)
    page.goto(BASE + "/manage/pluginManager/available", wait_until="domcontentloaded"); settle(page, 2)
    page.locator("input.jenkins-search__input:visible").fill("GitLab")
    row = page.locator('tr[data-plugin-id="gitlab-plugin"]'); row.wait_for(timeout=30000); time.sleep(1)
    row.locator('input[type="checkbox"]').check(force=True); time.sleep(0.5)
    shoot(page, lab, "01-plugin-gitlab", [
        (("css", "input.jenkins-search__input:visible"), 1, "down"),
        (("css", 'tr[data-plugin-id="gitlab-plugin"] .jenkins-checkbox'), 2, "down"),
        (("role", "button", "Install", True), 3, "down")])
    page.get_by_role("button", name="Install", exact=True).first.click(); settle(page, 3)
    for _ in range(90):
        txt = page.locator("body").inner_text()
        if "GitLab" in txt and ("Success" in txt or "Failure" in txt) and "Pending" not in txt and "Installing" not in txt:
            break
        time.sleep(3); page.reload(); settle(page, 1)
    print("kontrol restart gerekli mi:", "restart" in page.locator("body").inner_text().lower())
    print("\n".join(l for l in page.locator("body").inner_text().splitlines() if "GitLab" in l or "Success" in l or "Failure" in l or "estart" in l)[:800])


def b05_job(page):
    lab = "b05"; job = "gitlab-webhook-demo"; d = os.path.join(ROOT, LAB_DIRS[lab])
    login_b(page)
    delete_job(job)
    ui_new_pipeline_inline(page, job)
    page.goto(BASE + f"/job/{job}/configure", wait_until="domcontentloaded"); settle(page, 3)
    cb = page.locator('input[name="com-dabsquared-gitlabjenkins-GitLabPushTrigger"]')
    cb.locator("xpath=following-sibling::label[1]").click(); time.sleep(1)
    page.locator('xpath=//input[@name="com-dabsquared-gitlabjenkins-GitLabPushTrigger"]/following::button[contains(@class,"advanced-button")][1]').click(); time.sleep(1)
    page.get_by_role("button", name="Generate").first.click(); time.sleep(2)
    token = page.locator('input[name="_.secretToken"]').first.input_value()
    cb.scroll_into_view_if_needed(); time.sleep(0.5)
    shoot(page, lab, "02-trigger", [
        (("css", '.jenkins-checkbox:has(input[name="com-dabsquared-gitlabjenkins-GitLabPushTrigger"])'), 4, "left")])
    page.locator('input[name="_.secretToken"]').first.scroll_into_view_if_needed(); time.sleep(0.5)
    shoot(page, lab, "03-secret-token", [
        (("css", 'input[name="_.secretToken"]'), 5, "left"), (("role", "button", "Generate"), 6, "up")])
    page.locator("div.ace_editor").first.wait_for(timeout=30000)
    set_pipeline_script(page, open(os.path.join(d, "Jenkinsfile"), encoding="utf-8").read()); time.sleep(1)
    page.locator('button[name="Submit"]').first.click(); settle(page, 2)
    n = ui_build_now(page, job); print("kontrol ilk", n, build_result(job, n))
    open(os.environ["JK_TOKEN_FILE"], "w").write(token)
    print("kontrol token uzunluk", len(token))


def b05_after(page):
    lab = "b05"; job = "gitlab-webhook-demo"
    login_b(page)
    for _ in range(40):
        r = build_result(job, 2) if '"result"' in api(f'curl -s -u "admin:$P" "$J/job/{job}/2/api/json?tree=result" || true\n') else None
        if r:
            break
        time.sleep(3)
    t = console_text(job, 2)
    print("kontrol webhook build", build_result(job, 2))
    print("\n".join(l.split("] ", 1)[-1] for l in t.splitlines() if any(k in l for k in ("Started by", "EVENT-DRIVEN", "Tetikleme", "Derleme Numarası", "SUCCESS]"))))
    page.goto(BASE + f"/job/{job}/2/console", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "04-console-webhook", [(("text", "Started by GitLab push"), 7, "left")])


def b07_run(page):
    lab = "b07"; job = "shared-library-demo"; d = os.path.join(ROOT, LAB_DIRS[lab])
    H = 'xpath=//*[contains(text(),"Global Trusted Pipeline Libraries")]'
    login_b(page)
    delete_job(job)
    page.goto(BASE + "/manage/configure", wait_until="domcontentloaded"); settle(page, 3)
    page.locator(H + '/following::button[normalize-space(.)="Add"][1]').first.click(); time.sleep(2)
    page.locator(H + '/following::input[@name="_.name"][1]').fill("devops-shared-library")
    page.locator(H + '/following::input[@name="_.defaultVersion"][1]').fill("main")
    page.locator(H + '/following::input[@name="_.remote"][1]').fill("https://gitlab.com/devops-practitioner-labs/jenkins-labs.git")
    page.locator(H + '/following::input[@name="_.libraryPath"][1]').fill("bonus-labs/07-shared-libraries-jcasc-ops/")
    page.locator(H + '/following::input[@name="_.defaultVersion"][1]').press("Tab"); time.sleep(3)
    page.locator(H + '/following::input[@name="_.name"][1]').scroll_into_view_if_needed(); page.mouse.wheel(0, -60); time.sleep(1)
    shoot(page, lab, "01-library-name-version", [
        (("css", H + '/following::input[@name="_.name"][1]'), 1, "left"),
        (("css", H + '/following::input[@name="_.defaultVersion"][1]'), 2, "left")])
    page.locator(H + '/following::input[@name="_.remote"][1]').scroll_into_view_if_needed(); time.sleep(0.5)
    shoot(page, lab, "02-library-repo", [
        (("css", H + '/following::input[@name="_.remote"][1]'), 3, "left")])
    page.locator(H + '/following::input[@name="_.libraryPath"][1]').scroll_into_view_if_needed(); time.sleep(0.5)
    shoot(page, lab, "03-library-path", [
        (("css", H + '/following::input[@name="_.libraryPath"][1]'), 4, "left"), (("css", 'button[name="Submit"]'), 5, "up")])
    page.locator('button[name="Submit"]').first.click(); settle(page, 3)
    ui_new_pipeline_inline(page, job)
    ui_set_script(page, job, open(os.path.join(d, "Jenkinsfile"), encoding="utf-8").read())
    n = ui_build_now(page, job)
    t = console_text(job, n)
    print("kontrol", n, build_result(job, n))
    print("\n".join(l for l in t.splitlines() if any(k in l for k in ("Loading library", "DEVOPS-AUDIT", "SHARED-LIB", "NOTIFICATION", "digest:", "ERROR", "Exception"))))
    page.goto(BASE + f"/job/{job}/{n}/console", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "04-console", [(("text", "Loading library devops-shared-library"), 6, "left")])
    # Script Console
    page.goto(BASE + "/manage/script", wait_until="domcontentloaded"); settle(page, 2)
    code = open(os.path.join(d, "scripts", "system-info.groovy"), encoding="utf-8").read()
    page.evaluate("""(c) => { const cm = document.querySelector('.CodeMirror'); if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(c); return; }
        const ta = document.querySelector('textarea[name="script"]'); ta.value = c; }""", code)
    time.sleep(0.5)
    page.locator('button[name="Submit"], button:has-text("Run")').first.click(); settle(page, 3)
    shoot(page, lab, "05-script-console", [(("css", ".CodeMirror, textarea[name=script]"), 7, "left"), (("css", "pre"), 8, "left")], full=False)
    print("kontrol script console:", page.locator("pre").last.inner_text()[:600])


def b07_console(page):
    lab = "b07"; d = os.path.join(ROOT, LAB_DIRS[lab])
    login_b(page)
    page.goto(BASE + "/manage/script", wait_until="domcontentloaded"); settle(page, 2)
    code = open(os.path.join(d, "scripts", "system-info.groovy"), encoding="utf-8").read()
    page.locator(".CodeMirror").first.click(); time.sleep(0.5)
    page.keyboard.press("Control+A"); page.keyboard.insert_text(code); time.sleep(1)
    shoot(page, lab, "05-script-console", [(("css", ".CodeMirror"), 7, "left"), (("css", 'button[name="Submit"]'), 8, "up")])
    page.locator('button[name="Submit"]').first.click(); settle(page, 3)
    res = page.locator('pre:has-text("JENKINS SISTEM BILGILERI")').last
    res.scroll_into_view_if_needed(); time.sleep(0.5)
    shoot(page, lab, "06-script-result", [(("css", 'pre:has-text("JENKINS SISTEM BILGILERI")'), 9, "left")])
    print("kontrol sonuc:\n" + res.inner_text()[:700])


def b07_clean(page):
    lab = "b07"; d = os.path.join(ROOT, LAB_DIRS[lab]); job = "shared-library-demo"
    login_b(page)
    ui_build_now(page, job); ui_build_now(page, job)
    before = api(f'curl -s -u "admin:$P" "$J/job/{job}/api/json?tree=builds%5Bnumber%5D"\n')
    others = api('curl -s -u "admin:$P" "$J/job/progressive-learning/api/json?tree=builds%5Bnumber%5D"\n')
    page.goto(BASE + "/manage/script", wait_until="domcontentloaded"); settle(page, 2)
    page.locator(".CodeMirror").first.click(); time.sleep(0.5)
    page.keyboard.press("Control+A"); page.keyboard.insert_text(open(os.path.join(d, "scripts", "clean-build-history.groovy"), encoding="utf-8").read()); time.sleep(1)
    page.locator('button[name="Submit"]').first.click(); settle(page, 3)
    res = page.locator('pre:has-text("build var")').last
    res.scroll_into_view_if_needed(); time.sleep(0.5)
    shoot(page, lab, "07-clean-result", [(("css", 'pre:has-text("build var")'), 10, "left")])
    print("once:", before); print("sonuc:\n" + res.inner_text())
    print("sonra:", api(f'curl -s -u "admin:$P" "$J/job/{job}/api/json?tree=builds%5Bnumber%5D"\n'))
    print("diger job degismedi:", others == api('curl -s -u "admin:$P" "$J/job/progressive-learning/api/json?tree=builds%5Bnumber%5D"\n'))


ARGOCD = os.environ.get("JK_ARGOCD", "https://34.179.157.236:30087")


def argocd_login(page, pw):
    page.goto(ARGOCD + "/login", wait_until="domcontentloaded"); settle(page, 3)
    if page.locator('input[name="username"]').count():
        page.fill('input[name="username"]', "admin"); page.fill('input[name="password"]', pw)
        return True
    return False


def b06_run(page):
    lab = "b06"; job = "argocd-gitops-pipeline"
    pw = remote("kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d")
    argocd_login(page, pw)
    shoot(page, lab, "01-argocd-login", [
        (("union", ("css", 'input[name="username"]'), ("css", 'input[name="password"]')), 1, "left"),
        (("css", 'button:has-text("Sign In"), button:has-text("SIGN IN")'), 2, "left")])
    page.locator('button:has-text("Sign In"), button:has-text("SIGN IN")').first.click(); settle(page, 5)
    page.goto(ARGOCD + "/applications", wait_until="domcontentloaded"); settle(page, 4)
    shoot(page, lab, "02-app-outofsync", [(("text", "devops-app", True), 3, "left")])
    login_b(page)
    delete_job(job)
    ui_credential(page, "Username with password", {'input[name="_.username"]': "admin", 'input[name="_.password"]': pw,
                                                   'input[name="_.id"]': "argocd-admin"},
                  shot=(lab, "03-jenkins-credential", [
                      (("css", 'input[name="_.username"]'), 4, "left"), (("css", 'input[name="_.password"]'), 5, "left"),
                      (("css", 'input[name="_.id"]'), 6, "left"), (("role", "button", "Create"), 7, "down")]))
    ui_new_pipeline_scm(page, job, "bonus-labs/06-argocd-gitops-sync/Jenkinsfile")
    n = ui_build_now(page, job); t = console_text(job, n)
    print("kontrol ilk (nginx:alpine)", n, build_result(job, n))
    print("\n".join(l.split("] ", 1)[-1] for l in t.splitlines() if "Durum:" in l or "Synced" in l or "Image ayari" in l or "ERROR" in l or "acilamadi" in l))
    img = os.environ.get("JK_APP_IMAGE", "hbayraktar/devops-app-public:v2-db5fc93")
    n = ui_build_with_params(page, job, {"APP_IMAGE": img}, shot=(lab, "04-build-with-parameters", [
        (("css", 'xpath=//input[@name="name" and @value="APP_IMAGE"]/following::*[@name="value"][1]'), 8, "left"),
        (("css", "button.jenkins-button--primary"), 9, "up")]))
    t = console_text(job, n)
    print("kontrol image", n, build_result(job, n))
    print("\n".join(l.split("] ", 1)[-1] for l in t.splitlines() if "Durum:" in l or "Synced ve" in l or "Image ayari" in l or "Sync bas" in l))
    page.goto(BASE + f"/job/{job}/{n}/console", wait_until="domcontentloaded"); settle(page, 2)
    shoot(page, lab, "05-console", [(("text", "Uygulama Synced ve Healthy"), 10, "left")])
    argocd_login(page, pw)
    if page.locator('input[name="username"]').count():
        page.locator('button:has-text("Sign In"), button:has-text("SIGN IN")').first.click(); settle(page, 5)
    page.goto(ARGOCD + "/applications/argocd/devops-app", wait_until="domcontentloaded"); settle(page, 6)
    shoot(page, lab, "06-app-synced", [(("text", "Healthy"), 11, "down"), (("text", "Synced"), 12, "down")])


FLOWS = {"lab01a-wizard": lab01a_wizard, "lab01a-tour": lab01a_tour, "lab01a-plugin-install": lab01a_plugin_install, "lab01a-plugin-uninstall": lab01a_plugin_uninstall, "lab01a-restart": lab01a_restart, "lab01a-pipeline": lab01a_pipeline, "lab01a-rebuild-link": lab01a_rebuild_link, "lab01a-console": lab01a_console, "lab01b": lab01b, "lab02": lab02, "lab02a-credential": lab02a_credential, "lab02a-build": lab02a_build, "lab03": lab03, "lab04": lab04, "lab04-results": lab04_results, "lab06": lab06, "lab05": lab05, "lab05-tail": lab05_jenkins_tail, "lab05-token": lab05_token, "lab07": lab07, "lab01b-jobs": lab01b_jobs, "lab02-run": lab02_run, "lab02a-run": lab02a_run, "lab03-run": lab03_run, "lab04-run": lab04_run, "lab05-run": lab05_run, "lab06-run": lab06_run, "lab07-run": lab07_run, "b01-run": b01_run, "b01-prod": b01_prod, "b02-run": b02_run, "b02-node": b02_node, "b03-run": b03_run, "b04-run": b04_run, "b05-plugin": b05_plugin, "b05-job": b05_job, "b05-after": b05_after, "b07-run": b07_run, "b07-console": b07_console, "b07-clean": b07_clean, "b06-run": b06_run}

if __name__ == "__main__":
    names = sys.argv[1:] or list(FLOWS)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        ctx = browser.new_context(viewport={"width": 1400, "height": 860}, device_scale_factor=SCALE, locale="en-US", ignore_https_errors=True)
        page = ctx.new_page()
        for n in names:
            FLOWS[n](page)
        browser.close()
