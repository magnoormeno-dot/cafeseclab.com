# CafeSec Lab Home

This repository hosts the public root site for CafeSec Lab:

<https://cafeseclab.com/>

The main research repository remains:

<https://github.com/magnoormeno-dot/netcafe-security-lab>

The long-form research site remains:

<https://research.cafeseclab.com/>

## Maintenance

This site is intentionally small. It should provide a stable public entry point,
not duplicate the research blog or project documentation.

Before changing it, confirm:

- links still point to the active research repository and research site;
- role-based contact addresses remain current;
- the wording does not imply vendor, platform, or field certification;
- defensive-only boundaries are visible on the first page.

Most of this checklist is enforced automatically:

```sh
python3 scripts/site_check.py
```

The same script runs in CI (`.github/workflows/site-checks.yml`) on every
pull request and push to `main`. It also verifies that referenced assets
exist, that `.well-known/security.txt` is more than 30 days from expiry,
and that the sitemap, robots.txt, and CNAME are intact.

