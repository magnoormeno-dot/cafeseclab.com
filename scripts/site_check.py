#!/usr/bin/env python3
"""Pre-publish checks for cafeseclab.com.

Automates the maintenance checklist in README.md:
- links still point to the active research repository and research site;
- role-based contact addresses remain current;
- the wording does not imply vendor, platform, or field certification;
- defensive-only boundaries are visible on the first page.

Plus structural checks: referenced local assets exist, security.txt has not
expired, sitemap is well-formed, robots/CNAME are intact.

Stdlib only. Exit code 0 = all checks pass.
"""

import re
import sys
import xml.dom.minidom
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    mark = "ok  " if ok else "FAIL"
    suffix = f" — {detail}" if detail and not ok else ""
    print(f"{mark} {name}{suffix}")
    if not ok:
        FAILURES.append(name)


index = (ROOT / "index.html").read_text(encoding="utf-8")
security = (ROOT / ".well-known" / "security.txt").read_text(encoding="utf-8")
robots = (ROOT / "robots.txt").read_text(encoding="utf-8")

# Links still point to the active research repository and research site.
check("link: research site", "https://research.cafeseclab.com/" in index)
check(
    "link: research repository",
    "https://github.com/magnoormeno-dot/netcafe-security-lab" in index,
)

# Role-based contact addresses remain current.
for addr in (
    "contact@cafeseclab.com",
    "research@cafeseclab.com",
    "security@cafeseclab.com",
):
    check(f"contact: {addr}", addr in index)
check("contact: security@ in security.txt", "security@cafeseclab.com" in security)

# Wording must not imply vendor, platform, or field certification.
banned = re.findall(r"certif\w*|accredit\w*|guarantee\w*", index, re.I)
check("wording: no certification claims", not banned, f"found {sorted(set(banned))}")

# Defensive-only boundary visible on the first page.
check("boundary: defensive-only notice", "Defensive-only boundary" in index)

# Page metadata.
check(
    "meta: canonical",
    '<link rel="canonical" href="https://cafeseclab.com/">' in index,
)
check("meta: og:image", 'property="og:image"' in index)
check("meta: content security policy", "Content-Security-Policy" in index)

# Every root-relative asset referenced by the page must exist in the repo.
for asset in sorted(set(re.findall(r'(?:src|href)="/([^"]+)"', index))):
    check(f"asset: /{asset}", (ROOT / asset).is_file())
check("asset: 404.html", (ROOT / "404.html").is_file())

# security.txt must not be expired or close to expiry (RFC 9116).
m = re.search(r"^Expires:\s*(\S+)", security, re.M)
check("security.txt: Expires present", bool(m))
if m:
    expires = datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
    check(
        "security.txt: >30 days before expiry",
        expires > datetime.now(timezone.utc) + timedelta(days=30),
        f"expires {expires:%Y-%m-%d}",
    )

# Sitemap, robots, custom domain.
try:
    xml.dom.minidom.parse(str(ROOT / "sitemap.xml"))
    check("sitemap.xml: well-formed", True)
except Exception as exc:  # noqa: BLE001 - report any parse failure
    check("sitemap.xml: well-formed", False, str(exc))
check(
    "robots.txt: references site sitemap",
    "https://cafeseclab.com/sitemap.xml" in robots,
)
check("CNAME: cafeseclab.com", (ROOT / "CNAME").read_text().strip() == "cafeseclab.com")

if FAILURES:
    print(f"\n{len(FAILURES)} check(s) failed.")
    sys.exit(1)
print("\nAll checks passed.")
