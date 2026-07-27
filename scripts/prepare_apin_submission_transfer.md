# APIN submission — repo transfer checklist

**Date:** 27 July 2026  
**Target repo:** https://github.com/edu-risk-lab/leakage-controlled-kt-audit

## 1. Transfer on GitHub (browser — required once)

1. Open https://github.com/tuanymc/p0_project → **Settings**
2. **Danger Zone** → **Transfer ownership**
3. New owner: **edu-risk-lab**
4. New repository name: **leakage-controlled-kt-audit**
5. Confirm transfer

## 2. Local git (after transfer succeeds)

```powershell
cd "d:\0. NCS\CODE\p0_project"
git remote set-url origin https://github.com/edu-risk-lab/leakage-controlled-kt-audit.git
git push -u origin main
git tag -a apin-submission-20260727 -m "APIN submission snapshot"
git push origin apin-submission-20260727
```

## 3. EM upload files

| File | Path |
|------|------|
| Manuscript PDF | `paper/submission_APIN/DaoMinh_2026_LeakageControlledKT_APIN.pdf` |
| Cover letter | Export `paper/cover_letter_APIN.md` → Word/PDF or paste into EM |

**EM metadata**

- Corresponding author: **Van-Hau Nguyen** / **nvhau66@gmail.com**
- Submitter (cover letter): **Tuan Dao Minh**

## 4. Verify before upload

- [ ] `https://github.com/edu-risk-lab/leakage-controlled-kt-audit` loads in browser
- [ ] PDF Data/Code availability shows new URL
- [ ] Title page email: nvhau66@gmail.com
