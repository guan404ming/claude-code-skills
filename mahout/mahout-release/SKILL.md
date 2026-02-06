---
name: mahout-release
description: Guide the Apache Mahout release process.
---

# Mahout Release

## Usage
```
/mahout-release <qumat_version> <qdp_version>
```

Example: `/mahout-release 0.5.0 0.1.0`

## Instructions

Refer to `dev/release.md` for full details. **Stop after each phase and confirm with user before proceeding.**

### Phase 1: RC Preparation

1. **Create stable branch** from main (e.g., `v0.5-stable`)
2. **Update versions** to RC suffix:
   - `pyproject.toml` → `version = "<qumat_version>rc1"`
   - `qdp/Cargo.toml` → `version = "<qdp_version>-rc1"`
3. **Build:**
   ```bash
   uv build
   cd qdp/qdp-python
   uv tool run maturin build --release --interpreter python3.10
   uv tool run maturin build --release --interpreter python3.11
   uv tool run maturin build --release --interpreter python3.12
   ```
4. **Sign and hash** artifacts (GPG + SHA-512)
5. **Upload to TestPyPI** first, verify install works
6. **Upload to PyPI** after TestPyPI is confirmed
7. **Open testing issue:** `./dev/generate-rc-issue.sh <qumat_ver>rc1 <qdp_ver>rc1 "Qumat <qumat_ver>"`
8. **Send RC email** using template in `dev/rc-email-template.md`

**Stop and confirm with user before Phase 2.**

### Phase 2: Vote

1. Submit source artifacts to ATR
2. Send vote email using template in `dev/rc-email-template.md`
3. Wait 72 hours for 3 binding +1 votes

**Stop and confirm with user before Phase 3.**

### Phase 3: Final Publication

1. Promote release in ATR
2. **Publish final version to TestPyPI**, verify, then **publish to PyPI**
3. Tag release: `git tag -a v<qumat_version> -m "Release <qumat_version>"`
4. Bump version on `main` to next dev (e.g., `0.6.0`)
5. Create versioned docs: `cd website && npm run version <qumat_version>`
6. Announce on `dev@mahout.apache.org`
